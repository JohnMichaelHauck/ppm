import list_helpers as lh

class SimulationTracker:
    def __init__(self):
        self.simulations = 0
        self.npvs_millions = []
        self.development_costs_millions = []
        self.unit_sales = []
        self.sales_millions = []
        self.consumable_sales_millions = []
        self.ros = []
        self.roi = []
        self.ftes_by_month = []
        self.sales_by_month = []
        self.consumable_sales_by_month = []
        self.years_to_break_even = []
        self.years_to_achieve_10pct_ros = []
    
    def add(self, result):
        self.simulations += 1
        self.npvs_millions.append(result.net() / 1000000)
        self.development_costs_millions.append(result.development_cost / 1000000)
        self.unit_sales.append(result.unit_sales)
        self.sales_millions.append(result.sales / 1000000)
        self.consumable_sales_millions.append(result.consumable_sales / 1000000)
        self.ros.append(result.ros() * 100)
        self.roi.append(result.roi() * 100)
        for month in range(len(result.ftes_by_month)):
            lh.add_value_to_index(self.ftes_by_month, month, result.ftes_by_month[month])
        for month in range(len(result.sales_by_month)):
            lh.add_value_to_index(self.sales_by_month, month, result.sales_by_month[month])
        for month in range(len(result.consumable_sales_by_month)):
            lh.add_value_to_index(self.consumable_sales_by_month, month, result.consumable_sales_by_month[month])

        # record the number of months to break even
        months_to_break_even = -12
        months_to_achive_10pct_ros = -12
        cumulative_sales = 0
        for month in range(len(result.cumulative_net_by_month)):
            cumulative_net = result.cumulative_net_by_month[month]
            sales = result.sales_by_month[month]
            cumulative_sales += sales
            cumulative_ros = cumulative_net / cumulative_sales if cumulative_sales != 0 else 0
            if cumulative_net > 0 and months_to_break_even < 0:
                months_to_break_even = month
            if cumulative_ros >= 0.1 and months_to_achive_10pct_ros < 0:
                months_to_achive_10pct_ros = month
            if months_to_break_even >= 0 and months_to_achive_10pct_ros >= 0:
                break
        self.years_to_break_even.append(months_to_break_even / 12)
        self.years_to_achieve_10pct_ros.append(months_to_achive_10pct_ros / 12)
    
    def normalize(self):
        if self.simulations > 0:
            # normalize FTEs by dividing each value by the number of simulations
            for month in range(len(self.ftes_by_month)):
                self.ftes_by_month[month] /= self.simulations

            # normalize sales by dividing each value by the number of simulations
            for month in range(len(self.sales_by_month)):
                self.sales_by_month[month] /= self.simulations

            # normalize consumable sales by dividing each value by the number of simulations
            for month in range(len(self.consumable_sales_by_month)):
                self.consumable_sales_by_month[month] /= self.simulations
