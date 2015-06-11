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
