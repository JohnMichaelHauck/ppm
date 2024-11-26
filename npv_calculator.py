import list_helpers as lh
import financial_helpers as fh
import npv_calculation_result as ncr

class NpvCalculator:

    # Calculate the NPV of a product
    def calculate_product_npv(self, product_variables_snapshot, company_constants):

        # this is what we will calculate and return 
        npv_calculation_result = ncr.NpvCalculationResult()
        unit_monthly_sales_history = []

        # loop through all the months
        for month in range(round(product_variables_snapshot.total_years() * 12) + 1):
            mix_month = month + round(product_variables_snapshot.years_mix_delay * 12)
        
            # compute the development ftes for this month
            development_ftes_this_month = product_variables_snapshot.development_ftes_this_mix_month(mix_month)

            # compute the unit sales for this month
            unit_sales_this_month = product_variables_snapshot.unit_sales_this_mix_month(mix_month)
            lh.add_value_to_index(unit_monthly_sales_history, month, unit_sales_this_month)

            # compute the consumable sales for this month
            unit_sales_needing_consumables_this_month = sum(unit_monthly_sales_history[-round(product_variables_snapshot.years_of_consumable_sales * 12):])

            # compute the future value of the cost of development, unit cost, unit price, and sg&a for this month
            monthly_development_cost_fte_fv = fh.fv(company_constants.yearly_development_fte_cost_pv / 12, company_constants.development_cost_trend / 12, mix_month)
            unit_cost_fv = fh.fv(product_variables_snapshot.unit_cost_pv, company_constants.product_cost_trend / 12, mix_month)
            unit_price_fv = fh.fv(product_variables_snapshot.unit_price_pv, company_constants.product_price_trend / 12, mix_month)
            consumable_sales_fv = fh.fv(product_variables_snapshot.yearly_unit_consumable_sales / 12, company_constants.product_price_trend / 12, mix_month)

            # return everything to present value
            development_cost_this_month_pv = fh.pv(development_ftes_this_month * monthly_development_cost_fte_fv, company_constants.market_return / 12, mix_month)
            sales_this_month_pv = fh.pv(unit_sales_this_month * unit_price_fv, company_constants.market_return / 12, mix_month)
            cost_of_goods_this_month_pv = fh.pv(unit_sales_this_month * unit_cost_fv, company_constants.market_return / 12, mix_month)
            sga_this_month_pv = fh.pv(sales_this_month_pv * product_variables_snapshot.sga_factor, company_constants.market_return / 12, mix_month)
            consumable_sales_this_month_pv = fh.pv(unit_sales_needing_consumables_this_month * consumable_sales_fv, company_constants.market_return / 12, mix_month)
            consumable_cost_of_goods_pv = consumable_sales_this_month_pv * (1 - product_variables_snapshot.consumable_margin)

            # add the results for this month to the total
            npv_calculation_result.development_cost += development_cost_this_month_pv
            npv_calculation_result.sales += sales_this_month_pv + consumable_sales_this_month_pv
            npv_calculation_result.consumable_sales += consumable_sales_this_month_pv
            npv_calculation_result.cost_of_goods += cost_of_goods_this_month_pv + consumable_cost_of_goods_pv
            npv_calculation_result.sga += sga_this_month_pv
            npv_calculation_result.unit_sales += unit_sales_this_month
            npv_calculation_result.record_ftes(mix_month, development_ftes_this_month)
            npv_calculation_result.record_sales(mix_month, sales_this_month_pv + consumable_sales_this_month_pv)
            npv_calculation_result.record_consumable_sales(mix_month, consumable_sales_this_month_pv)
            npv_calculation_result.record_cumulative_net_by_month(mix_month, npv_calculation_result.net())

        return npv_calculation_result
