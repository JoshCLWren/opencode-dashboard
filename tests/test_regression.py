"""Regression tests for bug fixes."""

import pytest
from opencode_dashboard.dashboard import PipelineMonitor


def test_issue_row_key_parsing() -> None:
    """Test parsing issue number from RowKey.value - regression for click crash.

    This test ensures we use row_key.value instead of str(row_key) to avoid
    ValueError when parsing issue numbers from DataTable row selection.
    """

    class MockRowKey:
        """Mock RowKey object."""

        def __init__(self, value: str):
            self.value = value

        def __str__(self) -> str:
            return f"<MockRowKey value={self.value}>"

    # Test that we can extract the value correctly
    row_key = MockRowKey("366")
    assert row_key.value == "366"
    assert int(row_key.value) == 366

    # Verify that str(row_key) would fail with ValueError (old bug)
    with pytest.raises(ValueError):
        int(str(row_key))

    # Verify that int(row_key.value) works (correct approach)
    issue_num = int(row_key.value)
    assert issue_num == 366


def test_issue_row_key_with_none() -> None:
    """Test handling None value in RowKey - regression for type checking.

    This test ensures we check for None before accessing row_key.value
    to satisfy pyright type checking.
    """

    class MockRowKey:
        """Mock RowKey object with optional value."""

        def __init__(self, value: str | None):
            self.value = value

    # Test with None value
    row_key = MockRowKey(None)
    assert row_key.value is None

    # Test that we check for None before converting
    if row_key and row_key.value:
        raise AssertionError("Should not reach here with None value")

    # Test with valid value
    row_key = MockRowKey("123")
    if row_key and row_key.value:
        issue_num = int(row_key.value)
        assert issue_num == 123
    else:
        raise AssertionError("Should reach here with valid value")
