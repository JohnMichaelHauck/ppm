import os
import tempfile
import sys
import company_constants as cc
import product_variable_ranges as pvr
import monte_carlo_calculator as mcc
import monte_carlo_plotter as mcp
import excel_helpers as xh

# Check if there are any command line arguments
if len(sys.argv) == 2:
    excel_file_path = sys.argv[1]
    plot_file_path = os.path.join(tempfile.gettempdir(), 'ppm.png')
    plot_file_path = ""
    company_constants, mix_variables_ranges = xh.ExcelHelpers().read_excel_data(excel_file_path)
else:
    excel_file_path = ""
    plot_file_path = ""
    company_constants = cc.CompanyConstants()
    product1 = pvr.ProductVariablesRanges()
    mix_variables_ranges = [product1]

# Run the Monte Carlo simulation
monte_carlo_results = mcc.MonteCarloCalculator().calculate(company_constants, mix_variables_ranges)
mcp.MonteCarloPlotter().plot(monte_carlo_results, plot_file_path)