# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial TUI dashboard for monitoring opencode pipelines
- Real-time issue state tracking with state machine visualization
- Worker process monitoring via pgrep
- Model health monitoring with backoff tracking
- GitHub PR integration with CI status checking
- Timesheet tracking showing recent work
- Auto-refresh every 2s (local) and 30s (GitHub)
- Keyboard shortcuts for navigation and actions
- Live log tailing for selected issues

## [0.1.0] - 2026-03-25

### Added

- Initial release
- Python 3.13 support
- Textual TUI framework integration
- Support for monitoring multiple opencode pipeline instances
- Comprehensive dashboard with workers, issues, logs, model health, and timesheet panels
