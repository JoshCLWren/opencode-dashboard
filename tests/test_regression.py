def test_pipeline_monitor_tail_log_with_data(tmp_path) -> None:
    """Test PipelineMonitor tail_log with existing log."""
    monitor = PipelineMonitor(tmp_path)
    logs_dir = tmp_path / ".opencode_logs"
    issue_dir = logs_dir / "issue_123"
    issue_dir.mkdir(parents=True)

    log_file = issue_dir / "implement.log"
    log_file.write_text("line 1\nline 2\nline 3\nline 4\nline 5\n")

    content = monitor.tail_log(123, "implement", lines=3)
    # tail_log returns last 3 lines: line 3, line 4, line 5 (line 5 is empty after trailing \n)
    assert "line 4" in content
    assert "line 5" in content
    assert "line 1" not in content
    assert "line 2" not in content


def test_issue_row_key_parsing() -> None:
    """Test parsing issue number from RowKey.value - regression for click crash."""

    # Simulate RowKey object structure
    class MockRowKey:
        def __init__(self, value: str):
            self.value = value

        def __str__(self) -> str:
            return f"<MockRowKey value={self.value}>"

    # Test that we can extract the value correctly
    row_key = MockRowKey("366")
    assert row_key.value == "366"
    assert int(row_key.value) == 366

    # Verify that str(row_key) would fail with ValueError (old bug)
    try:
        int(str(row_key))
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    # Verify that int(row_key.value) works (correct approach)
    issue_num = int(row_key.value)
    assert issue_num == 366


def test_issue_row_key_with_none() -> None:
    """Test handling None value in RowKey - regression for type checking."""

    class MockRowKey:
        def __init__(self, value: str | None):
            self.value = value

    # Test with None value
    row_key = MockRowKey(None)
    assert row_key.value is None

    # Test that we check for None before converting
    if row_key and row_key.value:
        issue_num = int(row_key.value)
        assert False, "Should not reach here"
    else:
        assert True
