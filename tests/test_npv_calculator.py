import pytest
from npv_calculator import NpvCalculator
import financial_helpers as fh
import npv_calculation_result as ncr

class MockProductVariablesSnapshot:
    def total_years(self): return 1
    years_mix_delay = 0.5
    def development_ftes_this_mix_month(self): return 1
    def unit_sales_this_mix_month(self): return 10
    years_of_consumable_sales = 1
    unit_cost_pv = 100
    unit_price_pv = 150
    sga_factor = 0.1
    yearly_unit_consumable_sales = 120
    consumable_margin = 0.2

class MockCompanyConstants:
    yearly_development_fte_cost_pv = 120000
    development_cost_trend = 0.03
    product_cost_trend = 0.02
    product_price_trend = 0.02
    market_return = 0.05

@pytest.fixture
def npv_calculator():
    return NpvCalculator()

@pytest.fixture
def product_variables_snapshot():
    return MockProductVariablesSnapshot()

@pytest.fixture
def company_constants():
    return MockCompanyConstants()

def test_calculate_product_npv(npv_calculator, product_variables_snapshot, company_constants):
    result = npv_calculator.calculate_product_npv(product_variables_snapshot, company_constants)
    assert isinstance(result, ncr.NpvCalculationResult)
    assert result.development_cost > 0
    assert result.sales > 0
    assert result.consumable_sales > 0
    assert result.cost_of_goods > 0
    assert result.sga > 0
    assert result.unit_sales > 0
    assert len(result.ftes_by_month) > 0
    assert len(result.sales_by_month) > 0
    assert len(result.consumable_sales_by_month) > 0
    assert len(result.cumulative_net_by_month) > 0