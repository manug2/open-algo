from abc import ABCMeta, abstractmethod
import logging

from com.open.algo.utils import EventHandler
from com.open.algo.utils import EVENT_TYPES_FILL, EVENT_TYPES_REJECTED, EVENT_TYPES_TICK, EVENT_TYPES_FILTERED
from com.open.algo.utils import EVENT_TYPES_EXCEPTION
from com.open.algo.trading.fxEvents import OrderEvent


class AbstractStrategy(EventHandler):
    __metaclass__ = ABCMeta

    def __init__(self):
        super(AbstractStrategy, self).__init__()

    @abstractmethod
    def calculate_signals(self, event):
        raise NotImplementedError('sub-classes should implement this')

    def process(self, event):
        return self.calculate_signals(event)


from com.open.algo.model import ExceptionEvent


class StrategyOrderManager(EventHandler):

    def __init__(self, strategy, units=1000):
        'call super'
        assert strategy is not None
        self.units = units
        self.strategy = strategy
        self.signaled_positions = dict()
        self.open_interests = dict()
        self.logger = logging.getLogger(self.__class__.__name__)

    def process(self, event):
        return self.calculate_signals(event)

    def calculate_signals(self, event):
        if event.TYPE != EVENT_TYPES_TICK:
            self.acknowledge(event)
            return

        instrument = getattr(event, 'instrument')
        if not instrument:
            raise RuntimeError('received event without attribute "instrument" - [%s]' % event)

        buy_sell_signal = self.strategy.calculate_signals(event)
        if buy_sell_signal:
            order = OrderEvent(instrument, self.units, buy_sell_signal)
            signal_units = order.get_signed_units()
            try:
                signal_amount_pending_ack = self.get_signaled_position(instrument)
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

    def get_signaled_positions(self):
        return self.signaled_positions

    def get_signaled_position(self, instrument):
        return self.signaled_positions[instrument]

    def acknowledge(self, event):
        self.logger.info('received ack/nak [%s]', event)
        if event.TYPE == EVENT_TYPES_FILL:
            self.acknowledge_execution(event)
        elif event.TYPE == EVENT_TYPES_FILTERED or event.TYPE == EVENT_TYPES_REJECTED:
            self.acknowledge_rejection(event)
        elif event.TYPE == EVENT_TYPES_EXCEPTION:
            self.acknowledge_exception(event)
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

    def acknowledge_exception(self, exception_event):
        self.logger.warn('received exception event:')
        self.logger.error(str(exception_event))

        if not isinstance(exception_event, ExceptionEvent):
            return

        order = exception_event.orig_event
        if not isinstance(order, OrderEvent):
            self.logger.error('cannot determine original order causing exception')
        else:
            instrument = order.instrument
            if instrument not in self.signaled_positions:
                raise ValueError('no positions found in generated signals for acknowledging rejection of [%s]' % order)
            self.update_signaled_position(instrument, -order.get_signed_orig_units())

    def get_open_interests(self):
        return self.open_interests

    def get_open_interest(self, instrument):
        return self.open_interests[instrument]
