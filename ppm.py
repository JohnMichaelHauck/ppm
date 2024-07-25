import numpy as np # linear algebra library
import matplotlib.pyplot as plt # plotting library

def pv(future_value, rate, periods):
    return future_value / (1 + rate) ** periods

def fv(present_value, rate, periods):
    return present_value * (1 + rate) ** periods

class CompanyConstants:
    def __init__(self):
        # what we would expect to earn on an investment in a financial market with a similar risk
        self.market_return = 0.03
        
        # how much it costs per person to run a product development team (in present dollars)
        self.development_fte_cost_pv = 50000
        
        # how much the cost of development increases each year
        self.development_cost_trend = 0.03
        
        # how much the cost of a product increases each year
        self.unit_cost_trend = 0.03
        
        # how much the selling price of a product increases each year
        self.unit_price_trend = 0.03
        
        # the percentage of the selling price that is allocated to cover selling, general, and administrative expenses
        self.sga_percentage = 0.30

class ProductVariables:
    def __init__(self):
        # the number of people (full time equivalents) on the development team
        self.development_ftes = np.random.triangular(4, 5, 6)
        
        # the number of years remaining to develop the product
        self.remaining_development_years = round(np.random.triangular(3, 4, 5))
        
        # the number of remaining years after development that the product will be sold
        self.remaining_delay_years = round(np.random.triangular(0, 1, 2))
        
        # the number of people that need to keep working on the product after development
        self.maintenance_ftes = np.random.triangular(0, 0.5, 1)
        
        # the cost to manufacture one unit of the product (in present dollars)
        self.unit_cost_pv = np.random.triangular(8000, 10000, 12000)
        
        # the selling price of the product (in present dollars)
        self.unit_price_pv = np.random.triangular(self.unit_cost_pv * 1.9, self.unit_cost_pv * 2, self.unit_cost_pv * 2.1)
        
        # the number of units that are expected to be sold per year
        self.yearly_unit_sales = 100
        
        # the number of years that the product is expected to be sold
        self.remaining_years_of_sales = 10

        # the number of units that are expected to be sold per year
        price_range = np.array([16000, 24000])
        sales_range = np.array([120, 80])
        exact_sales = np.interp(20000, price_range, sales_range)
        self.yearly_unit_sales = np.random.triangular(exact_sales * 0.9, exact_sales, exact_sales * 1.1)

        # the number of years that the product is expected to be sold
        self.remaining_years_of_sales = round(np.random.triangular(8, 10, 12))

class NpvCalculationResult:
    def __init__(self):
        self.future_development_cost = 0
        self.future_sales = 0
        self.future_cost_of_goods = 0
        self.future_sga = 0

    def npv(self):
        return self.future_sales - self.future_cost_of_goods - self.future_sga - self.future_development_cost

def calculate_npv(product_variables, company_constants):

    # this is what we will calculate and return 
    npv_calculation_result = NpvCalculationResult()

    # starting at year zero (today)
    year = 0

    # let's compute the remaining product development costs, one year at a time
    for _ in range(product_variables.remaining_development_years):

        # compute the future value of the cost of development for this year
        development_cost_fte_fv = fv(company_constants.development_fte_cost_pv, company_constants.development_cost_trend, year)

        # add the cost of development
        npv_calculation_result.future_development_cost += pv(development_cost_fte_fv * product_variables.development_ftes, company_constants.market_return, year)

        # move to the next year
        year += 1

    # let's compute the cost of delay
    for _ in range(product_variables.remaining_delay_years):

        # compute the future value of the cost of development for this year
        development_cost_fte_fv = fv(company_constants.development_fte_cost_pv, company_constants.development_cost_trend, year)

        # add the cost of development
        npv_calculation_result.future_development_cost += pv(development_cost_fte_fv * product_variables.maintenance_ftes, company_constants.market_return, year)

        # move to the next year
        year += 1


    # let's compute and add in the sales
    for j in range(product_variables.remaining_years_of_sales):
        
        # compute the future value of the selling price, unit cost, and cost of development for this year
        list_price_fv = fv(product_variables.unit_price_pv, company_constants.unit_price_trend, year)
        unit_cost_fv = fv(product_variables.unit_cost_pv, company_constants.unit_cost_trend, year)
        development_cost_fte_fv = fv(company_constants.development_fte_cost_pv, company_constants.development_cost_trend, year)
        
        # compute the selling, general, and administrative expenses per unit
        sga_fv = list_price_fv * company_constants.sga_percentage

        # compute the future value of this year
        development_cost_fte_fv = fv(company_constants.development_fte_cost_pv, company_constants.development_cost_trend, year)

        # add the cost of development, sales, cost of goods, and sga
        npv_calculation_result.future_development_cost += pv(development_cost_fte_fv * product_variables.maintenance_ftes, company_constants.market_return, year)
        npv_calculation_result.future_sales += pv(list_price_fv * product_variables.yearly_unit_sales, company_constants.market_return, year)
        npv_calculation_result.future_cost_of_goods += pv(unit_cost_fv * product_variables.yearly_unit_sales, company_constants.market_return, year)
        npv_calculation_result.future_sga += pv(sga_fv * product_variables.yearly_unit_sales, company_constants.market_return, year)

        # move to the next year
        year += 1

    return npv_calculation_result

company_constants = CompanyConstants()

def simulate_npv():
    product_variables = ProductVariables()
    npv_calculation_result = calculate_npv(product_variables, company_constants)
    return npv_calculation_result

npvs = []
for i in range(10000):
    npv_calculation_result = simulate_npv()
    npvs.append(npv_calculation_result.npv())
plt.hist(npvs, bins=30)
plt.xlabel('NPV')
plt.ticklabel_format(style='plain', axis='x')
plt.show()