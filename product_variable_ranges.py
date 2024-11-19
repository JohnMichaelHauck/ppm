class ProductVariablesRanges:
    def __init__(self,
                 name = "",
                 type = "",
                 years_of_development_growth = 0, # Years of development FTE increase from zero (linear)
                 years_of_development_maturity = 0, # Years of development FTE full usage
                 years_of_development_decline = 0, #Years of development FTE decrease to zero (linear)
                 years_of_pilot = 0, # Years after development before sales begin
                 years_of_sales_growth = 0, # Years of sales increase from zero (linear)
                 years_of_sales_maturity = 0, # Years of full sales
                 years_of_sales_decline = 0, # Years of sales decrease to zero (linear)
                 development_ftes = 0, # The number of people (full time equivalents) on the development team
                 maintenance_ftes = 0, # The number of people that need to keep working on the product after development
                 years_of_maintenance = 0, # The number of years people need to keep working on the product after development
                 unit_cost_pv = 0, # The cost to manufacture one unit of the product (in present dollars)
                 unit_margin = 0, # The percentage of the selling price that exceeds cost of goods
                 sga_factor = 0, # The percentage of the selling price that is allocated to cover selling, general, and administrative
                 yearly_unit_sales = 0, # The number of units that are expected to be sold per year
                 yearly_unit_consumable_sales = 0, # The consumable sales per unit sold per year
                 years_of_consumable_sales = 0, # The number of years consumables will be sold following a unit sale
                 consumable_margin = 0): # The percentage of consumable sales that exceeds the consumable cost of goods

        self.name = name
        self.type = type
        self.years_mix_delay = 0
        self.years_of_development_growth = years_of_development_growth if years_of_development_growth is not None else [0, 0, 0]
        self.years_of_development_maturity = years_of_development_maturity if years_of_development_maturity is not None else [0, 0, 0]
        self.years_of_development_decline = years_of_development_decline if years_of_development_decline is not None else [0, 0, 0]
        self.years_of_pilot = years_of_pilot if years_of_pilot is not None else [0, 0, 0]
        self.years_of_sales_growth = years_of_sales_growth if years_of_sales_growth is not None else [0, 0, 0]
        self.years_of_sales_maturity = years_of_sales_maturity if years_of_sales_maturity is not None else [0, 0, 0]
        self.years_of_sales_decline = years_of_sales_decline if years_of_sales_decline is not None else [0, 0, 0]
        self.development_ftes = development_ftes if development_ftes is not None else [0, 0, 0]
        self.maintenance_ftes = maintenance_ftes if maintenance_ftes is not None else [0, 0, 0]
        self.years_of_maintenance = years_of_maintenance if years_of_maintenance is not None else [0, 0, 0]
        self.unit_cost_pv = unit_cost_pv if unit_cost_pv is not None else [0, 0, 0]
        self.unit_margin = unit_margin if unit_margin is not None else [0, 0, 0]
        self.sga_factor = sga_factor if sga_factor is not None else [0, 0, 0]
        self.yearly_unit_sales = yearly_unit_sales if yearly_unit_sales is not None else [0, 0, 0]
        self.yearly_unit_consumable_sales = yearly_unit_consumable_sales if yearly_unit_consumable_sales is not None else [0, 0, 0]
        self.years_of_consumable_sales = years_of_consumable_sales if years_of_consumable_sales is not None else [0, 0, 0]
        self.consumable_margin = consumable_margin if consumable_margin is not None else [0, 0, 0]
    
    @classmethod
    def market_of(
        cls,
        name,
        type,
        existing_instance,
        unit_cost,
        unit_margin,
        sga_factor,
        yearly_unit_sales,
        yearly_unit_consumable_sales,
        years_of_consumable_sales,
        consumable_margin):

        return cls(
            name = name,
            type = type,
            years_of_development_growth = 0,
            years_of_development_maturity = 0,
            years_of_development_decline = 0,
            years_of_pilot = 0,
            years_of_sales_growth = existing_instance.years_of_sales_growth,
            years_of_sales_maturity = existing_instance.years_of_sales_maturity,
            years_of_sales_decline = existing_instance.years_of_sales_decline,
            development_ftes = 0,
            maintenance_ftes = 0,
            years_of_maintenance = 0,
            unit_cost_pv = unit_cost if unit_cost is not None else existing_instance.unit_cost_pv,
            unit_margin = unit_margin if unit_margin is not None else existing_instance.unit_margin,
            sga_factor = sga_factor if sga_factor is not None else existing_instance.sga_factor,
            yearly_unit_sales = yearly_unit_sales if yearly_unit_sales is not None else existing_instance.yearly_unit_sales,
            yearly_unit_consumable_sales = yearly_unit_consumable_sales if yearly_unit_consumable_sales is not None else existing_instance.yearly_unit_consumable_sales,
            years_of_consumable_sales = years_of_consumable_sales if years_of_consumable_sales is not None else existing_instance.years_of_consumable_sales,
            consumable_margin = consumable_margin if consumable_margin is not None else existing_instance.consumable_margin)