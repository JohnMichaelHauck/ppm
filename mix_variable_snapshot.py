from tornado_enum import Tornado
import product_variables_snapshot as pvs

class MixVariablesSnapshot:
    def __init__(self, mix_variables_ranges, tornado = Tornado.OFF):
        self.mix_variables_ranges = mix_variables_ranges
        self.mix_variables_snapshots = []
        for product_variables_ranges in mix_variables_ranges:
            product_variables_snapshot = pvs.ProductVariablesSnapshot(product_variables_ranges, tornado)
            self.mix_variables_snapshots.append(product_variables_snapshot)