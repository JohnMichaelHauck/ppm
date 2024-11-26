import monte_carlo_results as mcr
import mix_calculator as mc
import mix_variable_snapshot as mvs

class MonteCarloCalculator:
    def calculate(self, company_constants, mix_variables_ranges):
        monte_carlo_results = mcr.MonteCarloResults()
                
        # compute the monte carlo analysis
        simulations = 4000
        for i in range(simulations):
            mix_variables_snapshot = mvs.MixVariablesSnapshot(mix_variables_ranges)
            mix_result = mc.MixCalculator().calculate_mix_npv(mix_variables_snapshot, company_constants)
            monte_carlo_results.simulation_tracker.add(mix_result)

        # normalize the results
        monte_carlo_results.simulation_tracker.normalize()
        
        # compute the tornado analysis
        for i in range(100):    
            for tornado_tracker in monte_carlo_results.tornado_trackers:
                mix_variables_snapshot = mvs.MixVariablesSnapshot(mix_variables_ranges, tornado_tracker.tornado)
                mix_result = mc.MixCalculator().calculate_mix_npv(mix_variables_snapshot, company_constants)
                tornado_tracker.add(mix_result.net() / 1000000)

        # Sort the tornado trackers by range
        monte_carlo_results.tornado_trackers.sort(key=lambda x: x.range())
    
        return monte_carlo_results
