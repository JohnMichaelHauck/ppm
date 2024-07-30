from enum import Enum
import numpy as np # linear algebra library
import matplotlib.pyplot as plt # plotting library
import pandas as pd

def pv(future_value, rate, periods):
    return future_value / (1 + rate) ** periods

def fv(present_value, rate, periods):
    return present_value * (1 + rate) ** periods

class CompanyConstants:
    def __init__(self):
        # what we would expect to earn on an investment in a financial market with a similar risk
        self.market_return = 0.03
        
        # how much it costs per person to run a product development team (in present dollars)
        self.yearly_development_fte_cost_pv = 50000
        
        # how much the cost of development increases each year
        self.development_cost_trend = 0.03
        
        # how much the cost of a product increases each year
        self.unit_cost_trend = 0.03
        
        # the percentage of the selling price that is allocated to cover selling, general, and administrative expenses
        self.sga_percentage = 0.30

class ProductVariablesRanges:
    def __init__(self):
        # the number of people (full time equivalents) on the development team
        self.development_ftes = [4, 5, 6]

        # development years profile
        self.years_before_development = 0
        self.years_of_development_growth = 0
        self.years_of_development_maturity = [3, 4, 5]
        self.years_of_development_decline = 0
        
        # the number of people that need to keep working on the product after development
        self.maintenance_ftes = [0, 0.5, 1]
        
        # the cost to manufacture one unit of the product (in present dollars)
        self.unit_cost_pv = [8000, 10000, 12000]
        
        # the selling price cost factors to compute the price of the product (in present dollars)
        self.unit_price_cost_factor = [1.9, 2.0, 2.1]

        # the number of units that are expected to be sold per year
        self.yearly_unit_sales_lowest_price = [110, 120, 130]
        self.yearly_unit_sales_highest_price = [70, 80, 90]

        # sales years profile
        self.years_before_sales = 1
        self.years_of_sales_growth = 0
        self.years_of_sales_maturity = [8, 10, 12]
        self.years_of_sales_decline = 0

    def lowest_price(self):
        return self.unit_cost_pv[0] * self.unit_price_cost_factor[0]
    
    def highest_price(self):
        return self.unit_cost_pv[2] * self.unit_price_cost_factor[2]

def gen_t(a, tornado, key):
    if isinstance(a, list):
        if(tornado == Tornado.OFF or key == tornado):
            return np.random.triangular(a[0], a[1], a[2])
        else:
            return a[1]  
    else:   
        return a

class Tornado(Enum):
    OFF = 99
    Dev_Ftes = 0
    Dev_Years = 1
    Maint_Ftes = 2
    Sales_Years = 3
    Unit_Cost = 4
    Margin = 5
    Yearly_Sales = 6

class ProductVariablesSnapshot:
    def __init__(self, product_variables_ranges, tornado):
        
        # convert various ranges to actual value using a triangular distribution (or use the expected value if the tornado is on)
        self.development_ftes = gen_t(product_variables_ranges.development_ftes, tornado, Tornado.Dev_Ftes)
        self.years_before_development = gen_t(product_variables_ranges.years_before_development, tornado, Tornado.OFF)
        self.years_of_development_growth = gen_t(product_variables_ranges.years_of_development_growth, tornado, Tornado.OFF)
        self.years_of_development_maturity = gen_t(product_variables_ranges.years_of_development_maturity, tornado, Tornado.Dev_Years)
        self.years_of_development_decline = gen_t(product_variables_ranges.years_of_development_decline, tornado, Tornado.OFF)
        self.maintenance_ftes = gen_t(product_variables_ranges.maintenance_ftes, tornado, Tornado.Maint_Ftes)
        self.years_before_sales = gen_t(product_variables_ranges.years_before_sales, tornado, Tornado.OFF)
        self.years_of_sales_growth = gen_t(product_variables_ranges.years_of_sales_growth, tornado, Tornado.OFF)
        self.years_of_sales_maturity = gen_t(product_variables_ranges.years_of_sales_maturity, tornado, Tornado.Sales_Years)
        self.years_of_sales_decline = gen_t(product_variables_ranges.years_of_sales_decline, tornado, Tornado.OFF)
        self.unit_cost_pv = gen_t(product_variables_ranges.unit_cost_pv, tornado, Tornado.Unit_Cost)
        self.unit_price_cost_factor = gen_t(product_variables_ranges.unit_price_cost_factor, tornado, Tornado.Margin)

        # compute the unit price
        self.unit_price_pv = self.unit_cost_pv * self.unit_price_cost_factor

        # interpoloate the yearly unit sales range as a function of the unit price
        price_range = np.array([product_variables_ranges.lowest_price(), product_variables_ranges.highest_price()])
        yearly_unit_sales_range = [0, 0, 0]
        for i in range(3):
            sales_range_i = np.array([product_variables_ranges.yearly_unit_sales_lowest_price[i], product_variables_ranges.yearly_unit_sales_highest_price[i]])
            yearly_unit_sales_range[i] = np.interp(self.unit_price_pv, price_range, sales_range_i)
        
        # convert the sales range to actual value using a triangular distribution
        self.yearly_unit_sales = gen_t(yearly_unit_sales_range, tornado, Tornado.Yearly_Sales)

    def total_remaining_years(self):
        return self.years_before_development + self.years_of_development_growth + self.years_of_development_maturity + self.years_of_development_decline + self.years_before_sales + self.years_of_sales_growth + self.years_of_sales_maturity + self.years_of_sales_decline
    
    def development_ftes_this_month(self, month):
        if month < self.years_before_development * 12:
            return 0
        month -= self.years_before_development * 12
        if month < self.years_of_development_growth * 12:
            return self.development_ftes * month / (self.years_of_development_growth * 12)
        month -= self.years_of_development_growth * 12
        if month < self.years_of_development_maturity * 12:
            return self.development_ftes
        month -= self.years_of_development_maturity * 12
        if month < self.years_of_development_decline * 12:
            return self.development_ftes * (1 - month / (self.years_of_development_decline * 12))
        return self.maintenance_ftes
    
    def sales_this_month(self, month):
        month -= self.years_before_development * 12
        month -= self.years_of_development_growth * 12
        month -= self.years_of_development_maturity * 12
        month -= self.years_of_development_decline * 12
        if month < self.years_before_sales * 12:
            return 0
        month -= self.years_before_sales * 12
        if month < self.years_of_sales_growth * 12:
            return self.yearly_unit_sales * month / (self.years_of_sales_growth * 12) / 12
        month -= self.years_of_sales_growth * 12
        if month < self.years_of_sales_maturity * 12:
            return self.yearly_unit_sales / 12
        month -= self.years_of_sales_maturity * 12
        if month < self.years_of_sales_decline * 12:
            return self.yearly_unit_sales * (1 - month / (self.years_of_sales_decline * 12)) / 12
        return 0

class NpvCalculationResult:
    def __init__(self):
        self.development_cost = 0
        self.sales = 0
        self.cost_of_goods = 0
        self.sga = 0
        self.unit_sales = 0

    def npv(self):
        return self.sales - self.cost_of_goods - self.sga - self.development_cost

    def roi(self):
        return self.npv() / self.development_cost

    def annualized_roi(self, years):
        return (1 + self.roi()) ** (1 / years) - 1

def calculate_npv(product_variables_snapshot, company_constants):

    # this is what we will calculate and return 
    result = NpvCalculationResult()

    # phase: development maturity
    for month in range(round(product_variables_snapshot.total_remaining_years() * 12)):
    
        # compute the development_ftes for this month
        development_ftes = product_variables_snapshot.development_ftes_this_month(month)

        # compute the unit sales for this month
        unit_sales = product_variables_snapshot.sales_this_month(month)

        # compute the future value of the cost of development, unit cost, and unit price for this month
        monthly_development_cost_fte_fv = fv(company_constants.yearly_development_fte_cost_pv / 12, company_constants.development_cost_trend / 12, month)
        unit_cost_fv = fv(product_variables_snapshot.unit_cost_pv, company_constants.unit_cost_trend / 12, month)
        unit_price_fv = fv(product_variables_snapshot.unit_price_pv, company_constants.unit_cost_trend * product_variables_snapshot.unit_price_cost_factor / 12, month)

        # compute the selling, general, and administrative expenses per unit
        sga_fv = unit_price_fv * company_constants.sga_percentage

        # add the cost of development in present value terms
        result.development_cost += pv(development_ftes * monthly_development_cost_fte_fv, company_constants.market_return / 12, month)
        result.unit_sales += unit_sales
        result.sales += pv(unit_sales * unit_price_fv, company_constants.market_return / 12, month)
        result.cost_of_goods += pv(unit_sales * unit_cost_fv, company_constants.market_return / 12, month)
        result.sga += pv(unit_sales * sga_fv, company_constants.market_return / 12, month)

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
    development_costs.append(result.development_cost/1000000)
    annualized_rois.append(result.annualized_roi(product_variables_snapshot.total_remaining_years())*100)
    unit_sales.append(result.unit_sales)
    sales.append(result.sales/1000000)
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