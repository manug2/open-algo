__author__ = 'maverick'

import logging
from com.open.algo.strategy import AbstractStrategy
from com.open.algo.trading.fxEvents import ORDER_SIDE_SELL, ORDER_SIDE_BUY
from com.open.algo.calcs.twma import TickTWMA


class TWMACrossoverStrategy(AbstractStrategy):

    def __init__(self, base_tick, period1=5, period2=10, attribute='bid'):
        if period1 >= period2:
            raise ValueError('For ma, period 1(%s) cannot be ge period 2(%s)', period1, period2)
        super(TWMACrossoverStrategy, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ma_func1 = TickTWMA(period1, base_tick, attribute)
        self.ma_func2 = TickTWMA(period2, base_tick, attribute)
        self.ma1 = 0
        self.ma2 = 0
        self.tolerance = 0.00001

    def stop(self):
        pass

    def calculate_signals(self, event):
        if not event:
            raise ValueError('cannot calculate signal from None event')

        ma1 = self.ma_func1(event)
        ma2 = self.ma_func2(event)
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

    def set_tolerance(self, tolerance):
        if tolerance is None:
            raise ValueError('value of "%s" cannot be None' % 'tolerance')
        if not isinstance(tolerance, float):
            raise ValueError('value of "%s" should be of type "%s", not "%s"' % ('period2', type(float), type(tolerance)))
        self.tolerance = tolerance
        return self
