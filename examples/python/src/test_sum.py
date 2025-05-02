"""Test Sum."""

from src.sum import sum  # noqa: A004


def test_sum() -> None:
    """Test Sum."""
    assert sum(2, 4) == 6  # noqa: PLR2004, S101
    assert sum(2, 4) != 5  # noqa: PLR2004, S101
