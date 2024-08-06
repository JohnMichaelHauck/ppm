from enum import Enum
import os
import numpy as np # linear algebra library
import matplotlib.pyplot as plt # plotting library
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
import tempfile
import sys

# Present Value (PV) function
def pv(future_value, rate, periods):
    return future_value / (1 + rate) ** periods

# Future Value (FV) function
def fv(present_value, rate, periods):
    return present_value * (1 + rate) ** periods

# Company Constants (user input)
class CompanyConstants:
    def __init__(self,
                 market_return = 0.03,
                 yearly_development_fte_cost_pv = 50000,
                 inflation = 0.03,
                 sga_percentage = 0.30):
        
        # what we would expect to earn on an investment in a financial market with a similar risk
        self.market_return = market_return
        
        # how much it costs per person to run a product development team (in present dollars)
        self.yearly_development_fte_cost_pv = yearly_development_fte_cost_pv
        
        # how much costs increase each year
        self.inflation = inflation

        # the percentage of the selling price that is allocated to cover selling, general, and administrative expenses        
        self.sga_percentage = sga_percentage

# Product Variables Ranges (user input)
class ProductVariablesRanges:
    def __init__(self,
                 years_before_development = 1.5,
                 years_of_development_growth = 0,
                 years_of_development_maturity = [3, 4, 5],
                 years_of_development_decline = 0,
                 years_before_sales = 0,
                 years_of_sales_growth = 0,
                 years_of_sales_maturity = [8, 10, 12],
                 years_of_sales_decline = 0,
                 development_ftes = [4, 5, 6],
                 maintenance_ftes = [0, 0.5, 1],
                 unit_cost_pv=[8000, 10000, 12000],
                 unit_price_cost_factor = [1.9, 2.0, 2.1],
                 yearly_unit_sales_lowest_price = [110, 120, 130],
                 yearly_unit_sales_highest_price = [70, 80, 90]):
        
        # development years profile
        self.years_before_development = years_before_development
        self.years_of_development_growth = years_of_development_growth
        self.years_of_development_maturity = years_of_development_maturity
        self.years_of_development_decline = years_of_development_decline

        # sales years profile
        self.years_before_sales = years_before_sales
        self.years_of_sales_growth = years_of_sales_growth
        self.years_of_sales_maturity = years_of_sales_maturity
        self.years_of_sales_decline = years_of_sales_decline
        
        # the number of people (full time equivalents) on the development team
        self.development_ftes = development_ftes

        # the number of people that need to keep working on the product after development
        self.maintenance_ftes = maintenance_ftes
        
        # the cost to manufacture one unit of the product (in present dollars)
        self.unit_cost_pv = unit_cost_pv
        
        # the selling price cost factors to compute the price of the product (in present dollars)
        self.unit_price_cost_factor = unit_price_cost_factor

        # the number of units that are expected to be sold per year
        self.yearly_unit_sales_lowest_price = yearly_unit_sales_lowest_price
        self.yearly_unit_sales_highest_price = yearly_unit_sales_highest_price

    def lowest_price(self):
        return self.unit_cost_pv[0] * self.unit_price_cost_factor[0]
    
    def highest_price(self):
        return self.unit_cost_pv[2] * self.unit_price_cost_factor[2]

# Used to lock in all but one variable when computing a tornado sensitivity analysis
class Tornado(Enum):
    OFF = 0
    Dev_Ftes = 1
    Dev_Years = 2
    Maint_Ftes = 3
    Sales_Years = 4
    Unit_Cost = 5
    Margin = 6
    Yearly_Sales = 7

# Return a single random number, given a low, likely, and high range, using a triangular distribution
# Just return the likely number in special situations (e.g., the range is invalid or a tornado sensitivity analysis is being performed with a different variable)
def triangle(a, tornado = Tornado.OFF, key = Tornado.OFF):

    # if a is a single number, return it
    if isinstance(a, (int, float)):
        return a

    # if the range is invalid, return the likely (middle) value
    if(a[0] > a[1] or a[1] > a[2] or a[0] >= a[2]):
        return a[1]
    
    # if the tornado sensitivity analysis is being performed and this variable is not the one bing varied, then return the likely (middle) value
    if (tornado != Tornado.OFF and key != tornado):
        return a[1]
    
    # return a single random number, given a low, likely, and high range, using a triangular distribution
    return np.random.triangular(a[0], a[1], a[2])

# Create a snapshot of the product variables with random values
class ProductVariablesSnapshot:
    def __init__(self, product_variables_ranges, tornado):
        
        # convert various ranges to actual values using a triangular distribution (or use the likely value if a tornado sensitivity analysis is being performed)
        self.development_ftes = triangle(product_variables_ranges.development_ftes, tornado, Tornado.Dev_Ftes)
        self.years_before_development = triangle(product_variables_ranges.years_before_development, tornado, Tornado.OFF)
        self.years_of_development_growth = triangle(product_variables_ranges.years_of_development_growth, tornado, Tornado.OFF)
        self.years_of_development_maturity = triangle(product_variables_ranges.years_of_development_maturity, tornado, Tornado.Dev_Years)
        self.years_of_development_decline = triangle(product_variables_ranges.years_of_development_decline, tornado, Tornado.OFF)
        self.maintenance_ftes = triangle(product_variables_ranges.maintenance_ftes, tornado, Tornado.Maint_Ftes)
        self.years_before_sales = triangle(product_variables_ranges.years_before_sales, tornado, Tornado.OFF)
        self.years_of_sales_growth = triangle(product_variables_ranges.years_of_sales_growth, tornado, Tornado.OFF)
        self.years_of_sales_maturity = triangle(product_variables_ranges.years_of_sales_maturity, tornado, Tornado.Sales_Years)
        self.years_of_sales_decline = triangle(product_variables_ranges.years_of_sales_decline, tornado, Tornado.OFF)
        self.unit_cost_pv = triangle(product_variables_ranges.unit_cost_pv, tornado, Tornado.Unit_Cost)
        self.unit_price_cost_factor = triangle(product_variables_ranges.unit_price_cost_factor, tornado, Tornado.Margin)

        # some product variables are dependent on others, so we need to compute them

        # compute the unit price
        self.unit_price_pv = self.unit_cost_pv * self.unit_price_cost_factor

        # interpoloate the yearly unit sales range as a function of the unit price
        price_range = np.array([product_variables_ranges.lowest_price(), product_variables_ranges.highest_price()])
        yearly_unit_sales_range = [0, 0, 0]
        for i in range(3):
            sales_range_i = np.array([product_variables_ranges.yearly_unit_sales_lowest_price[i], product_variables_ranges.yearly_unit_sales_highest_price[i]])
            yearly_unit_sales_range[i] = np.interp(self.unit_price_pv, price_range, sales_range_i)
        
        # convert the sales range to an actual value using a triangular distribution
        self.yearly_unit_sales = triangle(yearly_unit_sales_range, tornado, Tornado.Yearly_Sales)

        # precalculate the total remaining years
        self.total_remaining_years = self.years_before_development + self.years_of_development_growth + self.years_of_development_maturity + self.years_of_development_decline + self.years_before_sales + self.years_of_sales_growth + self.years_of_sales_maturity + self.years_of_sales_decline

    # compute the development full time equivalents for a given month
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
    
    # compute the unit sales for a given month
    def unit_sales_this_month(self, month):
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

# The result of a single NPV calculation
class NpvCalculationResult:
    def __init__(self):
        self.development_cost = 0
        self.sales = 0
        self.cost_of_goods = 0
        self.sga = 0
        self.unit_sales = 0
        self.total_remaining_years = 0

    def npv(self):
        return self.sales - self.cost_of_goods - self.sga - self.development_cost

    def roi(self):
        return self.npv() / self.development_cost

    def annualized_roi(self, years):
        return (1 + self.roi()) ** (1 / years) - 1

# Calculate the NPV of a product
def calculate_npv(product_variables_snapshot, company_constants):

    # this is what we will calculate and return 
    result = NpvCalculationResult()

    # loop through all the months
    for month in range(round(product_variables_snapshot.years_before_development * 12), round(product_variables_snapshot.total_remaining_years * 12)):
    
        # compute the development_ftes for this month
        development_ftes = product_variables_snapshot.development_ftes_this_month(month)

        # compute the unit sales for this month
        unit_sales = product_variables_snapshot.unit_sales_this_month(month)

        # compute the future value of the cost of development, unit cost, and unit price for this month
        monthly_development_cost_fte_fv = fv(company_constants.yearly_development_fte_cost_pv / 12, company_constants.inflation / 12, month)
        unit_cost_fv = fv(product_variables_snapshot.unit_cost_pv, company_constants.inflation / 12, month)
        unit_price_fv = fv(product_variables_snapshot.unit_price_pv, company_constants.inflation / 12, month)

        # compute the selling, general, and administrative expenses per unit
        sga_fv = unit_price_fv * company_constants.sga_percentage

        # add the cost of development in present value terms
        result.development_cost += pv(development_ftes * monthly_development_cost_fte_fv, company_constants.market_return / 12, month)
        result.unit_sales += unit_sales
        result.sales += pv(unit_sales * unit_price_fv, company_constants.market_return / 12, month)
        result.cost_of_goods += pv(unit_sales * unit_cost_fv, company_constants.market_return / 12, month)
        result.sga += pv(unit_sales * sga_fv, company_constants.market_return / 12, month)

    # handy for the result
    result.total_remaining_years = product_variables_snapshot.total_remaining_years

    return result

# Track all the results of multiple calculations
class SimulationTracker:
    def __init__(self):
        self.npvs_millions = []
        self.development_costs_millions = []
        self.annualized_rois_percentage = []
        self.unit_sales_thousands = []
        self.sales_millions = []
        self.years = []
    
    def add(self, result):
        self.npvs_millions.append(result.npv() / 1000000)
        self.development_costs_millions.append(result.development_cost / 1000000)
        self.annualized_rois_percentage.append(result.annualized_roi(result.total_remaining_years) * 100)
        self.unit_sales_thousands.append(result.unit_sales / 1000)
        self.sales_millions.append(result.sales / 1000000)
        self.years.append(result.total_remaining_years)

class TornadoTracker:
    def __init__(self, tornado, name):
        self.tornado = tornado
        self.name = name
        self.min_value = float('inf')
        self.max_value = float('-inf')

    def add(self, value):
        if value < self.min_value:
            self.min_value = value
        if value > self.max_value:
            self.max_value = value
    
    def range(self):
        return self.max_value - self.min_value

class MonteCarloAnalyzer:
    def __init__(self, company_constants, product_variables_ranges):
        self.company_constants = company_constants
        self.product_variables_ranges = product_variables_ranges
        self.simulation_tracker = SimulationTracker()
        self.tornado_trackers = []
        self.tornado_trackers.append(TornadoTracker(Tornado.Dev_Ftes, 'Dev FTEs'))
        self.tornado_trackers.append(TornadoTracker(Tornado.Dev_Years, 'Dev Years'))
        self.tornado_trackers.append(TornadoTracker(Tornado.Maint_Ftes, 'Maint FTEs'))
        self.tornado_trackers.append(TornadoTracker(Tornado.Sales_Years, 'Sales Years'))
        self.tornado_trackers.append(TornadoTracker(Tornado.Unit_Cost, 'Unit Cost'))
        self.tornado_trackers.append(TornadoTracker(Tornado.Margin, 'Margin'))
        self.tornado_trackers.append(TornadoTracker(Tornado.Yearly_Sales, 'Yearly Sales'))

    def analyze(self):
        # compute the monte carlo analysis
        for i in range(2000):
            product_variables_snapshot = ProductVariablesSnapshot(self.product_variables_ranges, Tornado.OFF)
            result = calculate_npv(product_variables_snapshot, self.company_constants)
            self.simulation_tracker.add(result)

        # compute the tornado analysis
        for i in range(100):    
            for tornado_tracker in self.tornado_trackers:
                product_variables_snapshot = ProductVariablesSnapshot(self.product_variables_ranges, tornado_tracker.tornado)
                result = calculate_npv(product_variables_snapshot, self.company_constants)
                tornado_tracker.add(result.npv() / 1000000)

        # Sort the tornado trackers by range
        self.tornado_trackers.sort(key=lambda x: x.range())
    
    # create a histogram
    def create_histogram(self, data, bins, xlabel, subplot_position, rows, cols):
        plt.subplot(rows, cols, subplot_position)
        plt.hist(data, bins=bins, edgecolor='black')
        plt.yticks([])
        plt.xlabel(xlabel, fontsize=10)

    # create a tornado plot
    def create_tornado_plot(self, names, ranges, min_values, xlabel, subplot_position, rows, cols):
        plt.subplot(rows, cols, subplot_position)
        plt.barh(names, ranges, left=min_values)
        plt.xlabel(xlabel)

    # plot the results
    def plot(self, file_path):
        rows = 2
        cols = 3
        plt.figure(figsize=(10, 5))

        self.create_histogram(self.simulation_tracker.unit_sales_thousands, 30, 'Sales (units/1000)', 1, rows, cols)
        self.create_histogram(self.simulation_tracker.sales_millions, 30, 'Sales ($ millions)', 2, rows, cols)
        self.create_histogram(self.simulation_tracker.development_costs_millions, 30, 'Development ($ millions)', 3, rows, cols)
        self.create_histogram(self.simulation_tracker.npvs_millions, 30, 'NPV ($ millions)', 4, rows, cols)
        self.create_histogram(self.simulation_tracker.annualized_rois_percentage, 30, 'Annualized ROI (%)', 5, rows, cols)
        # self.create_histogram(self.years, 30, 'Product Years', 6, rows, cols)

        tornado_names = [tornado_tracker.name for tornado_tracker in self.tornado_trackers]
        tornado_ranges = [tornado_tracker.range() for tornado_tracker in self.tornado_trackers]
        tornado_min_values = [tornado_tracker.min_value for tornado_tracker in self.tornado_trackers]
        self.create_tornado_plot(tornado_names, tornado_ranges, tornado_min_values, 'NPV Sensitivity ($ millions)', 6, rows, cols)

        plt.tight_layout()
        if( file_path != ""):
            plt.savefig(file_path)
        else:
            plt.show()
        plt.close()

def read_excel_data(file_path):

    # Load the workbook and select the sheets
    workbook = load_workbook(file_path)
    company_constants_sheet = workbook['Company Constants']
    product_variables_sheet = workbook['Product Variables']

    # Extract values from the DataFrame
    market_return = company_constants_sheet.cell(row=2, column=2).value
    yearly_development_fte_cost_pv = company_constants_sheet.cell(row=3, column=2).value
    inflation = company_constants_sheet.cell(row=4, column=2).value
    sga_percentage = company_constants_sheet.cell(row=5, column=2).value

    # Initialize the CompanyConstants instance
    company_constants = CompanyConstants(market_return, yearly_development_fte_cost_pv, inflation, sga_percentage)

    def convert(sheet, row):
        return [
            sheet.cell(row=row, column=2).value,
            sheet.cell(row=row, column=3).value,
            sheet.cell(row=row, column=4).value
        ]
    
    # Extract values from the DataFrame
    years_before_development = convert(product_variables_sheet, 2)
    years_of_development_growth = convert(product_variables_sheet, 3)
    years_of_development_maturity = convert(product_variables_sheet, 4)
    years_of_development_decline = convert(product_variables_sheet, 5)
    years_before_sales = convert(product_variables_sheet, 6)
    years_of_sales_growth = convert(product_variables_sheet, 7)
    years_of_sales_maturity = convert(product_variables_sheet, 8)
    years_of_sales_decline = convert(product_variables_sheet, 9)
    development_ftes = convert(product_variables_sheet, 10)
    maintenance_ftes = convert(product_variables_sheet, 11)
    unit_cost_pv = convert(product_variables_sheet, 12)
    unit_price_cost_factor = convert(product_variables_sheet, 13)
    yearly_unit_sales_at_15200 = convert(product_variables_sheet, 14)
    yearly_unit_sales_at_25200 = convert(product_variables_sheet, 15)

    # Initialize the ProductVariablesRanges instance
    product_variables_ranges = ProductVariablesRanges(years_before_development, years_of_development_growth, years_of_development_maturity, years_of_development_decline, years_before_sales, years_of_sales_growth, years_of_sales_maturity, years_of_sales_decline, development_ftes, maintenance_ftes, unit_cost_pv, unit_price_cost_factor, yearly_unit_sales_at_15200, yearly_unit_sales_at_25200)

    return company_constants, product_variables_ranges

def insert_plot_into_excel(excel_file_path_in, excel_file_path_out, image_path):
    # Load the workbook and select the sheet
    workbook = load_workbook(excel_file_path_in)
    sheet = workbook['Product Variables']

    # Load the image
    img = Image(image_path)
    
    # Insert the image into the sheet at the specified cell
    sheet.add_image(img, 'A16')

    # Save the workbook to the new file
    workbook.save(excel_file_path_out)

# Check if there are any command line arguments
if len(sys.argv) == 2:
    excel_file_path = sys.argv[1]
    plot_file_path = os.path.join(tempfile.gettempdir(), 'ppm.png')
    company_constants, product_variables_ranges = read_excel_data(excel_file_path)
else:
    excel_file_path = ""
    plot_file_path = ""
    company_constants = CompanyConstants()
    product_variables_ranges = ProductVariablesRanges()

# Run the Monte Carlo simulation
monte_carlo = MonteCarloAnalyzer(company_constants, product_variables_ranges)
monte_carlo.analyze()
monte_carlo.plot(plot_file_path)

# Save the plot
if len(sys.argv) == 2:
    insert_plot_into_excel(excel_file_path, excel_file_path, plot_file_path)