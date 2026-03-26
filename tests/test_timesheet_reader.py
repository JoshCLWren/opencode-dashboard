"""Tests for TimesheetReader cursor-based pagination."""

import json

from opencode_dashboard.dashboard import TimesheetReader


def test_timesheet_reader_empty_file(tmp_path) -> None:
    """Test TimesheetReader with non-existent file."""
    reader = TimesheetReader(tmp_path / "nonexistent.jsonl")
    entries = reader.read_last_n(10)
    assert entries == []


def test_timesheet_reader_small_file(tmp_path) -> None:
    """Test TimesheetReader with small file (less than requested)."""
    timesheet = tmp_path / "timesheet.jsonl"
    timesheet.write_text(
        '{"ts":"2026-03-25T12:00:00Z","issue":123,"role":"implement","model":"gpt-4","duration_s":60,"outcome":"success"}\n'
    )

    reader = TimesheetReader(timesheet)
    entries = reader.read_last_n(10)
    assert len(entries) == 1
    assert entries[0].issue == 123


def test_timesheet_reader_read_last_n(tmp_path) -> None:
    """Test TimesheetReader reads exactly N entries from end."""
    timesheet = tmp_path / "timesheet.jsonl"
    # Write 10 entries
    for i in range(10):
        entry = {
            "ts": f"2026-03-25T12:0{i}:00Z",
            "issue": 100 + i,
            "role": "implement",
            "model": "gpt-4",
            "duration_s": 60,
            "outcome": "success",
        }
        with timesheet.open("a") as f:
            f.write(json.dumps(entry) + "\n")

    reader = TimesheetReader(timesheet)
    entries = reader.read_last_n(5)

    # Should get last 5 entries (issues 105-109)
    assert len(entries) == 5
    assert entries[0].issue == 105
    assert entries[4].issue == 109


def test_timesheet_reader_handles_malformed_lines(tmp_path) -> None:
    """Test TimesheetReader skips malformed JSON lines."""
    timesheet = tmp_path / "timesheet.jsonl"
    timesheet.write_text(
        '{"ts":"2026-03-25T12:00:00Z","issue":123,"role":"implement","model":"gpt-4","duration_s":60,"outcome":"success"}\n'
        "invalid json line\n"
        '{"ts":"2026-03-25T12:01:00Z","issue":124,"role":"review","model":"gpt-4","duration_s":30,"outcome":"failed"}\n'
        "another bad line\n"
    )

    reader = TimesheetReader(timesheet)
    entries = reader.read_last_n(10)

    # Should skip malformed lines and return 2 valid entries
    assert len(entries) == 2
    assert entries[0].issue == 123
    assert entries[1].issue == 124


def test_timesheet_reader_efficiency_on_large_file(tmp_path) -> None:
    """Test TimesheetReader is reasonably fast even on large files."""
    timesheet = tmp_path / "timesheet.jsonl"

    # Create a file with 1000 entries
    for i in range(1000):
        entry = {
            "ts": f"2026-03-25T12:{i:02d}:00Z",
            "issue": 1000 + i,
            "role": "implement",
            "model": "gpt-4",
            "duration_s": 60,
            "outcome": "success",
        }
        with timesheet.open("a") as f:
            f.write(json.dumps(entry) + "\n")

    reader = TimesheetReader(timesheet)

    # Time how long it takes to read last 10 entries
    import time

    start = time.time()
    entries = reader.read_last_n(10)
    elapsed = time.time() - start

    # Should be reasonably fast (< 1 second) even for 1000-line file
    assert elapsed < 1.0
    assert len(entries) == 10
    # Should get last 10 entries (990-999)
    assert entries[0].issue == 990
    assert entries[9].issue == 999


def test_timesheet_reader_empty_lines(tmp_path) -> None:
    """Test TimesheetReader handles empty lines."""
    timesheet = tmp_path / "timesheet.jsonl"
    timesheet.write_text(
        '\n\n{"ts":"2026-03-25T12:00:00Z","issue":123,"role":"implement","model":"gpt-4","duration_s":60,"outcome":"success"}\n\n\n'
    )

    reader = TimesheetReader(timesheet)
    entries = reader.read_last_n(10)

    # Should skip empty lines
    assert len(entries) == 1
    assert entries[0].issue == 123
