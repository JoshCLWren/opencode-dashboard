# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Warning banners to README.md and AGENTS.md to clearly indicate template files
- Post-initialization checklist section to README.md
- Placeholder system using `[[MODULE_NAME]]` for easy replacement
- POST_INIT_CHECKLIST.md with comprehensive post-init guidance
- TEMPLATE_GUIDE.md explaining template purpose and usage
- Improved `make init` output with summary of changes and next steps
- Comment placeholder in CI workflow for Codecov token setup
- Git worktrees section marked as optional in AGENTS.md

### Changed

- Replaced hardcoded "example_module" with `[[MODULE_NAME]]` placeholder in README.md
- Updated CI badge URLs to use placeholders (YOUR_USERNAME/YOUR_REPO)
- Enhanced `make init` target to provide detailed summary of automated changes
- Improved documentation clarity with visual indicators (⚠️, ✅, 📋, etc.)

### Improved

- Template now provides clearer guidance on what gets automated vs manual
- Better distinction between template-specific patterns and project-specific needs
- More comprehensive documentation for new users
- Enhanced visibility of post-initialization requirements

## [0.1.0] - 2024-01-15

### Added

- Initial template release
- Python 3.13 support
- uv package manager integration
- pytest with 96% minimum coverage
- ruff for linting and formatting
- pyright for type checking
- Pre-commit hooks for code quality
- GitHub Actions CI workflow
- Make commands for common tasks
- AGENTS.md for AI agent guidelines
