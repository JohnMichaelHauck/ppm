class TornadoTracker:
    def __init__(self, tornado, name):
        self.tornado = tornado
        self.name = name
        self.min_value = float('inf')
        self.max_value = float('-inf')

    def add(self, value):
        if value < self.min_value:
            self.min_value = value
        if value > self.max_value:
            self.max_value = value
    
    def range(self):
        return self.max_value - self.min_value
