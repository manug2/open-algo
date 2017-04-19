__author__ = 'maverick'

import logging
from com.open.algo.strategy import AbstractStrategy
from com.open.algo.trading.fxEvents import ORDER_SIDE_SELL, ORDER_SIDE_BUY
from com.open.algo.calcs.ma import sma


class BidsMACrossoverStrategy(AbstractStrategy):

    def __init__(self, period1=5, period2=10, ma_function=sma):
        if period1 >= period2:
            raise ValueError('For ma, period 1(%s) cannot be ge period 2(%s)', period1, period2)
        super(BidsMACrossoverStrategy, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.bids = []
        #self.asks = []
        self.period1 = period1
        self.period2 = period2
        self.ma1 = None
        self.ma2 = None
        self.tolerance = 0.00001
        self.ma_function = ma_function

    def stop(self):
        pass

    def calculate_signals(self, event):
        if not event:
            raise ValueError('cannot calculate signal from None event')

        self.bids.append(event.bid)
        #self.asks.append(event.ask)

        if len(self.bids) < self.period1:
            return None

        if len(self.bids) < self.period2:
            if len(self.bids) == self.period2 - 1:
                self.ma1 = self.ma_function(self.bids, period=self.period1)
            return None

        ma1 = self.ma_function(self.bids, period=self.period1)
        ma2 = self.ma_function(self.bids, period=self.period2)
        diff = ma1 - ma2

        try:
            suspect_cross_over = abs(diff) >= self.tolerance
            if suspect_cross_over:
                if ma1 < self.ma1:
                    return ORDER_SIDE_SELL
                elif ma1 > self.ma1:
                    return ORDER_SIDE_BUY
                else:
                    return None
        finally:
            self.ma1 = ma1
            self.ma2 = ma2

    def start(self):
        pass

    def set_ma_function(self, ma_function):
        if ma_function is None:
            raise ValueError('value of "%s" cannot be None' % 'ma_function')
        self.ma_function = ma_function
        return self

    def set_tolerance(self, tolerance):
        assert tolerance is not None, 'value of "%s" cannot be None' % 'tolerance'
        assert isinstance(tolerance, float), 'value of "%s" should be of type "%s", not "%s"' % \
                                             ('period2', type(float), type(tolerance))
        self.tolerance = tolerance
        return self

