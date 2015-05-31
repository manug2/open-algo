__author__ = 'ManuGarg'

from com.open.algo.model import MarketRateCache
from com.open.algo.utils import get_age_seconds, EventHandler


class FxPricesCache(MarketRateCache, EventHandler):

    def __init__(self, max_tick_age=(16*60*60 + 2*60)):
        self.rates = {}
        self.rates_tuples = {}
        self.started = False

        self.SAME_CCY_RATE = {'bid': 1.0, 'ask': 1.0}
        self.SAME_CCY_RATE_TUPLE = (1.0, 1.0)

        # self.max_tick_age -  represents oldest tick that cache will accept. default is 16 hours(EST) + few minutes
        assert max_tick_age > 0, 'Maximum permissible age of ticks should be more than 0, found [%s]' % max_tick_age
        self.max_tick_age = max_tick_age

    def set_rate(self, tick):
        assert tick is not None
        assert tick.instrument is not None
        assert tick.bid is not None
        assert tick.ask is not None

        age = -1 * get_age_seconds(tick.time)
        assert age > 0, 'Future tick is not allowed - [%s]' % tick
        assert age < self.max_tick_age, 'Tick too old, age[%s], max allowed[%s] - [%s]' % (age, self.max_tick_age, tick)

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