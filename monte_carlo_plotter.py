import numpy as np # linear algebra library
import matplotlib.pyplot as plt # plotting library

class MonteCarloPlotter:
    # create a histogram
    def create_histogram(self, data, bins, xlabel, subplot_position, rows, cols, color = 'blue'):
        plt.subplot(rows, cols, subplot_position)
        plt.hist(data, bins=bins, edgecolor='black', color=color)
        plt.yticks([])
        plt.xlabel(xlabel)

    # create a tornado plot
    def create_tornado_plot(self, names, ranges, min_values, xlabel, subplot_position, rows, cols):
        plt.subplot(rows, cols, subplot_position)
        plt.barh(names, ranges, left=min_values)
        plt.xlabel(xlabel)
    
    # create a line chart
    def create_line_chart(self, data, xlabel, ylabel, subplot_position, rows, cols, color = 'blue'):
        plt.subplot(rows, cols, subplot_position)
        years = np.arange(len(data)) / 12
        plt.plot(years, data, color=color)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

    # plot the results
    def plot(self, monte_carlo_results, file_path = ""):
        rows = 4
        cols = 3
        plt.figure(figsize=(10, 5))

        self.create_histogram(monte_carlo_results.simulation_tracker.unit_sales, 20, 'Sales (units)', 1, rows, cols, 'blue')
        self.create_histogram(monte_carlo_results.simulation_tracker.sales_millions, 20, 'Sales ($ millions)', 2, rows, cols, 'red')
        self.create_histogram(monte_carlo_results.simulation_tracker.development_costs_millions, 20, 'Development ($ millions)', 3, rows, cols, 'green')

        self.create_histogram(monte_carlo_results.simulation_tracker.npvs_millions, 20, 'NPV ($ millions)', 4, rows, cols, 'purple')
        self.create_histogram(monte_carlo_results.simulation_tracker.ros, 20, 'ROS (%)', 5, rows, cols, 'orange')
        self.create_histogram(monte_carlo_results.simulation_tracker.years_to_achieve_10pct_ros, 20, 'Years to 10% ROS', 6, rows, cols, 'pink')

        tornado_names = [tornado_tracker.name for tornado_tracker in monte_carlo_results.tornado_trackers]
        tornado_ranges = [tornado_tracker.range() for tornado_tracker in monte_carlo_results.tornado_trackers]
        tornado_min_values = [tornado_tracker.min_value for tornado_tracker in monte_carlo_results.tornado_trackers]

        self.create_tornado_plot(tornado_names, tornado_ranges, tornado_min_values, 'NPV Sensitivity ($ millions)', 7, rows, cols)
        self.create_line_chart(monte_carlo_results.simulation_tracker.ftes_by_month, 'Years', 'Ftes', 8, rows, cols, 'black')
        self.create_line_chart(monte_carlo_results.simulation_tracker.sales_by_month, 'Years', 'Monthly Sales ($)', 9, rows, cols, 'black')

        self.create_histogram(monte_carlo_results.simulation_tracker.years_to_break_even, 20, 'Years to Break Even', 10, rows, cols, 'teal')
        self.create_histogram(monte_carlo_results.simulation_tracker.consumable_sales_millions, 20, 'Consumables ($ millions)', 11, rows, cols, 'red')
        self.create_line_chart(monte_carlo_results.simulation_tracker.consumable_sales_by_month, 'Years', 'Monthly Consumables ($)', 12, rows, cols, 'black')

        plt.tight_layout( pad=0, w_pad=0, h_pad=0 )

        if( file_path != ""):
            plt.savefig(file_path)
        else:
            plt.show()
            
        plt.close()
