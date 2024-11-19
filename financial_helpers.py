# Present Value (PV) function
def pv(future_value, rate, periods):
    return future_value / (1 + rate) ** periods

# Future Value (FV) function
def fv(present_value, rate, periods):
    return present_value * (1 + rate) ** periods

# Relationship between margin and cost factor
def cost_factor(margin):
    return 1 / (1 - margin)
