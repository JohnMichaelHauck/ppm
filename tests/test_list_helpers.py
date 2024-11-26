import pytest
from list_helpers import safe_index, add_value_to_index

def test_safe_index():
    assert safe_index([1, 2, 3], 1) == 2
    assert safe_index([1, 2, 3], 0) == 1
    assert safe_index(5, 0) == 5
    assert safe_index(5.5, 2) == 5.5

def test_add_value_to_index():
    array = [1, 2, 3]
    add_value_to_index(array, 1, 5)
    assert array == [1, 7, 3]

    array = [1, 2, 3]
    add_value_to_index(array, 3, 4)
    assert array == [1, 2, 3, 4]

    array = [1, 2, 3]
    add_value_to_index(array, 5, 2)
    assert array == [1, 2, 3, 0, 0, 2]