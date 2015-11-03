__author__ = 'maverick'

import logging
from com.open.algo.strategy import AbstractStrategy
from com.open.algo.trading.fxEvents import ORDER_SIDE_SELL, ORDER_SIDE_BUY, OrderEvent
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
        self.tolerance = 0.001
        self.ma_function = ma_function
        self.units = 1000

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

        try:
            order = None
            signal_units = 0

            suspect_cross_over = abs(ma1-ma2) <= self.tolerance
            if suspect_cross_over:
                if ma1 < self.ma1:
                    side = ORDER_SIDE_SELL
                elif ma1 > self.ma1:
                    side = ORDER_SIDE_BUY
                else:
                    return None

                order = OrderEvent(event.instrument, self.units, side)
                signal_units = order.get_signed_units()
                try:
                    signal_amount_pending_ack = self.get_signaled_position(event.instrument)
                except KeyError:
                    signal_amount_pending_ack = 0

                if signal_amount_pending_ack != 0:
                    if signal_units > 0 and signal_amount_pending_ack > 0:
                        signal_units = 0
                    elif signal_units < 0 and signal_amount_pending_ack < 0:
                        signal_units = 0

            if signal_units != 0:
                self.logger.info('issuing order - %s' % order)
                self.update_signaled_position(order.instrument, order.get_signed_units())
                return order

        finally:
            self.ma1 = ma1
            self.ma2 = ma2

        return None

    def process_all(self, events):
        pass

    def start(self):
        pass

    def set_ma_function(self, ma_function):
        if ma_function is None:
            raise ValueError('value of "%s" cannot be None' % 'ma_function')
        self.ma_function = ma_function
        return self

    def set_tolerance(self, tolerance):
        if tolerance is None:
            raise ValueError('value of "%s" cannot be None' % 'tolerance')
        if not isinstance(tolerance, float):
            raise ValueError('value of "%s" should be of type "%s", not "%s"' % ('period2', type(float), type(tolerance)))
        self.tolerance = tolerance
        return self