import tornado_tracker as tt
import simulation_tracker as st
from tornado_enum import Tornado

class MonteCarloResults:
    def __init__(self):
        self.simulation_tracker = st.SimulationTracker()
        self.tornado_trackers = []
        self.tornado_trackers.append(tt.TornadoTracker(Tornado.Dev_Ftes, 'Dev FTEs'))
        self.tornado_trackers.append(tt.TornadoTracker(Tornado.Dev_Years, 'Dev Years'))
        self.tornado_trackers.append(tt.TornadoTracker(Tornado.Maint_Ftes, 'Maint FTEs'))
        self.tornado_trackers.append(tt.TornadoTracker(Tornado.Sales_Years, 'Sales Years'))
        self.tornado_trackers.append(tt.TornadoTracker(Tornado.Unit_Cost, 'Unit Cost'))
        self.tornado_trackers.append(tt.TornadoTracker(Tornado.Margin, 'Margin'))
        self.tornado_trackers.append(tt.TornadoTracker(Tornado.Yearly_Sales, 'Yearly Sales'))
