import list_helpers as lh

class NpvCalculationResult:
    def __init__(self):
        self.development_cost = 0
        self.sales = 0 # inlcudes consumable sales
        self.consumable_sales = 0 # special breakout of consumable sales
        self.cost_of_goods = 0 # includes consumable cost of goods
        self.sga = 0
        self.unit_sales = 0
        self.ftes_by_month = []
        self.sales_by_month = [] # includes consumable sales
        self.consumable_sales_by_month = [] # special breakout of consumable sales
        self.cumulative_net_by_month = []

    def net(self):
        return self.sales - self.cost_of_goods - self.sga - self.development_cost

    def ros(self):
        return self.net() / self.sales if self.sales != 0 else 0

    def roi(self):
        return self.net() / self.development_cost if self.development_cost != 0 else 0

    def annualized_roi(self, years):
        return (1 + self.roi()) ** (1 / years) - 1 if years != 0 else 0
    
    def record_ftes(self, month, ftes):
        lh.add_value_to_index(self.ftes_by_month, month, ftes)
    
    def record_sales(self, month, sales):
        lh.add_value_to_index(self.sales_by_month, month, sales)
    
    def record_consumable_sales(self, month, consumable_sales):
        lh.add_value_to_index(self.consumable_sales_by_month, month, consumable_sales)

    def record_cumulative_net_by_month(self, month, npv):
        lh.add_value_to_index(self.cumulative_net_by_month, month, npv)

    def add(self, result):
        self.development_cost += result.development_cost
        self.sales += result.sales
        self.consumable_sales += result.consumable_sales
        self.cost_of_goods += result.cost_of_goods
        self.sga += result.sga
        self.unit_sales += result.unit_sales
        for month in range(len(result.ftes_by_month)):
            lh.add_value_to_index(self.ftes_by_month, month, result.ftes_by_month[month])
        for month in range(len(result.sales_by_month)):
            lh.add_value_to_index(self.sales_by_month, month, result.sales_by_month[month])
        for month in range(len(result.consumable_sales_by_month)):
            lh.add_value_to_index(self.consumable_sales_by_month, month, result.consumable_sales_by_month[month])
        for month in range(len(result.cumulative_net_by_month)):
            lh.add_value_to_index(self.cumulative_net_by_month, month, result.cumulative_net_by_month[month])
