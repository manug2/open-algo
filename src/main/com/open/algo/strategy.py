from abc import ABCMeta, abstractmethod

from com.open.algo.utils import EventHandler
from com.open.algo.utils import EVENT_TYPES_FILL, EVENT_TYPES_REJECTED, EVENT_TYPES_TICK, EVENT_TYPES_FILTERED
import logging


class AbstractStrategy(EventHandler):
    __metaclass__ = ABCMeta

    def __init__(self):
        super(AbstractStrategy, self).__init__()
        self.signaled_positions = dict()
        self.open_interests = dict()
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def calculate_signals(self, event):
        raise NotImplementedError('sub-classes should implement this')

    def process(self, event):
        if event.TYPE == EVENT_TYPES_TICK:
            return self.calculate_signals(event)
        else:
            self.acknowledge(event)

    def acknowledge(self, event):
        self.logger.info('received ack/nak [%s]', event)
        if event.TYPE == EVENT_TYPES_FILL:
            self.acknowledge_execution(event)
        elif event.TYPE == EVENT_TYPES_FILTERED or event.TYPE == EVENT_TYPES_REJECTED:
            self.acknowledge_rejection(event)
        else:
            raise ValueError('Don\'t know how to handle event of type "%s" - [%s]' % (event.TYPE, event))

    def update_signaled_position(self, instrument, signed_units):
        if instrument in self.signaled_positions:
            old_pos = self.signaled_positions[instrument]
        else:
            old_pos = 0
        self.signaled_positions[instrument] = old_pos + signed_units

    def update_open_interest(self, instrument, signed_units):
        if instrument in self.open_interests:
            existing_pos = self.open_interests[instrument]
        else:
            existing_pos = 0
        self.open_interests[instrument] = existing_pos + signed_units

    def acknowledge_execution(self, executed_order):
        instrument = executed_order.order.instrument
        if instrument not in self.signaled_positions:
            raise ValueError('no signals found for acknowledging execution of [%s]' % executed_order)
        self.update_signaled_position(instrument, -executed_order.order.get_signed_orig_units())
        self.update_open_interest(instrument, executed_order.get_signed_units())

    def acknowledge_rejection(self, order):
        instrument = order.instrument
        if instrument not in self.signaled_positions:
            raise ValueError('no positions found in generated signals for acknowledging rejection of [%s]' % order)
        self.update_signaled_position(instrument, -order.get_signed_orig_units())

    def get_open_interests(self):
        return self.open_interests

    def get_open_interest(self, instrument):
        return self.open_interests[instrument]

    def get_signaled_positions(self):
        return self.signaled_positions

    def get_signaled_position(self, instrument):
        return self.signaled_positions[instrument]


from com.open.algo.calcs.ma import sma
from com.open.algo.trading.fxEvents import OrderEvent, ORDER_SIDE_BUY, ORDER_SIDE_SELL


class MACrossoverStrategy(AbstractStrategy):

    def __init__(self, period1=5, period2=10, ma_function=sma):
        if period1 >= period2:
            raise ValueError('For ma, period 1(%s) cannot be ge period 2(%s)', period1, period2)
        super(MACrossoverStrategy, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.bids = []
        self.asks = []
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
        self.asks.append(event.ask)

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
