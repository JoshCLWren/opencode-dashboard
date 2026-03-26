# opencode-dashboard UX Improvements Plan

## Overview
UX audit revealed several critical issues that make the dashboard feel broken and confusing.

## Priority 1: Fix Initial Load (CRITICAL)

**Problem**: Dashboard deliberately waits 2s before loading data, leaving user staring at "Loading..." placeholder.

**Fix**:
- File: `opencode_dashboard/dashboard.py:823-828`
- Change: Load data immediately on mount instead of waiting for timer
- Impact: Eliminates 19-second load time, makes app feel instant

```python
def on_mount(self) -> None:
    """Set up refresh timers and load initial data."""
    self.set_interval(2, self.refresh_local)
    self.set_interval(30, self.refresh_github)
    # Load data immediately on mount for instant UX
    self.refresh_local()
    self.refresh_github()
```

## Priority 2: Redesign Layout

**Current Layout Issues**:
- Workers panel (25 chars) takes prime left column for low-density info
- Issues table cramped in top-right despite being primary interaction target
- Log viewer is 3fr (huge) but often empty or confusing
- Model health shows confusing "expired — available" status

**Proposed Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  🔧 opencode pipeline  [comic-pile]   [q]uit  [r]efresh           │
├───────────────────────────────────────────────────────────────────┤
│  📊 SYSTEM HEALTH                                                  │
│  Workers: 9 live  |  Issues: 4 done, 2 pending, 8 in-progress     │
│  Failing models: 2  |  CI status: 1 failing, 2 pending            │
├───────────────────────────────────────────────────────────────────┤
│  📋 ISSUES (arrow keys to navigate)                                  │
│  ┌──────┬──────────────┬─────────────┬──────┬──────────────────┐ │
│  │#363  │ implementing │ devstral    │ 2m   │ [lock]           │ │
│  │#369  │ pending      │ —           │ 5m   │                  │ │
│  └──────┴──────────────┴─────────────┴──────┴──────────────────┘ │
├───────────────────────────────────────────────────────────────────┤
│  📜 LOGS  (select issue above to view its logs)                       │
│  [Recent activity across all workers...]                            │
├───────────────────────────────────────────────────────────────────┤
│  📊 RECENT ACTIVITY (timesheet)                                   │
│  18:51  #371  ci_check   gpt-4.1     312s  ✓ success             │
│  18:49  #363  implement  devstral     2s   ✗ failed              │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation**:
- Add `SystemHealthHeader` widget to replace WorkersPanel
- Rebalance vertical proportions: issues 2fr, logs 1.5fr
- Consolidate model health into system health header
- Move timesheet to bottom panel

## Priority 3: Simplify Log Viewer

**Problem**: Two modes (recent logs vs issue logs) with no clear indication of which is active.

**Fix**:
- Remove `_show_recent_logs()` method
- Always show issue-specific logs when issue selected
- Show helpful message when no issue selected: "Select an issue above to view its logs"
- Remove confusing mode switching

## Priority 4: Add Loading Indicators

**Problem**: No visual feedback during data fetch makes app feel laggy.

**Fix**:
- Add spinner or skeleton during GitHub PR fetch (30s can feel long)
- Use `Spinner` widget from Textual
- Show skeleton rows in issues table during initial load

## Priority 5: Clarify Model Health

**Problem**: "expired — available" is confusing.

**Fix**:
- Change to "ready" instead of "expired — available"
- Highlight failing models in red
- Hide models with 0 fails from view to reduce clutter

## Implementation Order

1. **Do this first**: Fix initial load (Priority 1)
2. Then: Redesign layout (Priority 2)
3. Then: Simplify log viewer (Priority 3)
4. Finally: Add loading indicators (Priority 4)

## Notes

- Current coverage: 41%, need to maintain >35%
- All lint checks must pass
- Add regression tests for any new features
- Keep file size under 1000 lines if possible
