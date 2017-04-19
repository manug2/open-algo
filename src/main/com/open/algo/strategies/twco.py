__author__ = 'maverick'

import logging
from com.open.algo.strategy import AbstractStrategy
from com.open.algo.trading.fxEvents import ORDER_SIDE_SELL, ORDER_SIDE_BUY
from com.open.algo.calcs.twma import TWMA


class TWMACrossoverStrategy(AbstractStrategy):

    def __init__(self, period1, period2, time_attr='time', val_attr='bid'):
        assert period1 < period2, 'For TWMA crossover, period 1(%s) cannot be ge period 2(%s)' % (period1, period2)
        super(TWMACrossoverStrategy, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ticks = []
        self.ma1 = None
        self.ma2 = None
        self.tolerance = 0.00001
        self.ma_function1 = TWMA(period1, time_attr, val_attr)
        self.ma_function2 = TWMA(period2, time_attr, val_attr)

    def stop(self):
        pass

    def calculate_signals(self, event):
        if not event:
            raise ValueError('cannot calculate signal from None event')

        self.ticks.append(event)

        if len(self.ticks) < self.ma_function1.time_period:
            return None

        if len(self.ticks) < self.ma_function2.time_period:
            if len(self.ticks) == self.ma_function2.time_period - 1:
                self.ma1 = self.ma_function1(event.time, self.ticks)
            return None

        #now = event.receive_time
        now = event.time

        ma1 = self.ma_function1(now, self.ticks)
        ma2 = self.ma_function2(now, self.ticks)
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
        assert tolerance is not None, 'value of "%s" cannot be None' % 'tolerance'
        assert isinstance(tolerance, float), 'value of "%s" should be of type "%s", not "%s"' % \
                                             ('period2', type(float), type(tolerance))
        self.tolerance = tolerance
        return self
