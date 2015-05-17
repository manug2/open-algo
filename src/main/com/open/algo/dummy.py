import random
import logging

from com.open.algo.trading.fxEvents import OrderEvent
from com.open.algo.model import Strategy


class DummyBuyStrategy(Strategy):
    def __init__(self, events, units, journaler):
        self.events = events
        self.units = units
        self.journaler = journaler
        self.logger = logging.getLogger(self.__class__.__name__)

    def calculate_signals(self, event):
        if event.TYPE == 'TICK':
            order = OrderEvent(event.instrument, self.units, 'buy')
            self.journaler.log_event(order)
            self.events.put(order)

    def start(self):
        super().start()

    def stop(self):
        super().stop()


class BuyOrSellAt5thTickStrategy(Strategy):
    def __init__(self, events, units, journaler):
        self.events = events
        self.units = units
        self.ticks = 0
        self.journaler = journaler

    def calculate_signals(self, event):
        if event.TYPE == 'TICK':
            self.ticks += 1
            if self.ticks % 5 == 0:
                side = random.choice(["buy", "sell"])
                order = OrderEvent(
                    event.instrument, self.units, side)
                self.journaler.log_event(order)
                self.events.put(order)

    def start(self):
        super().start()

    def stop(self):
        super().stop()


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

