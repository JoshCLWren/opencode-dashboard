# Contributing

Thanks for contributing to this project. This project values clear, approachable
code and best practices. Please follow the checks below for any code
change.

## Pre-commit hook

A pre-commit hook is installed in `.git/hooks/pre-commit` that automatically runs:
- Check for type/linter ignores in staged files
- Run the shared lint script (`scripts/lint.sh`)

The lint script runs:
- Python compilation check
- Ruff linting
- Any type usage check (ruff ANN401 rule)
- Pyright type checking

The hook will block commits containing `# type: ignore`, `# noqa`, `# ruff: ignore`, or `# pylint: ignore`.

To test the hook manually: `make githook` or `bash scripts/lint.sh`

## Code quality standards

- Run linting after each change:
  - `make lint` or `bash scripts/lint.sh`
- Use specific types instead of `Any` in type annotations (ruff ANN401 rule)
- Run tests when you touch logic or input handling:
  - `uv run python -m pytest`
- Always write a regression test when fixing a bug.
- If you break something while fixing it, fix both in the same PR.
- Do not use in-line comments to disable linting or type checks.
- Do not narrate your code with comments; prefer clear code and commit messages.
- Do not use `pytest.skip` in test files; all tests must run in CI.

## Style guidelines

- Keep helpers explicit and descriptive (snake_case), and annotate public
  functions with precise types.
- Avoid shell-specific shortcuts; prefer Python APIs and `pathlib.Path` helpers.

## Branch workflow

- Always create a feature branch from `main` before making changes:
  - `git checkout -b feature-name`
  - Use descriptive names like `fix-bug` or `add-feature`
- Push the feature branch to create a pull request
- After your PR is merged, update your local `main`:
  - `git checkout main`
  - `git pull`
  - Delete the merged branch: `git branch -d feature-name`

## Pull request guidelines

- Use imperative, component-scoped commit messages (e.g., "Add feature X")
- Bundle related changes per commit
- PR summary should describe user impact and testing performed
- Attach screenshots when UI is affected
