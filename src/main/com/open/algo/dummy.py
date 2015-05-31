import random

from com.open.algo.strategy import AbstractStrategy
from com.open.algo.trading.fxEvents import OrderEvent, ORDER_SIDE_BUY, ORDER_SIDE_SELL


class DummyBuyStrategy(AbstractStrategy):
    def __init__(self, units):
        super(DummyBuyStrategy, self).__init__()
        self.units = units

    def calculate_signals(self, event):
        try:
            signal_amount_pending_ack = self.get_signaled_position(event.instrument)
        except KeyError:
            signal_amount_pending_ack = 0
        if signal_amount_pending_ack == 0:
            order = OrderEvent(event.instrument, self.units, ORDER_SIDE_BUY)
            self.update_signaled_position(order.instrument, order.get_signed_units())
            return order


class BuyOrSellAt5thTickStrategy(AbstractStrategy):
    def __init__(self, units):
        super(BuyOrSellAt5thTickStrategy, self).__init__()
        self.units = units
        self.ticks = 0

    def calculate_signals(self, event):
        self.ticks += 1
        if self.ticks % 5 == 0:
            side = random.choice([ORDER_SIDE_BUY, ORDER_SIDE_SELL])
            order = OrderEvent(event.instrument, self.units, side)
            self.update_signaled_position(order.instrument, order.get_signed_units())
            return order


class AlternateBuySellAt5thTickStrategy(AbstractStrategy):
    def __init__(self, units):
        super(AlternateBuySellAt5thTickStrategy, self).__init__()
        self.units = units
        self.ticks = 0
        self.side = ORDER_SIDE_BUY

    def calculate_signals(self, event):
        self.ticks += 1
        if self.ticks % 5 == 0:
            order = OrderEvent(event.instrument, self.units, self.side)
            if self.side == ORDER_SIDE_SELL:
                self.side = ORDER_SIDE_BUY
            else:
                self.side = ORDER_SIDE_SELL
            self.update_signaled_position(order.instrument, order.get_signed_units())
            return order


from com.open.algo.model import ExecutionHandler
import logging


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

