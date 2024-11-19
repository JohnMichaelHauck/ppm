import npv_calculation_result as ncr
import npv_calculator as nc

# Calculate the product mix
class MixCalculator:
    
    # Calculate the years mix delay based on the maximum development FTEs
    def calculate_years_mix_delay(self, maximum_development_ftes, minimum_years_mix_delay, allocated_ftes_by_month, new_ftes_by_month):
        months_mix_delay = round(minimum_years_mix_delay * 12)
        maximum_development_ftes = max(maximum_development_ftes, max(new_ftes_by_month))
        allocated_ftes_by_month.extend([0] * len(new_ftes_by_month))
        while(True):
            overallocated = False
            for month in range(len(new_ftes_by_month)):
                if allocated_ftes_by_month[month + months_mix_delay] + new_ftes_by_month[month] > maximum_development_ftes:
                    overallocated = True
                    break
            if not overallocated:
                return months_mix_delay / 12
            months_mix_delay += 1

    # Calculate the NPV of a product mix
    def calculate_mix_npv(self, mix_variables_snapshot, company_constants):
        mix_result = ncr.NpvCalculationResult()
        minimum_years_mix_delay = 0
        for product_variables_snapshot in mix_variables_snapshot.mix_variables_snapshots:
            if( product_variables_snapshot.type == "Product"):
                minimum_years_mix_delay = 0
            product_variables_snapshot.years_mix_delay = self.calculate_years_mix_delay(company_constants.maximum_development_ftes, minimum_years_mix_delay, mix_result.ftes_by_month, product_variables_snapshot.ftes_by_month)
            product_result = nc.NpvCalculator().calculate_product_npv(product_variables_snapshot, company_constants)
            mix_result.add(product_result)
            minimum_years_mix_delay = product_variables_snapshot.years_before_sales()

        return mix_result
