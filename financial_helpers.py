# Present Value (PV) function
def pv(future_value, rate, periods):
    return future_value / (1 + rate) ** periods

# Future Value (FV) function
def fv(present_value, rate, periods):
    return present_value * (1 + rate) ** periods

def fvpv( present_value, rate_to_future, rate_to_present, periods):
    return pv( fv(present_value, rate_to_future, periods), rate_to_present, periods)

# Relationship between margin and cost factor
def cost_factor(margin):
    return 1 / (1 - margin)

