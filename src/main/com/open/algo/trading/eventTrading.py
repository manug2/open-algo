
class AlgoTrader:
    def __init__(self, prices, strategy, executor):
        self.prices = prices
        self.strategy = strategy
        self.executor = executor

    def process(self, event):
        try:
            if event.TYPE == 'TICK':
                self.strategy.calculate_signals(event)
            elif event.TYPE == 'ORDER':
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

