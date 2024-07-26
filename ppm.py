from enum import Enum
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

class ProductVariablesRanges:
    def __init__(self):
        # the number of people (full time equivalents) on the development team
        self.development_ftes = [4, 5, 6]
        
        # the number of remaining years to develop the product
        self.remaining_development_years = [3, 4, 5]
        
        # the number of remaining years after development that the product will be sold
        self.remaining_delay_years = [0, 1, 2]
        
        # the number of people that need to keep working on the product after development
        self.maintenance_ftes = [0, 0.5, 1]
        
        # the cost to manufacture one unit of the product (in present dollars)
        self.unit_cost_pv = [8000, 10000, 12000]
        
        # the number of remaining years that the product is expected to be sold
        self.remaining_sales_years = [8, 10, 12]

        # the selling price cost factors to compute the price of the product (in present dollars)
        self.unit_price_cost_factor = [1.9, 2.0, 2.1]

        # the number of units that are expected to be sold per year
        self.yearly_unit_sales_lowest_price = [110, 120, 130]
        self.yearly_unit_sales_highest_price = [70, 80, 90]

    def lowest_price(self):
        return self.unit_cost_pv[0] * self.unit_price_cost_factor[0]
    
    def highest_price(self):
        return self.unit_cost_pv[2] * self.unit_price_cost_factor[2]

def gen_t(a, tornado, key):
    if(tornado == Tornado.OFF or key == tornado):
        return np.random.triangular(a[0], a[1], a[2])
    else:
        return a[1]  

class Tornado(Enum):
    OFF = 99
    Dev_Ftes = 0
    Dev_Years = 1
    Delay_Years = 2
    Maint_Ftes = 3
    Unit_Cost = 4
    Sales_Years = 5
    Margin = 6
    Yearly_Sales = 7

class ProductVariablesSnapshot:
    def __init__(self, product_variables_ranges, tornado):
        
        # convert range to actual value using a triangular distribution
        self.development_ftes = gen_t(product_variables_ranges.development_ftes, tornado, Tornado.Dev_Ftes)
        self.remaining_development_years = gen_t(product_variables_ranges.remaining_development_years, tornado, Tornado.Dev_Years)
        self.remaining_delay_years = gen_t(product_variables_ranges.remaining_delay_years, tornado, Tornado.Delay_Years)
        self.maintenance_ftes = gen_t(product_variables_ranges.maintenance_ftes, tornado, Tornado.Maint_Ftes)
        self.unit_cost_pv = gen_t(product_variables_ranges.unit_cost_pv, tornado, Tornado.Unit_Cost)
        self.remaining_sales_years = gen_t(product_variables_ranges.remaining_sales_years, tornado, Tornado.Sales_Years)
        self.unit_price_cost_factor = gen_t(product_variables_ranges.unit_price_cost_factor, tornado, Tornado.Margin)

        # compute the unit price
        self.unit_price_pv = self.unit_cost_pv * self.unit_price_cost_factor

        # interpoloate the yearly unit sales range as a function of the unit price
        price_range = np.array([product_variables_ranges.lowest_price(), product_variables_ranges.highest_price()])
        yearly_unit_sales_range = [0, 0, 0]
        for i in range(3):
            sales_range_i = np.array([product_variables_ranges.yearly_unit_sales_lowest_price[i], product_variables_ranges.yearly_unit_sales_highest_price[i]])
            yearly_unit_sales_range[i] = np.interp(self.unit_price_pv, price_range, sales_range_i)
        
        # convert range to actual value using a triangular distribution
        self.yearly_unit_sales = gen_t(yearly_unit_sales_range, tornado, Tornado.Yearly_Sales)

    def total_remaining_years(self):
        return self.remaining_development_years + self.remaining_delay_years + self.remaining_sales_years

class NpvCalculationResult:
    def __init__(self):
        self.future_development_cost = 0
        self.future_sales = 0
        self.future_cost_of_goods = 0
        self.future_sga = 0
        self.future_unit_sales = 0

    def npv(self):
        return self.future_sales - self.future_cost_of_goods - self.future_sga - self.future_development_cost

    def roi(self):
        return self.npv() / self.future_development_cost

    def annualized_roi(self, years):
        return (1 + self.roi()) ** (1 / years) - 1

def calculate_npv(product_variables_snapshot, company_constants):

    # this is what we will calculate and return 
    result = NpvCalculationResult()

    # DEVELOPMENT COSTS
    year = product_variables_snapshot.remaining_development_years / 2

    # compute the future value of the cost of development for this year
    development_cost_fte_fv = fv(company_constants.development_fte_cost_pv, company_constants.development_cost_trend, year)

    # add the cost of development
    result.future_development_cost += pv(development_cost_fte_fv * product_variables_snapshot.development_ftes * product_variables_snapshot.remaining_development_years, company_constants.market_return, year)

    # DELAY COSTS
    year = product_variables_snapshot.remaining_development_years + product_variables_snapshot.remaining_delay_years / 2

    # compute the future value of the cost of development for this year
    development_cost_fte_fv = fv(company_constants.development_fte_cost_pv, company_constants.development_cost_trend, year)

    # add the cost of development
    result.future_development_cost += pv(development_cost_fte_fv * product_variables_snapshot.maintenance_ftes * product_variables_snapshot.remaining_delay_years, company_constants.market_return, year)

    # SALES
    year = product_variables_snapshot.remaining_development_years + product_variables_snapshot.remaining_delay_years + product_variables_snapshot.remaining_sales_years / 2

    # compute the future value of the selling price, unit cost, and cost of development for this year
    unit_price_fv = fv(product_variables_snapshot.unit_price_pv, company_constants.unit_price_trend, year)
    unit_cost_fv = fv(product_variables_snapshot.unit_cost_pv, company_constants.unit_cost_trend, year)
    development_cost_fte_fv = fv(company_constants.development_fte_cost_pv, company_constants.development_cost_trend, year)
    
    # compute the selling, general, and administrative expenses per unit
    sga_fv = unit_price_fv * company_constants.sga_percentage

    # record unit sales, costs of development, sales, cost of goods, sga
    result.future_unit_sales = product_variables_snapshot.yearly_unit_sales * product_variables_snapshot.remaining_sales_years
    result.future_development_cost += pv(development_cost_fte_fv * product_variables_snapshot.maintenance_ftes * product_variables_snapshot.remaining_sales_years, company_constants.market_return, year)
    result.future_sales = pv(unit_price_fv * product_variables_snapshot.yearly_unit_sales * product_variables_snapshot.remaining_sales_years, company_constants.market_return, year)
    result.future_cost_of_goods = pv(unit_cost_fv * product_variables_snapshot.yearly_unit_sales * product_variables_snapshot.remaining_sales_years, company_constants.market_return, year)
    result.future_sga = pv(sga_fv * product_variables_snapshot.yearly_unit_sales * product_variables_snapshot.remaining_sales_years, company_constants.market_return, year)

    return result

class TornadoTracker:
    def __init__(self):
        self.min_value = float('inf')
        self.max_value = float('-inf')

    def add(self, value):
        if value < self.min_value:
            self.min_value = value
        if value > self.max_value:
            self.max_value = value
    
    def range(self):
        return self.max_value - self.min_value

company_constants = CompanyConstants()
product_variables_ranges = ProductVariablesRanges()

npvs = []
annualized_rois = []
development_costs = []
unit_sales = []
sales = []
years = []

tornado_trackers = {}
for tornado in Tornado:
    tornado_trackers[tornado] = TornadoTracker()

for i in range(10000):
    product_variables_snapshot = ProductVariablesSnapshot(product_variables_ranges, Tornado.OFF)
    result = calculate_npv(product_variables_snapshot, company_constants)
    npvs.append(result.npv()/1000000)
    development_costs.append(result.future_development_cost/1000000)
    annualized_rois.append(result.annualized_roi(product_variables_snapshot.total_remaining_years())*100)
    unit_sales.append(result.future_unit_sales)
    sales.append(result.future_sales/1000000)
    years.append(product_variables_snapshot.total_remaining_years())

    # loop through all the tornado variables
    for tornado in Tornado:
        if(tornado != Tornado.OFF):
            product_variables_snapshot = ProductVariablesSnapshot(product_variables_ranges, tornado)
            result = calculate_npv(product_variables_snapshot, company_constants)
            tornado_trackers[tornado].add(result.npv()/1000000)

# Plotting
plt.figure(figsize=(10, 5))

rows = 2
cols = 3

plt.subplot(rows, cols, 1)
plt.hist(unit_sales, bins=30, edgecolor='black')
plt.yticks([])
plt.xlabel('Sales (units)')

plt.subplot(rows, cols, 2)
plt.hist(sales, bins=30, edgecolor='black')
plt.yticks([])
plt.xlabel('Sales ($ millions)')

plt.subplot(rows, cols, 3)
plt.hist(development_costs, bins=30, edgecolor='black')
plt.yticks([])
plt.xlabel('Development ($ millions)')

# plt.subplot(rows, cols, 4)
# plt.hist(years, bins=30, edgecolor='black')
# plt.yticks([])
# plt.xlabel('Total Remaining Years')

plt.subplot(rows, cols, 4)
plt.hist(npvs, bins=30, edgecolor='black')
plt.yticks([])
plt.xlabel('NPV ($ millions)')

plt.subplot(rows, cols, 5)
plt.hist(annualized_rois, bins=30, edgecolor='black')
plt.yticks([])
plt.xlabel('Annualized ROI (%)')

plt.subplot(rows, cols, 6)
tornado_names = [tornado.name for tornado in Tornado]
range_values = [tornado_trackers[tornado].range() for tornado in Tornado]
plt.barh(tornado_names, range_values)
plt.xlabel('NPV Range ($ millions)')

plt.tight_layout()
plt.show()