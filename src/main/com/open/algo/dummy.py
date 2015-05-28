import random
import logging

from com.open.algo.model import EVENT_TYPES_FILL, EVENT_TYPES_ORDER, EVENT_TYPES_TICK, EVENT_TYPES_REJECTED
from com.open.algo.model import Strategy
from com.open.algo.trading.fxEvents import OrderEvent, ORDER_SIDE_BUY, ORDER_SIDE_SELL


class DummyBuyStrategy(Strategy):
    def __init__(self, events, units, journaler):
        self.events = events
        self.units = units
        self.journaler = journaler
        self.logger = logging.getLogger(self.__class__.__name__)
        self.signaled_positions = dict()
        self.open_interests = dict()

    def calculate_signals(self, event):
        order = OrderEvent(event.instrument, self.units, ORDER_SIDE_BUY)
        self.update_open_interest(order)
        self.journaler.log_event(order)
        self.events.put(order)

    def update_open_interest(self, order):
        if order.instrument in self.signaled_positions:
            old_pos = self.signaled_positions[order.instrument]
        else:
            old_pos = 0
        self.signaled_positions[order.instrument] = old_pos + order.get_signed_units()

    def acknowledge_execution(self, executed_order):
        if executed_order.TYPE != EVENT_TYPES_FILL:
            raise ValueError('Cannot acknowledge as order is not type "%s" - [%s]' % (EVENT_TYPES_FILL, executed_order))
        elif not self.find_and_update_execution(executed_order):
            raise ValueError('no signals found for acknowledging execution of [%s]' & executed_order)

    def find_and_update_execution(self, executed_order):
        instrument = executed_order.order.instrument
        if instrument not in self.signaled_positions:
            return False

        signaled_pos = self.signaled_positions[instrument]
        self.signaled_positions[instrument] = signaled_pos - executed_order.order.get_signed_orig_units()
        if instrument in self.open_interests:
            existing_pos = self.open_interests[instrument]
        else:
            existing_pos = 0
        self.open_interests[instrument] = existing_pos + executed_order.get_signed_units()
        return True

    def acknowledge_rejection(self, order):
        if order.TYPE != EVENT_TYPES_REJECTED:
            raise ValueError('Cannot acknowledge as order is not of type "%s" - [%s]' % (EVENT_TYPES_REJECTED, order))
        elif order.instrument in self.signaled_positions:
            old_pos = self.signaled_positions[order.instrument]
            self.signaled_positions[order.instrument] = old_pos - order.get_signed_orig_units()
        else:
            raise ValueError('no positions found in generated signals for acknowledging rejection of [%s]' & order)

    def get_open_interests(self):
        return self.open_interests

    def get_open_interest(self, instrument):
        return self.open_interests[instrument]

    def get_signaled_positions(self):
        return self.signaled_positions

    def get_signaled_position(self, instrument):
        return self.signaled_positions[instrument]


class BuyOrSellAt5thTickStrategy(Strategy):
    def __init__(self, events, units, journaler):
        self.events = events
        self.units = units
        self.ticks = 0
        self.journaler = journaler

    def calculate_signals(self, event):
        if event.TYPE == EVENT_TYPES_TICK:
            self.ticks += 1
            if self.ticks % 5 == 0:
                side = random.choice([ORDER_SIDE_BUY, ORDER_SIDE_SELL])
                order = OrderEvent(
                    event.instrument, self.units, side)
                self.journaler.log_event(order)
                self.events.put(order)


from com.open.algo.model import ExecutionHandler


class DummyExecutor(ExecutionHandler):
    def __init__(self):
        self.lastEvent = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_last_event(self):
        return self.lastEvent

    def execute_order(self, event):
        self.lastEvent = event
        self.logger.info('Dummy Execution "%s"' % event)

    def stop(self):
        self.logger.info("Stopping Dummy Execution!")

    def start(self):
        self.logger.info("Starting Dummy Execution!")

