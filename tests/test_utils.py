import pytest
from app.services.consumer import calculate_moving_average

def test_calculate_moving_average_exact():
    """
    Test that the moving average is exactly 100 for known inputs.
    """
    prices = [100, 101, 99, 102, 98]
    assert calculate_moving_average(prices) == 100

def test_calculate_moving_average_fractional():
    """
    Test that the moving average handles non-integer results correctly.
    """
    prices = [1, 2, 3]
    assert calculate_moving_average(prices) == pytest.approx(2.0)
