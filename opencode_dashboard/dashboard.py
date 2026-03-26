"""opencode-dashboard - TUI dashboard for monitoring opencode pipelines."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from humanize import naturaldelta
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import DataTable, Footer, Header, Static


@dataclass
class IssueState:
    """State for a single issue."""

    number: int
    state: str
    last_updated: int
    last_model: str | None = None
    is_locked: bool = False
    fail_ts: int | None = None

    @property
    def age_seconds(self) -> int:
        """Get age in seconds."""
        return int(datetime.now(UTC).timestamp()) - self.last_updated

    @property
    def backoff_remaining(self) -> int | None:
        """Get backoff remaining in seconds."""
        if self.fail_ts is None:
            return None
        elapsed = int(datetime.now(UTC).timestamp()) - self.fail_ts
        backoff = 15 * (2**0)
        remaining = backoff - elapsed
        return max(0, remaining)


@dataclass
class WorkerInfo:
    """Information about a worker process."""

    role: str
    count: int = 0


@dataclass
class ModelHealth:
    """Health information for a model."""

    name: str
    fail_count: int
    last_fail_ts: int

    @property
    def backoff_remaining(self) -> int:
        """Get backoff remaining in seconds."""
        elapsed = int(datetime.now(UTC).timestamp()) - self.last_fail_ts
        backoff = 15 * (2 ** (self.fail_count - 1))
        remaining = backoff - elapsed
        return max(0, remaining)


@dataclass
class TimesheetEntry:
    """Entry from timesheet.jsonl."""

    ts: str
    issue: int
    role: str
    model: str
    duration_s: int
    outcome: str


class TimesheetReader:
    """Efficient reader for timesheet.jsonl that only reads last N entries."""

    def __init__(self, timesheet_path: Path) -> None:
        """Initialize reader.

        Args:
            timesheet_path: Path to timesheet.jsonl file
        """
        self.timesheet_path = timesheet_path

    def read_last_n(self, n: int) -> list[TimesheetEntry]:
        """Read last N entries by reading file and taking last N lines.

        Args:
            n: Number of entries to read

        Returns:
            List of timesheet entries (most recent last)
        """
        entries: list[TimesheetEntry] = []

        if not self.timesheet_path.exists():
            return entries

        try:
            # Read all lines and take last N
            with self.timesheet_path.open("r") as f:
                lines = f.readlines()

            # Take last N lines
            last_n_lines = lines[-n:] if len(lines) > n else lines

            # Parse each line
            for line in last_n_lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entry = TimesheetEntry(
                        ts=data.get("ts", ""),
                        issue=data.get("issue", 0),
                        role=data.get("role", ""),
                        model=data.get("model", ""),
                        duration_s=data.get("duration_s", 0),
                        outcome=data.get("outcome", ""),
                    )
                    entries.append(entry)
                except (json.JSONDecodeError, KeyError):
                    continue

        except (OSError, json.JSONDecodeError):
            pass

        return entries


@dataclass
class PRInfo:
    """Information about a PR."""

    number: int
    title: str
    issue_number: int | None = None
    ci_status: str | None = None


class PipelineMonitor:
    """Monitors pipeline state from filesystem."""

    def __init__(self, repo_path: Path) -> None:
        """Initialize monitor.

        Args:
            repo_path: Path to repository root
        """
        self.repo_path = repo_path
        self.logs_dir = repo_path / ".opencode_logs"

    def read_file(self, path: Path, default: str = "") -> str:
        """Read file content.

        Args:
            path: Path to file
            default: Default value if file doesn't exist

        Returns:
            File content or default
        """
        try:
            return path.read_text().strip()
        except (FileNotFoundError, OSError):
            return default

    def get_issues(self) -> dict[int, IssueState]:
        """Get all issue states.

        Returns:
            Dict mapping issue number to state
        """
        issues: dict[int, IssueState] = {}

        for issue_dir in self.logs_dir.glob("issue_*"):
            if not issue_dir.is_dir():
                continue

            try:
                issue_num = int(issue_dir.name.split("_")[1])
            except (ValueError, IndexError):
                continue

            state = self.read_file(issue_dir / "state", "pending")
            last_updated_str = self.read_file(issue_dir / "last_updated")
            last_model = self.read_file(issue_dir / "last_model") or None
            fail_ts_str = self.read_file(issue_dir / ".fail_ts") or None

            try:
                last_updated = int(last_updated_str) if last_updated_str else 0
            except ValueError:
                last_updated = 0

            try:
                fail_ts = int(fail_ts_str) if fail_ts_str else None
            except ValueError:
                fail_ts = None

            is_locked = (issue_dir / "lock" / "pid").exists()

            issues[issue_num] = IssueState(
                number=issue_num,
                state=state,
                last_updated=last_updated,
                last_model=last_model,
                is_locked=is_locked,
                fail_ts=fail_ts,
            )

        return issues

    def get_workers(self) -> list[WorkerInfo]:
        """Get worker process information.

        Returns:
            List of worker info
        """
        workers: dict[str, int] = {}

        import subprocess

        try:
            result = subprocess.run(
                ["pgrep", "-fa", "opencode_pipeline"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if "opencode_pipeline.sh" in line:
                        match = re.search(r"opencode_pipeline\.sh\s+(\w+)", line)
                        if match:
                            role = match.group(1)
                            workers[role] = workers.get(role, 0) + 1
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return [WorkerInfo(role=role, count=count) for role, count in workers.items()]

    def get_model_health(self) -> list[ModelHealth]:
        """Get model health information.

        Returns:
            List of model health info
        """
        models: list[ModelHealth] = []
        backoff_dir = self.logs_dir / ".model_backoff"

        if not backoff_dir.exists():
            return models

        for model_file in backoff_dir.iterdir():
            if not model_file.is_file():
                continue

            model_name = model_file.name.replace("_", "/")
            lines = model_file.read_text().strip().split("\n")

            try:
                fail_count = int(lines[0]) if len(lines) > 0 else 0
                last_fail_ts = int(lines[1]) if len(lines) > 1 else 0
            except (ValueError, IndexError):
                continue

            models.append(
                ModelHealth(
                    name=model_name,
                    fail_count=fail_count,
                    last_fail_ts=last_fail_ts,
                )
            )

        return sorted(models, key=lambda m: m.backoff_remaining, reverse=True)

    def get_timesheet_entries(self, limit: int = 8) -> list[TimesheetEntry]:
        """Get recent timesheet entries using efficient reader.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of timesheet entries
        """
        timesheet_path = self.logs_dir / "timesheet.jsonl"
        reader = TimesheetReader(timesheet_path)
        return reader.read_last_n(limit)

    def get_prs(self) -> list[PRInfo]:
        """Get open PRs with CI status.

        Returns:
            List of PR info
        """
        prs: list[PRInfo] = []

        import subprocess

        try:
            result = subprocess.run(
                [
                    "gh",
                    "pr",
                    "list",
                    "--state",
                    "open",
                    "--json",
                    "number,title,statusCheckRollup",
                ],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.repo_path,
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                for pr in data:
                    issue_number = None
                    try:
                        view_result = subprocess.run(
                            ["gh", "pr", "view", str(pr["number"]), "--json", "body"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                            cwd=self.repo_path,
                        )
                        if view_result.returncode == 0:
                            body_data = json.loads(view_result.stdout)
                            body = body_data.get("body", "")
                            match = re.search(r"#(\d+)", body)
                            if match:
                                issue_number = int(match.group(1))
                    except (subprocess.TimeoutExpired, json.JSONDecodeError, ValueError):
                        pass

                    ci_status = None
                    status_rollup = pr.get("statusCheckRollup", [])
                    if status_rollup:
                        if any(
                            s.get("status") == "COMPLETED" and s.get("conclusion") == "FAILURE"
                            for s in status_rollup
                        ):
                            ci_status = "failing"
                        elif any(
                            s.get("status") in ["IN_PROGRESS", "PENDING", "QUEUED"]
                            for s in status_rollup
                        ):
                            ci_status = "pending"
                        elif all(
                            s.get("status") == "COMPLETED" and s.get("conclusion") == "SUCCESS"
                            for s in status_rollup
                        ):
                            ci_status = "passing"

                    prs.append(
                        PRInfo(
                            number=pr["number"],
                            title=pr["title"],
                            issue_number=issue_number,
                            ci_status=ci_status,
                        )
                    )
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass

        return prs

    def tail_log(self, issue_num: int, log_type: str, lines: int = 50) -> str:
        """Tail a log file for an issue.

        Args:
            issue_num: Issue number
            log_type: Type of log (implement, review, fix, ci_check, pr)
            lines: Number of lines to return

        Returns:
            Log content
        """
        log_name = f"{log_type}.log"
        log_path = self.logs_dir / f"issue_{issue_num}" / log_name

        if not log_path.exists():
            return f"[No {log_name} yet]"

        try:
            all_lines = log_path.read_text().split("\n")
            return "\n".join(all_lines[-lines:])
        except OSError:
            return f"[Error reading {log_name}]"


class WorkersPanel(Static):
    """Panel showing worker processes."""

    def __init__(self, monitor: PipelineMonitor) -> None:
        """Initialize workers panel.

        Args:
            monitor: Pipeline monitor instance
        """
        super().__init__()
        self.monitor = monitor

    def update_content(self) -> None:
        """Refresh panel content."""
        workers = self.monitor.get_workers()

        lines = ["WORKERS", ""]
        total = 0

        for worker in workers:
            lines.append(f"{worker.role}×{worker.count}")
            total += worker.count

        lines.append("")
        lines.append(f"{total} opencode")
        lines.append(" runs live")

        self.update("\n".join(lines))


class IssuesTable(DataTable):
    """Table showing issues."""

    def __init__(self, monitor: PipelineMonitor, pr_info: dict[int, PRInfo]) -> None:
        """Initialize issues table.

        Args:
            monitor: Pipeline monitor instance
            pr_info: Dict mapping issue number to PR info
        """
        super().__init__()
        self.monitor = monitor
        self.pr_info = pr_info
        self.cursor_type = "row"
        self.zebra_stripes = True

    def on_mount(self) -> None:
        """Set up table columns."""
        self.add_column("Issue", width=8)
        self.add_column("State", width=14)
        self.add_column("Model", width=20)
        self.add_column("Age", width=8)
        self.add_column("Status", width=10)

    def update_content(self) -> None:
        """Refresh table data."""
        self.clear()

        issues = self.monitor.get_issues()
        sorted_issues = sorted(
            issues.values(),
            key=lambda i: i.last_updated,
            reverse=True,
        )

        for issue in sorted_issues:
            age_str = naturaldelta(issue.age_seconds) if issue.age_seconds > 0 else "0s"
            if issue.age_seconds < 60:
                age_str = f"{issue.age_seconds}s"

            model_str = issue.last_model or "—"

            status_parts = []
            if issue.is_locked:
                status_parts.append("[lock]")
            if issue.backoff_remaining and issue.backoff_remaining > 0:
                status_parts.append(f"backoff {issue.backoff_remaining}s")

            if issue.number in self.pr_info:
                pr = self.pr_info[issue.number]
                if pr.ci_status == "failing":
                    status_parts.append("[CI failing]")
                elif pr.ci_status == "pending":
                    status_parts.append("[CI pending]")
                elif pr.ci_status == "passing":
                    status_parts.append("[CI OK]")

            status_str = " ".join(status_parts) if status_parts else ""

            self.add_row(
                f"#{issue.number}",
                issue.state,
                model_str,
                age_str,
                status_str,
                key=str(issue.number),
            )

        pending = sum(1 for i in issues.values() if i.state == "pending")
        in_progress = sum(1 for i in issues.values() if i.state not in ["pending", "done"])
        done = sum(1 for i in issues.values() if i.state == "done")

        self.border_subtitle = f"done: {done}  pending: {pending}  in_progress: {in_progress}"


class LogViewer(Static):
    """Viewer for issue logs."""

    def __init__(self, monitor: PipelineMonitor) -> None:
        """Initialize log viewer.

        Args:
            monitor: Pipeline monitor instance
        """
        super().__init__()
        self.monitor = monitor
        self.current_issue: int | None = None
        self.current_log = "implement"
        self.log_types = ["implement", "review", "fix", "ci_check", "pr"]

    def set_issue(self, issue_num: int | None) -> None:
        """Set the current issue to view.

        Args:
            issue_num: Issue number or None
        """
        self.current_issue = issue_num
        self.update_content()

    def cycle_log(self) -> None:
        """Cycle to next log type."""
        if self.current_issue is None:
            return

        issue = self.monitor.get_issues().get(self.current_issue)
        if issue is None:
            return

        idx = self.log_types.index(self.current_log)
        self.current_log = self.log_types[(idx + 1) % len(self.log_types)]
        self.update_content()

    def update_content(self) -> None:
        """Refresh log content."""
        if self.current_issue is None:
            self._show_recent_logs()
            return

        issue = self.monitor.get_issues().get(self.current_issue)
        if issue is None:
            self._show_recent_logs()
            return

        state_to_log = {
            "implementing": "implement",
            "reviewing": "review",
            "fixing": "fix",
            "ci_checking": "ci_check",
            "pr_open": "pr",
            "pr_opened": "pr",
        }
        if issue.state in state_to_log:
            self.current_log = state_to_log[issue.state]

        self.border_title = (
            f"SELECTED ISSUE LOG   (#{self.current_issue} {self.current_log}.log — live tail)"
        )
        content = self.monitor.tail_log(self.current_issue, self.current_log)
        self.update(content)

    def _show_recent_logs(self) -> None:
        """Show recent log entries across all issues."""
        self.border_title = "RECENT LOGS   (select an issue to view its logs)"
        self.update(self._get_recent_logs())

    def _get_recent_logs(self, lines: int = 50) -> str:
        """Get recent log entries from all worker logs.

        Args:
            lines: Number of lines to return

        Returns:
            Recent log content
        """
        import subprocess

        log_lines: list[str] = []

        try:
            worker_logs = list(self.monitor.logs_dir.glob("worker_*.log"))

            for log_file in worker_logs[-5:]:
                try:
                    result = subprocess.run(
                        ["tail", "-n", "10", str(log_file)],
                        capture_output=True,
                        text=True,
                        timeout=1,
                    )
                    if result.returncode == 0:
                        log_lines.append(f"=== {log_file.name} ===")
                        log_lines.append(result.stdout)
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
        except OSError:
            pass

        if not log_lines:
            return "[No recent logs yet - select an issue to view its logs]"

        all_lines = "\n".join(log_lines).split("\n")
        return "\n".join(all_lines[-lines:])

    def _show_recent_logs(self) -> None:
        """Show recent log entries across all issues."""
        self.border_title = "RECENT LOGS   (select an issue to view its logs)"
        self.update(self._get_recent_logs())

    def _get_recent_logs(self, lines: int = 50) -> str:
        """Get recent log entries from all worker logs.

        Args:
            lines: Number of lines to return

        Returns:
            Recent log content
        """
        import subprocess

        log_lines: list[str] = []

        try:
            # Get all worker log files
            worker_logs = list(self.monitor.logs_dir.glob("worker_*.log"))

            for log_file in worker_logs[-5:]:  # Last 5 worker logs
                try:
                    # Get last 10 lines from each log
                    result = subprocess.run(
                        ["tail", "-n", "10", str(log_file)],
                        capture_output=True,
                        text=True,
                        timeout=1,
                    )
                    if result.returncode == 0:
                        log_lines.append(f"=== {log_file.name} ===")
                        log_lines.append(result.stdout)
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
        except OSError:
            pass

        if not log_lines:
            return "[No recent logs yet - select an issue to view its logs]"

        # Take last N lines total
        all_lines = "\n".join(log_lines).split("\n")
        return "\n".join(all_lines[-lines:])


class ModelHealthTable(DataTable):
    """Table showing model health."""

    def __init__(self, monitor: PipelineMonitor) -> None:
        """Initialize model health table.

        Args:
            monitor: Pipeline monitor instance
        """
        super().__init__()
        self.monitor = monitor
        self.cursor_type = "row"
        self.zebra_stripes = True

    def on_mount(self) -> None:
        """Set up table columns."""
        self.add_column("Model", width=35)
        self.add_column("Fails", width=8)
        self.add_column("Backoff", width=25)

    def update_content(self) -> None:
        """Refresh table data."""
        self.clear()

        models = self.monitor.get_model_health()[:10]

        for model in models:
            fail_str = f"{model.fail_count}"

            if model.backoff_remaining > 0:
                backoff_str = f"{naturaldelta(model.backoff_remaining)} remaining"
            else:
                backoff_str = "expired — available"

            self.add_row(model.name, fail_str, backoff_str)


class TimesheetTable(DataTable):
    """Table showing recent timesheet entries."""

    def __init__(self, monitor: PipelineMonitor) -> None:
        """Initialize timesheet table.

        Args:
            monitor: Pipeline monitor instance
        """
        super().__init__()
        self.monitor = monitor
        self.cursor_type = "row"
        self.zebra_stripes = True

    def on_mount(self) -> None:
        """Set up table columns."""
        self.add_column("Time", width=8)
        self.add_column("Issue", width=8)
        self.add_column("Role", width=12)
        self.add_column("Model", width=15)
        self.add_column("Duration", width=10)
        self.add_column("Outcome", width=12)

    def update_content(self) -> None:
        """Refresh table data."""
        self.clear()

        entries = self.monitor.get_timesheet_entries()

        for entry in reversed(entries):
            try:
                dt = datetime.fromisoformat(entry.ts.replace("Z", "+00:00"))
                time_str = dt.strftime("%H:%M")
            except ValueError:
                time_str = entry.ts[:5]

            issue_str = f"#{entry.issue}"
            duration_str = f"{entry.duration_s}s"

            outcome_symbol = "✓" if entry.outcome == "success" else "✗"
            outcome_str = f"{outcome_symbol} {entry.outcome}"

            self.add_row(
                time_str,
                issue_str,
                entry.role,
                entry.model[:15],
                duration_str,
                outcome_str,
            )


class DashboardApp(App):
    """Main dashboard application."""

    CSS = """
    Screen {
        layout: vertical;
    }

    #header {
        height: 3;
    }

    #main {
        height: 1fr;
    }

    #top {
        height: 2fr;
    }

    #workers {
        width: 25;
        padding: 1;
    }

    #issues {
        height: 1fr;
    }

    #log {
        height: 3fr;
    }

    #bottom {
        height: 1fr;
    }

    #model-health {
        width: 1fr;
    }

    #timesheet {
        width: 1fr;
    }

    DataTable {
        border: solid $primary;
        border_subtitle_align: center;
    }

    Static {
        border: solid $primary;
        padding: 1;
    }
    """

    def __init__(self, repo_path: Path) -> None:
        """Initialize dashboard.

        Args:
            repo_path: Path to repository root
        """
        super().__init__()
        self.repo_path = repo_path
        self.monitor = PipelineMonitor(repo_path)
        self.pr_info: dict[int, PRInfo] = {}
        self.title = f"🔧 opencode pipeline  [repo: {repo_path.name}]       [q]uit"

    def compose(self) -> ComposeResult:
        """Compose dashboard UI."""
        yield Header()

        with Container(id="main"):
            with Horizontal(id="top"):
                with Vertical():
                    workers_panel = WorkersPanel(self.monitor)
                    workers_panel.id = "workers"
                    yield workers_panel
                with Vertical():
                    issues_table = IssuesTable(self.monitor, self.pr_info)
                    issues_table.id = "issues"
                    yield issues_table

            log_viewer = LogViewer(self.monitor)
            log_viewer.id = "log"
            yield log_viewer

            with Horizontal(id="bottom"):
                with Container():
                    yield Static("MODEL HEALTH", id="model-health-title")
                    model_health_table = ModelHealthTable(self.monitor)
                    model_health_table.id = "model-health-table"
                    yield model_health_table
                with Container():
                    yield Static("RECENT TIMESHEET  last 8 entries", id="timesheet-title")
                    timesheet_table = TimesheetTable(self.monitor)
                    timesheet_table.id = "timesheet-table"
                    yield timesheet_table

        yield Footer()

    def on_mount(self) -> None:
        """Set up refresh timers."""
        self.set_interval(2, self.refresh_local)
        self.set_interval(30, self.refresh_github)
        # Don't load data on mount - let UI render immediately
        # Data will load on first timer tick (2s for local, 30s for GitHub)

    def refresh_local(self) -> None:
        """Refresh local state (issues, workers, models, timesheet)."""
        workers = self.query_one("#workers", WorkersPanel)
        workers.update_content()

        issues = self.query_one("#issues", IssuesTable)
        issues.pr_info = self.pr_info
        issues.update_content()

        log_viewer = self.query_one("#log", LogViewer)
        log_viewer.update_content()

        model_health = self.query_one("#model-health-table", ModelHealthTable)
        model_health.update_content()

        timesheet = self.query_one("#timesheet-table", TimesheetTable)
        timesheet.update_content()

    def refresh_github(self) -> None:
        """Refresh GitHub state (PRs)."""
        prs = self.monitor.get_prs()
        self.pr_info = {pr.issue_number: pr for pr in prs if pr.issue_number}

        issues = self.query_one("#issues", IssuesTable)
        issues.pr_info = self.pr_info
        issues.update_content()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in issues table.

        Args:
            event: Row selected event
        """
        if event.data_table.id == "issues":
            issue_key = event.row_key
            if issue_key and issue_key.value:
                issue_num = int(issue_key.value)
                log_viewer = self.query_one("#log", LogViewer)
                log_viewer.set_issue(issue_num)

    def on_key(self, event) -> None:
        """Handle key press.

        Args:
            event: Key event
        """
        if event.key == "q":
            self.exit()
        elif event.key == "r":
            self.refresh_local()
            self.refresh_github()
        elif event.key == "l":
            log_viewer = self.query_one("#log", LogViewer)
            log_viewer.cycle_log()
        elif event.key == "g":
            issues = self.query_one("#issues", IssuesTable)
            if issues.cursor_row:
                issue_num = int(str(issues.cursor_row))
                self.open_issue_in_browser(issue_num)
        elif event.key == "p":
            issues = self.query_one("#issues", IssuesTable)
            if issues.cursor_row:
                issue_num = int(str(issues.cursor_row))
                self.open_pr_in_browser(issue_num)
        elif event.key == "k":
            self.show_model_backoff_modal()

    def open_issue_in_browser(self, issue_num: int) -> None:
        """Open issue in browser.

        Args:
            issue_num: Issue number
        """
        import subprocess

        try:
            subprocess.run(
                ["gh", "issue", "view", str(issue_num), "--web"],
                check=False,
                timeout=5,
                cwd=self.repo_path,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    def open_pr_in_browser(self, issue_num: int) -> None:
        """Open PR in browser.

        Args:
            issue_num: Issue number
        """
        import subprocess

        if issue_num not in self.pr_info:
            return

        pr = self.pr_info[issue_num]

        try:
            subprocess.run(
                ["gh", "pr", "view", str(pr.number), "--web"],
                check=False,
                timeout=5,
                cwd=self.repo_path,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    def show_model_backoff_modal(self) -> None:
        """Show full model backoff table in modal."""
        models = self.monitor.get_model_health()
        print("\n=== MODEL BACKOFF ===")
        for model in models:
            print(
                f"{model.name}: {model.fail_count} fails, {model.backoff_remaining}s backoff remaining"
            )


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Monitor opencode pipeline")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Path to repository root")
    args = parser.parse_args()

    app = DashboardApp(args.repo)
    app.run()
