# Repository Guidelines

## Project Structure & Module Organization

The main application code lives in `opencode_dashboard/` directory. This is a TUI dashboard application built with Textual for monitoring opencode pipelines.

## Build, Test, and Development Commands

- `source .venv/bin/activate`: activate the virtual environment (do this once per session)
- `uv sync --group dev`: install dependencies via uv
- `opencode-dashboard`: run the dashboard entrypoint (monitors current directory by default)
- `python -m opencode_dashboard --repo /path/to/repo`: run with explicit repo path
- `pytest`: run tests
- `make lint`: run ruff + pyright checks

## Getting Started

1. Run `uv sync --group dev` to install all dependencies
2. Run `source .venv/bin/activate` to activate the virtual environment
3. Run `opencode-dashboard --repo /path/to/repo` to start monitoring
4. Use keyboard shortcuts: `q` to quit, `r` to refresh, `g`/`p` to open issue/PR in browser, `l` to cycle logs

## Test Coverage Requirements

- Current target: 96% coverage threshold (configured in `pyproject.toml`)
- Always run `pytest --cov=opencode_dashboard --cov-report=term-missing` to check missing coverage
- When touching logic or input handling, ensure tests are added to maintain coverage

## Coding Style & Naming Conventions

Follow standard PEP 8 spacing (4 spaces, 100-character soft wrap) and favor descriptive snake_case for functions and variables.

Ruff configuration (from `pyproject.toml`):
- Line length: 100 characters
- Python version: 3.13
- Enabled rules: E, F, I, N, UP, B, C4, D
- Ignored: D203, D213, E501, ANN401

## Pre-commit Hook

A pre-commit hook is installed in `.git/hooks/pre-commit` that automatically runs:
- Check for type/linter ignores in staged files
- Run the shared lint script (`scripts/lint.sh`)

The lint script runs:
- Python compilation check
- Ruff linting
- Pyright type checking

The hook will block commits containing `# type: ignore`, `# noqa`, `# ruff: ignore`, or `# pylint: ignore`.

## Code Quality Standards

- Run linting after each change: `make lint` or `bash scripts/lint.sh`
- Use specific types instead of `Any` in type annotations (ruff ANN401 rule)
- Run tests when you touch logic or input handling: `pytest`
- Always write a regression test when fixing a bug
- If you break something while fixing it, fix both in the same PR
- Do not use in-line comments to disable linting or type checks

## Style Guidelines

- Keep helpers explicit and descriptive (snake_case), and annotate public functions with precise types
- Avoid shell-specific shortcuts; prefer Python APIs and `pathlib.Path` helpers
- Use dataclasses for typed data containers
- Name widget update methods `update_content()` to avoid conflicts with Textual's built-in `refresh()` method

## Branch Workflow

- Always create a feature branch from `main` before making changes:
  - `git checkout -b feature-name`
  - Use descriptive names like `fix-bug` or `add-feature`
- Push the feature branch to create a pull request
- After your PR is merged, update your local `main`:
  - `git checkout main`
  - `git pull`
  - Delete the merged branch: `git branch -d feature-name`

## Testing Guidelines

- Automated tests live in `tests/` and run with `python -m pytest` (or `make pytest`)
- When adding tests, keep `pytest` naming like `test_example_function`
- Always use appropriate fixtures from `conftest.py` for testing dependencies

## Commit & Pull Request Guidelines

- Use imperative, component-scoped commit messages (e.g., "Add feature X")
- Bundle related changes per commit
- PR summary should describe user impact and testing performed
- Attach screenshots when UI is affected

## Project-Specific Patterns

### Textual Widget Naming

To avoid conflicts with Textual's built-in widget methods:
- Use `update_content()` instead of `refresh()` for custom update methods
- Widget IDs should be set directly: `widget.id = "id-name"`
- Do not chain `.id()` calls as they return None

### Data Model

All state tracking uses dataclasses:
- `IssueState`: Current state of a single issue
- `WorkerInfo`: Worker process information
- `ModelHealth`: Model backoff health
- `TimesheetEntry`: Timesheet log entry
- `PRInfo`: GitHub PR information

### Refresh Strategy

The dashboard uses two refresh intervals:
- 2 seconds: Local state (issues, workers, models, timesheet)
- 30 seconds: GitHub state (PRs)

Use `update_content()` methods on widgets to trigger updates without conflicting with Textual's refresh cycle.

### Cursor Row Access

DataTable's `cursor_row` returns a `DataRowKey` (string-like), not a list. Convert to string for parsing: `issue_num = int(str(issues.cursor_row))`.
