import os
import tempfile
import sys
from enum import Enum
import numpy as np # linear algebra library
import matplotlib.pyplot as plt # plotting library
from openpyxl import load_workbook
from openpyxl.drawing.image import Image

# Present Value (PV) function
def pv(future_value, rate, periods):
    return future_value / (1 + rate) ** periods

# Future Value (FV) function
def fv(present_value, rate, periods):
    return present_value * (1 + rate) ** periods

# Add a value to a given index in the array, growing the array if needed
def add_value_to_index(array, index, value):
    # Extend the array if the index is out of bounds
    if index >= len(array):
        array.extend([0] * (index - len(array) + 1))
    
    # Add the value to the specified index
    array[index] += value

# Company Constants (user input)
class CompanyConstants:
    def __init__(self,
                 market_return = 0.03,
                 development_cost_trend = 0.03,
                 product_cost_trend = 0.03,
                 product_price_trend = 0.03,
                 yearly_development_fte_cost_pv = 17000,
                 maximum_development_ftes = 6):
        
        # what we would expect to earn on an investment in a financial market with a similar risk
        self.market_return = market_return
        
        # how much things increase each year
        self.development_cost_trend = development_cost_trend
        self.product_cost_trend = product_cost_trend
        self.product_price_trend = product_price_trend

        # how much it costs per person to run a product development team (in present dollars)
        self.yearly_development_fte_cost_pv = yearly_development_fte_cost_pv

        # staff size limit
        self.maximum_development_ftes = maximum_development_ftes

# Return the value of a range, or a single value if it is not a range
def safe_index(range, i):
    if isinstance(range, (int, float)):
        return range
    return range[i]

# Relationship between margin and cost factor
def cost_factor(margin):
    return 1 / (1 - margin)

# Product Variables Ranges (user input)
class ProductVariablesRanges:
    def __init__(self,
                 years_of_development_growth = 0,
                 years_of_development_maturity = 2,
                 years_of_development_decline = 0,
                 years_of_kumbia = 0,
                 years_of_sales_growth = 0,
                 years_of_sales_maturity = 12,
                 years_of_sales_decline = 0,
                 development_ftes = 5,
                 maintenance_ftes = 0,
                 years_of_maintenance = 3,
                 unit_cost_pv = 21300,
                 unit_margin = 0.677272727,
                 sga_factor = 0.31,
                 yearly_unit_sales_lowest_price = 11,
                 yearly_unit_sales_highest_price = 11):
        
        # development years profile
        self.years_mix_delay = 0
        self.years_of_development_growth = years_of_development_growth
        self.years_of_development_maturity = years_of_development_maturity
        self.years_of_development_decline = years_of_development_decline

        # sales years profile
        self.years_of_kumbia = years_of_kumbia
        self.years_of_sales_growth = years_of_sales_growth
        self.years_of_sales_maturity = years_of_sales_maturity
        self.years_of_sales_decline = years_of_sales_decline
        
        # the number of people (full time equivalents) on the development team
        self.development_ftes = development_ftes

        # the people that need to keep working on the product after development
        self.maintenance_ftes = maintenance_ftes
        self.years_of_maintenance = years_of_maintenance
        
        # the cost to manufacture one unit of the product (in present dollars)
        self.unit_cost_pv = unit_cost_pv
        
        # the selling price margin
        self.unit_margin = unit_margin

        # the percentage of the selling price that is allocated to cover selling, general, and administrative expenses        
        self.sga_factor = sga_factor

        # the number of units that are expected to be sold per year
        self.yearly_unit_sales_lowest_price = yearly_unit_sales_lowest_price
        self.yearly_unit_sales_highest_price = yearly_unit_sales_highest_price

    def lowest_price(self):
        return safe_index(self.unit_cost_pv, 0) * cost_factor(safe_index(self.unit_margin, 0))
    
    def highest_price(self):
        return safe_index(self.unit_cost_pv, 2) * cost_factor(safe_index(self.unit_margin, 2))
    
    @classmethod
    def market_of(
        cls,
        existing_instance,
        unit_margin,
        sga_factor,
        yearly_unit_sales_lowest_price,
        yearly_unit_sales_highest_price):

        return cls(
            years_of_development_growth = 0,
            years_of_development_maturity = 0,
            years_of_development_decline = 0,
            years_of_kumbia = existing_instance.years_of_kumbia,
            years_of_sales_growth = existing_instance.years_of_sales_growth,
            years_of_sales_maturity = existing_instance.years_of_sales_maturity,
            years_of_sales_decline = existing_instance.years_of_sales_decline,
            development_ftes = 0,
            maintenance_ftes = 0,
            years_of_maintenance = 0,
            unit_cost_pv = existing_instance.unit_cost_pv,
            unit_margin = unit_margin,
            sga_factor = sga_factor,
            yearly_unit_sales_lowest_price = yearly_unit_sales_lowest_price,
            yearly_unit_sales_highest_price = yearly_unit_sales_highest_price)
    
# Return a single random number, given a low, expected, and high range, using a triangular distribution
# Just return the expected number if requested, or if the range is invalid
def triangle(a, just_expected = False):

    # if a is a single number, return it
    if isinstance(a, (int, float)):
        return a

    # if the range is invalid, return the likely (middle) value
    if(a[0] > a[1] or a[1] > a[2] or a[0] >= a[2]):
        return a[1]
    
    # if requested, just return the likely (middle) value
    if (just_expected):
        return a[1]
    
    # return a random number, given a low, likely, and high range, using a triangular distribution
    return np.random.triangular(a[0], a[1], a[2])

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

# Create a snapshot of the product variables with random values
class ProductVariablesSnapshot:
    def __init__(self, product_variables_ranges, tornado = Tornado.OFF):
        
        # convert various ranges to actual values using a triangular distribution (or use the likely value if a tornado sensitivity analysis is being performed)
        self.years_mix_delay = 0
        self.development_ftes = triangle(product_variables_ranges.development_ftes, tornado != Tornado.OFF and tornado != Tornado.Dev_Ftes)
        self.years_of_development_growth = triangle(product_variables_ranges.years_of_development_growth)
        self.years_of_development_maturity = triangle(product_variables_ranges.years_of_development_maturity, tornado != Tornado.OFF and tornado != Tornado.Dev_Years)
        self.years_of_development_decline = triangle(product_variables_ranges.years_of_development_decline)
        self.maintenance_ftes = triangle(product_variables_ranges.maintenance_ftes, tornado != Tornado.OFF and tornado != Tornado.Maint_Ftes)
        self.years_of_maintenance = triangle(product_variables_ranges.years_of_maintenance)
        self.years_of_kumbia = triangle(product_variables_ranges.years_of_kumbia)
        self.years_of_sales_growth = triangle(product_variables_ranges.years_of_sales_growth)
        self.years_of_sales_maturity = triangle(product_variables_ranges.years_of_sales_maturity, tornado != Tornado.OFF and tornado != Tornado.Sales_Years)
        self.years_of_sales_decline = triangle(product_variables_ranges.years_of_sales_decline)
        self.unit_cost_pv = triangle(product_variables_ranges.unit_cost_pv, tornado != Tornado.OFF and tornado != Tornado.Unit_Cost)
        self.unit_margin = triangle(product_variables_ranges.unit_margin, tornado != Tornado.OFF and tornado != Tornado.Margin)
        self.sga_factor = triangle(product_variables_ranges.sga_factor)

        # some product variables are dependent on others, so we need to compute them

        # compute the unit price
        self.unit_price_pv = self.unit_cost_pv * cost_factor(self.unit_margin)

        # interpolate the yearly unit sales range as a function of the unit price
        price_range = np.array([product_variables_ranges.lowest_price(), product_variables_ranges.highest_price()])
        yearly_unit_sales_range = [0, 0, 0]
        for i in range(3):
            sales_range_i = np.array([safe_index(product_variables_ranges.yearly_unit_sales_lowest_price, i), safe_index(product_variables_ranges.yearly_unit_sales_highest_price, i)])
            yearly_unit_sales_range[i] = np.interp(self.unit_price_pv, price_range, sales_range_i)
        
        # convert the sales range to an actual value using a triangular distribution
        self.yearly_unit_sales = triangle(yearly_unit_sales_range, tornado != Tornado.OFF and tornado != Tornado.Yearly_Sales)

        # precalculate the total remaining years
        self.years_before_sales = self.years_of_development_growth + self.years_of_development_maturity + self.years_of_development_decline + self.years_of_kumbia
        self.total_years = self.years_before_sales + self.years_of_sales_growth + self.years_of_sales_maturity + self.years_of_sales_decline

        # precalculate the development full time equivalents for each month
        self.ftes_by_month = []
        for month in range (round(self.years_of_development_growth * 12)):
            self.ftes_by_month.append(self.development_ftes * month / (self.years_of_development_growth * 12))
        for month in range (round(self.years_of_development_maturity * 12)):
            self.ftes_by_month.append(self.development_ftes)
        for month in range (round(self.years_of_development_decline * 12)):
            self.ftes_by_month.append(self.development_ftes * (1 - month / (self.years_of_development_decline * 12)))
        for month in range (round(self.years_of_maintenance * 12)):
            self.ftes_by_month.append(self.maintenance_ftes)

        # precalculate the unit sales for a given month
        self.unit_sales_by_month = []
        for month in range (round(self.years_of_sales_growth * 12)):
            self.unit_sales_by_month.append(self.yearly_unit_sales * month / (self.years_of_sales_growth * 12) / 12)
        for month in range (round(self.years_of_sales_maturity * 12)):
            self.unit_sales_by_month.append(self.yearly_unit_sales / 12)
        for month in range (round(self.years_of_sales_decline * 12)):
            self.unit_sales_by_month.append(self.yearly_unit_sales * (1 - month / (self.years_of_sales_decline * 12)) / 12)

    # compute the development full time equivalents for a given month
    def development_ftes_this_mix_month(self, month):
        month -= self.years_mix_delay * 12
        month = round(month)
        return self.ftes_by_month[month] if 0 <= month < len(self.ftes_by_month) else 0
    
    # compute the unit sales for a given month
    def unit_sales_this_mix_month(self, month):
        month -= self.years_mix_delay * 12
        month -= self.years_before_sales * 12
        month = round(month)
        return self.unit_sales_by_month[month] if 0 <= month < len(self.unit_sales_by_month) else 0

# Create a snapshot of the mix of product variables with random values
class MixVariablesSnapshot:
    def __init__(self, mix_variables_ranges, tornado = Tornado.OFF):
        self.mix_variables_ranges = mix_variables_ranges
        self.mix_variables_snapshots = []
        for product_variables_ranges in mix_variables_ranges:
            self.mix_variables_snapshots.append(ProductVariablesSnapshot(product_variables_ranges, tornado))

# The result of a single NPV calculation
class NpvCalculationResult:
    def __init__(self):
        self.development_cost = 0
        self.sales = 0
        self.cost_of_goods = 0
        self.sga = 0
        self.unit_sales = 0
        self.ftes_by_month = []
        self.sales_by_month = []

    def npv(self):
        return self.sales - self.cost_of_goods - self.sga - self.development_cost

    def ros(self):
        if( self.sales == 0):
            return 0
        return self.npv() / self.sales

    def roi(self):
        if( self.development_cost == 0):
            return 0
        return self.npv() / self.development_cost

    def annualized_roi(self, years):
        if( years == 0):
            return 0
        return (1 + self.roi()) ** (1 / years) - 1
    
    def record_ftes(self, month, ftes):
        add_value_to_index(self.ftes_by_month, month, ftes)
    
    def record_sales(self, month, sales):
        add_value_to_index(self.sales_by_month, month, sales)
    
    def add(self, result):
        self.development_cost += result.development_cost
        self.sales += result.sales
        self.cost_of_goods += result.cost_of_goods
        self.sga += result.sga
        self.unit_sales += result.unit_sales
        for month in range(len(result.ftes_by_month)):
            add_value_to_index(self.ftes_by_month, month, result.ftes_by_month[month])
        for month in range(len(result.sales_by_month)):
            add_value_to_index(self.sales_by_month, month, result.sales_by_month[month])

# Calculate the NPV of a product
def calculate_product_npv(product_variables_snapshot, company_constants):

    # this is what we will calculate and return 
    product_result = NpvCalculationResult()

    # loop through all the months
    for month in range(round(product_variables_snapshot.total_years * 12) + 1):
        mix_month = month + round(product_variables_snapshot.years_mix_delay * 12)
    
        # compute the development_ftes for this month
        development_ftes = product_variables_snapshot.development_ftes_this_mix_month(mix_month)

        # compute the unit sales for this month
        unit_sales = product_variables_snapshot.unit_sales_this_mix_month(mix_month)

        # compute the future value of the cost of development, unit cost, unit price, and sg&a for this month
        monthly_development_cost_fte_fv = fv(company_constants.yearly_development_fte_cost_pv / 12, company_constants.development_cost_trend / 12, mix_month)
        unit_cost_fv = fv(product_variables_snapshot.unit_cost_pv, company_constants.product_cost_trend / 12, mix_month)
        unit_price_fv = fv(product_variables_snapshot.unit_price_pv, company_constants.product_price_trend / 12, mix_month)
        sga_variable_fv = unit_price_fv * product_variables_snapshot.sga_factor

        # return everything to present value
        development_cost_pv = pv(development_ftes * monthly_development_cost_fte_fv, company_constants.market_return / 12, mix_month)
        sales_pv = pv(unit_sales * unit_price_fv, company_constants.market_return / 12, mix_month)
        cost_of_goods_pv = pv(unit_sales * unit_cost_fv, company_constants.market_return / 12, mix_month)
        sga_pv = pv(unit_sales * sga_variable_fv, company_constants.market_return / 12, mix_month)

        # add the results for this month to the total
        product_result.development_cost += development_cost_pv
        product_result.sales += sales_pv
        product_result.cost_of_goods += cost_of_goods_pv
        product_result.sga += sga_pv
        product_result.unit_sales += unit_sales
        product_result.record_ftes(mix_month, development_ftes)
        product_result.record_sales(mix_month, sales_pv)

    return product_result

# Calculate the years mix delay based on the maximum development FTEs
def calculate_years_mix_delay(maximum_development_ftes, allocated_ftes_by_month, new_ftes_by_month):
    months_mix_delay = 0
    maximum_development_ftes = max(maximum_development_ftes, max(new_ftes_by_month))
    allocated_ftes_by_month.extend([0] * len(new_ftes_by_month))
    while(True):
        overallocated = False
        for month in range(len(new_ftes_by_month)):
            if allocated_ftes_by_month[month + months_mix_delay] + new_ftes_by_month[month] > maximum_development_ftes:
                overallocated = True
                break
        if not overallocated:
            return months_mix_delay / 12
        months_mix_delay += 1

# Calculate the NPV of a product mix
def calculate_mix_npv(mix_variables_snapshot, company_constants):
    mix_result = NpvCalculationResult()
    for product_variables_snapshot in mix_variables_snapshot.mix_variables_snapshots:
        product_variables_snapshot.years_mix_delay = calculate_years_mix_delay(company_constants.maximum_development_ftes, mix_result.ftes_by_month, product_variables_snapshot.ftes_by_month)
        product_result = calculate_product_npv(product_variables_snapshot, company_constants)
        mix_result.add(product_result)
    return mix_result

# Track all the results of multiple calculations
class SimulationTracker:
    def __init__(self):
        self.npvs_millions = []
        self.development_costs_millions = []
        self.unit_sales = []
        self.sales_millions = []
        self.ros = []
        self.roi = []
        self.ftes_by_month = []
        self.sales_by_month = []
    
    def add(self, result):
        self.npvs_millions.append(result.npv() / 1000000)
        self.development_costs_millions.append(result.development_cost / 1000000)
        self.unit_sales.append(result.unit_sales)
        self.sales_millions.append(result.sales / 1000000)
        self.ros.append(result.ros() * 100)
        self.roi.append(result.roi() * 100)
        for month in range(len(result.ftes_by_month)):
            add_value_to_index(self.ftes_by_month, month, result.ftes_by_month[month])
        for month in range(len(result.sales_by_month)):
            add_value_to_index(self.sales_by_month, month, result.sales_by_month[month])

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
    def __init__(self, company_constants, mix_variables_ranges):
        self.company_constants = company_constants
        self.mix_variables_ranges = mix_variables_ranges
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
        simulations = 4000
        for i in range(simulations):
            mix_variables_snapshot = MixVariablesSnapshot(self.mix_variables_ranges)
            result = calculate_mix_npv(mix_variables_snapshot, self.company_constants)
            self.simulation_tracker.add(result)

        # normalize FTEs by dividing each value by the number of simulations
        for month in range(len(self.simulation_tracker.ftes_by_month)):
            self.simulation_tracker.ftes_by_month[month] /= simulations

        # normalize sales by dividing each value by the number of simulations
        for month in range(len(self.simulation_tracker.sales_by_month)):
            self.simulation_tracker.sales_by_month[month] /= simulations

        # compute the tornado analysis
        for i in range(100):    
            for tornado_tracker in self.tornado_trackers:
                mix_variables_snapshot = MixVariablesSnapshot(self.mix_variables_ranges, tornado_tracker.tornado)
                result = calculate_mix_npv(mix_variables_snapshot, self.company_constants)
                tornado_tracker.add(result.npv() / 1000000)

        # Sort the tornado trackers by range
        self.tornado_trackers.sort(key=lambda x: x.range())
    
    # create a histogram
    def create_histogram(self, data, bins, xlabel, subplot_position, rows, cols, color = 'blue'):
        plt.subplot(rows, cols, subplot_position)
        plt.hist(data, bins=bins, edgecolor='black', color=color)
        plt.yticks([])
        plt.xlabel(xlabel)

    # create a tornado plot
    def create_tornado_plot(self, names, ranges, min_values, xlabel, subplot_position, rows, cols):
        plt.subplot(rows, cols, subplot_position)
        plt.barh(names, ranges, left=min_values)
        plt.xlabel(xlabel)
    
    # create a line chart
    def create_line_chart(self, data, xlabel, ylabel, subplot_position, rows, cols, color = 'blue'):
        plt.subplot(rows, cols, subplot_position)
        years = np.arange(len(data)) / 12
        plt.plot(years, data, color=color)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

    # plot the results
    def plot(self, file_path = ""):
        rows = 3
        cols = 3
        plt.figure(figsize=(10, 5))

        self.create_histogram(self.simulation_tracker.unit_sales, 20, 'Sales (units)', 1, rows, cols, 'blue')
        self.create_histogram(self.simulation_tracker.sales_millions, 20, 'Sales ($ millions)', 2, rows, cols, 'red')
        self.create_histogram(self.simulation_tracker.development_costs_millions, 20, 'Development ($ millions)', 3, rows, cols, 'green')
        self.create_histogram(self.simulation_tracker.npvs_millions, 20, 'NPV ($ millions)', 4, rows, cols, 'purple')
        self.create_histogram(self.simulation_tracker.ros, 20, 'ROS (%)', 5, rows, cols, 'orange')
        self.create_histogram(self.simulation_tracker.roi, 20, 'ROI (%)', 6, rows, cols, 'pink')

        tornado_names = [tornado_tracker.name for tornado_tracker in self.tornado_trackers]
        tornado_ranges = [tornado_tracker.range() for tornado_tracker in self.tornado_trackers]
        tornado_min_values = [tornado_tracker.min_value for tornado_tracker in self.tornado_trackers]
        self.create_tornado_plot(tornado_names, tornado_ranges, tornado_min_values, 'NPV Sensitivity ($ millions)', 7, rows, cols)

        self.create_line_chart(self.simulation_tracker.ftes_by_month, 'Years', 'Ftes', 8, rows, cols, 'black')
        self.create_line_chart(self.simulation_tracker.sales_by_month, 'Years', 'Monthly Sales ($)', 9, rows, cols, 'black')

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
    product_price_trend = company_constants_sheet.cell(row=4, column=2).value

    # Initialize the CompanyConstants instance
    company_constants = CompanyConstants(market_return, yearly_development_fte_cost_pv, product_price_trend)

    def convert(sheet, row):
        return [
            sheet.cell(row=row, column=2).value,
            sheet.cell(row=row, column=3).value,
            sheet.cell(row=row, column=4).value
        ]
    
    # Extract values from the DataFrame
    years_of_development_growth = convert(product_variables_sheet, 3)
    years_of_development_maturity = convert(product_variables_sheet, 4)
    years_of_development_decline = convert(product_variables_sheet, 5)
    years_of_kumbia = convert(product_variables_sheet, 6)
    years_of_sales_growth = convert(product_variables_sheet, 7)
    years_of_sales_maturity = convert(product_variables_sheet, 8)
    years_of_sales_decline = convert(product_variables_sheet, 9)
    development_ftes = convert(product_variables_sheet, 10)
    maintenance_ftes = convert(product_variables_sheet, 11)
    unit_cost_pv = convert(product_variables_sheet, 12)
    unit_margin = convert(product_variables_sheet, 13)
    yearly_unit_sales_at_15200 = convert(product_variables_sheet, 14)
    yearly_unit_sales_at_25200 = convert(product_variables_sheet, 15)

    # Initialize the ProductVariablesRanges instance
    product_variables_ranges = ProductVariablesRanges(0, years_of_development_growth, years_of_development_maturity, years_of_development_decline, years_of_kumbia, years_of_sales_growth, years_of_sales_maturity, years_of_sales_decline, development_ftes, maintenance_ftes, unit_cost_pv, unit_margin, yearly_unit_sales_at_15200, yearly_unit_sales_at_25200)

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

    product1 = ProductVariablesRanges(
        years_of_development_growth = 2,
        years_of_development_maturity = [3,4,5],
        years_of_development_decline = 1,
        years_of_kumbia = 0,
        years_of_sales_growth = 2,
        years_of_sales_maturity = [10,11,12],
        years_of_sales_decline = 5,
        development_ftes = [3,4,5],
        maintenance_ftes = [0,0.1,0.25],
        years_of_maintenance = [6,8,10],
        unit_cost_pv = [31000,33700,36000],
        unit_margin = [0.55,0.58,0.60],
        sga_factor = 0.31,
        yearly_unit_sales_lowest_price = [35,40,45],
        yearly_unit_sales_highest_price = [20,25,30])

    product1b = ProductVariablesRanges.market_of(
        product1,
        unit_margin = 0.59,
        sga_factor = 0.31,
        yearly_unit_sales_lowest_price = 15,
        yearly_unit_sales_highest_price = 15)

    product1c = ProductVariablesRanges.market_of(
        product1,
        unit_margin = 0.38,
        sga_factor = 0.31,
        yearly_unit_sales_lowest_price = 6,
        yearly_unit_sales_highest_price = 6)

    mix_variables_ranges = [product1, product1, product1]

# Run the Monte Carlo simulation
monte_carlo = MonteCarloAnalyzer(company_constants, mix_variables_ranges)
monte_carlo.analyze()
monte_carlo.plot(plot_file_path)

# Save the plot
if len(sys.argv) == 2:
    insert_plot_into_excel(excel_file_path, excel_file_path, plot_file_path)