# opencode-dashboard

TUI dashboard for monitoring opencode pipelines.

[![CI Status](https://github.com/JoshCLWren/opencode-dashboard/workflows/CI/badge.svg)](https://github.com/JoshCLWren/opencode-dashboard/actions)

## Features

- **Live monitoring** of issue state machine (pending → implementing → reviewing → done)
- **Worker process tracking** via pgrep
- **Model health monitoring** with backoff tracking
- **CI status integration** via GitHub CLI
- **Timesheet tracking** showing recent work
- **Real-time log tailing** for selected issues
- **Auto-refresh** every 2s (local) and 30s (GitHub)

## Quick Start

```bash
# Install dependencies
uv sync --group dev

# Activate the virtual environment (do this once per session)
source .venv/bin/activate

# Run the dashboard (monitors current directory by default)
opencode-dashboard

# Or specify a repository path
opencode-dashboard --repo /path/to/repo

# Or run via Python
python -m opencode_dashboard --repo /path/to/repo
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **Arrow keys / Click** | Select an issue to view its log |
| **r** | Force refresh all data immediately |
| **l** | Cycle through log files (implement / review / fix / ci_check / pr) |
| **g** | Open selected issue in browser via `gh issue view --web` |
| **p** | Open the issue's PR in browser via `gh pr view --web` |
| **q** | Quit the dashboard |

## Data Sources

The dashboard reads from:

### Local State (polls every 2s)
- `.opencode_logs/issue_<N>/state` - Current state string
- `.opencode_logs/issue_<N>/last_updated` - Unix timestamp of last state change
- `.opencode_logs/issue_<N>/last_model` - Active model name
- `.opencode_logs/issue_<N>/lock/pid` - Worker lock file (indicates active work)
- `.opencode_logs/issue_<N>/.fail_ts` - Backoff timestamp
- `.opencode_logs/.model_backoff/<model_name>` - Fail count and last fail time
- `.opencode_logs/timesheet.jsonl` - Work log entries
- `.opencode_logs/worker_<role>_<N>.log` - Worker log files

### Worker Processes (polls every 2s)
- `pgrep -fa opencode_pipeline` - Find running workers and their roles

### GitHub (polls every 30s)
- `gh pr list --state open` - Open PRs with CI status
- PR body is parsed to find linked issue numbers (format: `#<N>`)

## State Machine

The pipeline follows this state machine:

```
pending → implementing → implemented → reviewing → reviewed
  → fixing → fixed → pr_open → pr_opened → ci_checking → done
                                   ↘ ci_failing → fixing
```

## Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  🔧 opencode pipeline  [repo: comic-pile]       [q] quit        │
├──────────────┬──────────────────────────────────────────────────┤
│ WORKERS      │ ISSUES                                           │
│              │                                                  │
│ implement×3  │ #363  implementing  devstral      2m  [lock]     │
│ ci_check×2   │ #369  pending       —             5m             │
│ review×1     │ #371  ci_checking   gpt-4.1       0m  [lock]     │
│ fix×1        │ #357  pr_opened     —             12m            │
│ pr×1         │ #358  pr_opened     —             12m            │
│ arbiter×1    │ ...                                              │
│              │                                                  │
│ 3 opencode   │ done: 4  pending: 2  in_progress: 8             │
│   runs live  │                                                  │
├──────────────┴──────────────────────────────────────────────────┤
│ SELECTED ISSUE LOG   (#363 implement.log — live tail)           │
│                                                                  │
│ [18:52:01] trying model: mistral/devstral-2512 (attempt 1/3)    │
│ [18:52:03] WARN: model failed (exit 1, 2s), trying next         │
│ [18:52:03] trying model: openai/gpt-4.1 (attempt 2/3)          │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│ MODEL HEALTH  (top 10 by backoff)                               │
│                                                                  │
│ openai/gpt-5.2   fails:4  backoff: 3m 12s remaining            │
│ mistral/medium   fails:2  backoff: 22s remaining                │
│ cerebras/qwen    fails:1  backoff: expired — available          │
├──────────────────────────────────────────────────────────────────┤
│ RECENT TIMESHEET  last 8 entries                                │
│ 18:51  #371  ci_check   gpt-4.1     312s  ✓ success            │
│ 18:49  #363  implement  devstral     2s   ✗ failed             │
└─────────────────────────────────────────────────────────────────┘
```

## Development

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=opencode_dashboard --cov-report=term-missing

# Run linting
make lint

# Format code
ruff format .
```

## Requirements

- Python 3.13+
- textual>=0.80
- humanize>=4.0
- gh CLI (for GitHub integration)

## License

MIT License - see LICENSE file for details
