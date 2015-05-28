from com.open.algo.utils import EventHandler, EVENT_TYPES_ORDER, EVENT_TYPES_TICK


class AlgoTrader(EventHandler):
    def __init__(self, prices, strategy, executor):
        super(AlgoTrader, self).__init__()
        self.prices = prices
        self.strategy = strategy
        self.executor = executor

    def process(self, event):
        try:
            if event.TYPE == EVENT_TYPES_TICK:
                return self.strategy.calculate_signals(event)
            elif event.TYPE == EVENT_TYPES_ORDER:
                self.executor.execute_order(event)
            else:
                raise TypeError('Not designed to handle event : [%s]' % event)
        except AttributeError:
            raise TypeError('Not designed to handle event without attribute [%s] : %s' % ('TYPE', event))

    def stop(self):
        if self.executor is not None:
            self.executor.stop()

        if self.prices is not None:
            self.prices.stop()

        # End of stop()

