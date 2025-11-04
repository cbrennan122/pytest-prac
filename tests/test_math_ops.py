import pytest
from math_ops import add, divide, subtract
import logging
log = logging.getLogger(__name__)

@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (-1, 1, 0),
    (0, 0, 0),
])
def test_add(a, b, expected):
    log.info(f"Starting test_sum with a={a}, b={b}, expected={expected}")
    assert add(a, b) == expected

def test_divide_valid():
    log.info(f"Starting test_divide_valid")
    assert divide(10, 2) == 5

def test_divide_by_zero():
    log.info(f"Starting test_divide_by_zero")
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(5, 0)

@pytest.mark.parametrize("a, b, expected", [
    (5, 3, 2),
    (0, 0, 0),
    (-1, 1, -2),
])
def test_subtract(a, b, expected):
    log.info(f"Starting test_subtract with a={a}, b={b}, expected={expected}")
    assert subtract(a, b) == expected