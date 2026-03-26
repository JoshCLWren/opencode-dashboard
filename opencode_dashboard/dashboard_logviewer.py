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
