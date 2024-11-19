from tornado_enum import Tornado
import triangle as t
import financial_helpers as fh

class ProductVariablesSnapshot:
    def __init__(self, product_variables_ranges, tornado = Tornado.OFF):
        
        # convert various ranges to actual values using a triangular distribution (or use the likely value if a tornado sensitivity analysis is being performed)
        self.years_mix_delay = 0
        self.name = product_variables_ranges.name
        self.type = product_variables_ranges.type        
        self.development_ftes = t.triangle(product_variables_ranges.development_ftes, tornado != Tornado.OFF and tornado != Tornado.Dev_Ftes)
        self.years_of_development_growth = t.triangle(product_variables_ranges.years_of_development_growth)
        self.years_of_development_maturity = t.triangle(product_variables_ranges.years_of_development_maturity, tornado != Tornado.OFF and tornado != Tornado.Dev_Years)
        self.years_of_development_decline = t.triangle(product_variables_ranges.years_of_development_decline)
        self.maintenance_ftes = t.triangle(product_variables_ranges.maintenance_ftes, tornado != Tornado.OFF and tornado != Tornado.Maint_Ftes)
        self.years_of_maintenance = t.triangle(product_variables_ranges.years_of_maintenance)
        self.years_of_pilot = t.triangle(product_variables_ranges.years_of_pilot)
        self.years_of_sales_growth = t.triangle(product_variables_ranges.years_of_sales_growth)
        self.years_of_sales_maturity = t.triangle(product_variables_ranges.years_of_sales_maturity, tornado != Tornado.OFF and tornado != Tornado.Sales_Years)
        self.years_of_sales_decline = t.triangle(product_variables_ranges.years_of_sales_decline)
        self.unit_cost_pv = t.triangle(product_variables_ranges.unit_cost_pv, tornado != Tornado.OFF and tornado != Tornado.Unit_Cost)
        self.unit_margin = t.triangle(product_variables_ranges.unit_margin, tornado != Tornado.OFF and tornado != Tornado.Margin)
        self.sga_factor = t.triangle(product_variables_ranges.sga_factor)
        self.yearly_unit_sales = t.triangle(product_variables_ranges.yearly_unit_sales, tornado != Tornado.OFF and tornado != Tornado.Yearly_Sales)
        self.yearly_unit_consumable_sales = t.triangle(product_variables_ranges.yearly_unit_consumable_sales)
        self.years_of_consumable_sales = t.triangle(product_variables_ranges.years_of_consumable_sales)
        self.consumable_margin = t.triangle(product_variables_ranges.consumable_margin)

        # compute the unit price
        self.unit_price_pv = self.unit_cost_pv * fh.cost_factor(self.unit_margin)
        
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
        if (len(self.ftes_by_month) == 0):
            self.ftes_by_month.append(0)

        # precalculate the unit sales for a given month
        self.unit_sales_by_month = []
        for month in range (round(self.years_of_sales_growth * 12)):
            self.unit_sales_by_month.append(self.yearly_unit_sales * month / (self.years_of_sales_growth * 12) / 12)
        for month in range (round(self.years_of_sales_maturity * 12)):
            self.unit_sales_by_month.append(self.yearly_unit_sales / 12)
        for month in range (round(self.years_of_sales_decline * 12)):
            self.unit_sales_by_month.append(self.yearly_unit_sales * (1 - month / (self.years_of_sales_decline * 12)) / 12)
        if (len(self.unit_sales_by_month) == 0):
            self.unit_sales_by_month.append(0)

    # compute the delay before sales begin
    def years_before_sales(self):
        return self.years_mix_delay + self.years_of_development_growth + self.years_of_development_maturity + self.years_of_development_decline + self.years_of_pilot

    # compute the total number of years for the product
    def total_years(self):
        return self.years_before_sales() + self.years_of_sales_growth + self.years_of_sales_maturity + self.years_of_sales_decline + self.years_of_consumable_sales

    # compute the development full time equivalents for a given month
    def development_ftes_this_mix_month(self, month):
        month -= self.years_mix_delay * 12
        month = round(month)
        return self.ftes_by_month[month] if 0 <= month < len(self.ftes_by_month) else 0
    
    # compute the unit sales for a given month
    def unit_sales_this_mix_month(self, month):
        month -= self.years_before_sales() * 12
        month = round(month)
        return self.unit_sales_by_month[month] if 0 <= month < len(self.unit_sales_by_month) else 0