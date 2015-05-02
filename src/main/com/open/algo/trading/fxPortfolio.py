__author__ = 'ManuGarg'


from com.open.algo.model import Portfolio


class FxPortfolio(Portfolio):

    def __init__(self, base_ccy, prices_cache=None):
        self.positions = {}
        self.executions = []
        assert base_ccy is not None, 'portfolio manager needs a base currency'
        assert base_ccy != '', 'portfolio manager needs a base currency'
        self.base_ccy = base_ccy
        self.price_cache = prices_cache
        self.positions_avg_price = {}

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

        self.positions_avg_price[executed_order.order.instrument] = executed_order.price

    def list_executions(self):
        return self.executions

    def list_position(self, instrument):
        return self.positions[instrument]

    def reval_position(self, instrument):
        position = self.positions[instrument]
        if position == 0:
            return 0
        rates = self.price_cache.get_rate(instrument)
        if position < 0:
            value = position * rates['bid']
        else:
            value = position * rates['ask']
        return value
