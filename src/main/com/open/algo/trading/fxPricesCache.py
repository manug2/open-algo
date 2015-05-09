__author__ = 'ManuGarg'

from com.open.algo.model import MarketRateCache


class FxPricesCache(MarketRateCache):

    def __init__(self):
        self.rates = {}
        self.rates_tuples = {}
        self.started = False

        self.SAME_CCY_RATE = {'bid': 1.0, 'ask': 1.0}
        self.SAME_CCY_RATE_TUPLE = (1.0, 1.0)

    def set_rate(self, tick):
        assert tick is not None
        assert tick.instrument is not None
        assert tick.bid is not None
        assert tick.ask is not None

        if tick.instrument not in self.rates:
            self.rates[tick.instrument] = {}
        self.rates[tick.instrument]['bid'] = tick.bid
        self.rates[tick.instrument]['ask'] = tick.ask

        self.rates_tuples[tick.instrument] = (tick.bid, tick.ask)

    def get_rate(self, instrument):
        assert instrument is not None
        try:
            return self.rates[instrument]
        except KeyError as ke:
            currencies = instrument.split('_')
            if currencies[0] == currencies[1]:
                self.rates[instrument] = self.SAME_CCY_RATE
                return self.SAME_CCY_RATE
            else:
                raise ke

    def get_rate_tuple(self, instrument):
        assert instrument is not None
        try:
            return self.rates_tuples[instrument]
        except KeyError as ke:
            currencies = instrument.split('_')
            if currencies[0] == currencies[1]:
                self.rates[instrument] = self.SAME_CCY_RATE
                return self.SAME_CCY_RATE_TUPLE
            else:
                raise ke

    def start(self):
        pass

    def process(self, event):
        try:
            if event.TYPE == 'TICK':
                self.set_rate(event)
            else:
                raise TypeError('Not designed to handle event : [%s]' % event)
        except AttributeError:
            raise TypeError('Not designed to handle event without attribute [%s] : %s' % ('TYPE', event))

    def stop(self):
        pass