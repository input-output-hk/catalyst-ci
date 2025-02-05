from src.sum import sum


def test_sum():
    assert sum(2, 4) == 6
    assert sum(2, 4) != 5
