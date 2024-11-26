import pytest
from financial_helpers import pv, fv, cost_factor

def test_pv():
    assert pv(1000, 0.05, 10) == pytest.approx(613.91, 0.01)
    assert pv(500, 0.03, 5) == pytest.approx(431.92, 0.01)
    assert pv(2000, 0.07, 3) == pytest.approx(1632.65, 0.01)

def test_fv():
    assert fv(1000, 0.05, 10) == pytest.approx(1628.89, 0.01)
    assert fv(500, 0.03, 5) == pytest.approx(579.64, 0.01)
    assert fv(2000, 0.07, 3) == pytest.approx(2450.48, 0.01)

def test_cost_factor():
    assert cost_factor(0.2) == pytest.approx(1.25, 0.01)
    assert cost_factor(0.3) == pytest.approx(1.4286, 0.01)
    assert cost_factor(0.1) == pytest.approx(1.1111, 0.01)