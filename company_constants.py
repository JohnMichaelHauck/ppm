class CompanyConstants:
    def __init__(self,
                 market_return = 0.0, #What we would expect to earn on an investment in a financial market with a similar risk
                 yearly_development_fte_cost_pv = 17000, # How much it costs per person to run a product development team (in present dollars)
                 maximum_development_ftes = 6, # How many product developers are available to staff projects
                 development_cost_trend = 0.0, # How much development costs increase each year
                 product_cost_trend = 0.0, # How much product costs increase each year
                 product_price_trend = 0.0): # How much product prices increase each year

        self.market_return = market_return
        self.yearly_development_fte_cost_pv = yearly_development_fte_cost_pv
        self.maximum_development_ftes = maximum_development_ftes
        self.development_cost_trend = development_cost_trend
        self.product_cost_trend = product_cost_trend
        self.product_price_trend = product_price_trend