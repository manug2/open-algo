__author__ = 'ManuGarg'

from com.open.algo.model import MarketRateCache


class FxPricesCache(MarketRateCache):

    def __init__(self):
        self.rates = {}
        self.rates_tuples = {}
        self.started = False

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
        rates = self.rates[instrument]
        return rates

    def get_rate_tuple(self, instrument):
        assert instrument is not None
        rates = self.rates_tuples[instrument]
        return rates

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