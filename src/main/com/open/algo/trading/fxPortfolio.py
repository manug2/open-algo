__author__ = 'ManuGarg'


from com.open.algo.model import Portfolio


class FxPortfolio(Portfolio):

    def __init__(self):
        self.positions = {}
        self.executions = []

    def list_positions(self):
        return self.positions

    def append_position(self, executed_order):
        self.executions.append(executed_order)
        if executed_order.order.side == 'buy':
            if executed_order.order.instrument not in self.positions:
                self.positions[executed_order.order.instrument] = executed_order.units
            else:
                self.positions[executed_order.order.instrument] += executed_order.units
        else:
            if executed_order.order.instrument not in self.positions:
                self.positions[executed_order.order.instrument] = -executed_order.units
            else:
                self.positions[executed_order.order.instrument] -= executed_order.units

    def list_executions(self):
        return self.executions

    def list_position(self, instrument):
        return self.positions[instrument]
