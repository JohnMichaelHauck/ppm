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
        self.npv_by_month = []

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
        lh.add_value_to_index(self.ftes_by_month, month, ftes)
    
    def record_sales(self, month, sales):
        lh.add_value_to_index(self.sales_by_month, month, sales)
    
    def record_consumable_sales(self, month, consumable_sales):
        lh.add_value_to_index(self.consumable_sales_by_month, month, consumable_sales)

    def record_npv_by_month(self, month, npv):
        lh.add_value_to_index(self.npv_by_month, month, npv)

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
        for month in range(len(result.npv_by_month)):
            lh.add_value_to_index(self.npv_by_month, month, result.npv_by_month[month])
