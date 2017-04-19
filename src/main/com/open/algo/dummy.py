import random

from com.open.algo.strategy import AbstractStrategy
from com.open.algo.trading.fxEvents import OrderEvent, ORDER_SIDE_BUY, ORDER_SIDE_SELL
from com.open.algo.utils import EventHandler

import logging
logger = logging.getLogger('dummy')


class DummyBuyStrategy(AbstractStrategy):
    """
    this strategy is used for testing of trading system in an event driven fashion
    as well as for unit testing of base class.
    """
    def __init__(self):
        super(DummyBuyStrategy, self).__init__()

    def calculate_signals(self, event):
        return ORDER_SIDE_BUY


class BuyOrSellAt5thTickStrategy(AbstractStrategy):
    def __init__(self):
        super(BuyOrSellAt5thTickStrategy, self).__init__()
        self.ticks = 0

    def calculate_signals(self, event):
        self.ticks += 1
        if self.ticks % 5 == 0:
            return random.choice([ORDER_SIDE_BUY, ORDER_SIDE_SELL])


class AlternateBuySellAt5thTickStrategy(AbstractStrategy):
    """
    this strategy is used for unit testing of abstract class.
    abstract class maintains signals, open interests etc.
    """
    def __init__(self):
        super(AlternateBuySellAt5thTickStrategy, self).__init__()
        self.ticks = 0
        self.side = ORDER_SIDE_SELL

    def calculate_signals(self, event):
        self.ticks += 1
        if self.ticks % 5 == 0:
            if self.side == ORDER_SIDE_SELL:
                self.side = ORDER_SIDE_BUY
                return self.side
            else:
                self.side = ORDER_SIDE_SELL
                return self.side


from com.open.algo.model import ExecutionHandler
from time import sleep
from com.open.algo.trading.fxEvents import ExecutedOrder


class DummyExecutor(ExecutionHandler, EventHandler):
    def __init__(self, delay=0):
        self.last_event = None
        self.delay = delay

    def get_last_event(self):
        return self.last_event

    def execute_order(self, event):
        if self.delay > 0:
            sleep(self.delay)
        self.last_event = event
        logger.info('Dummy Execution "%s", returning executed order' % event)
        return ExecutedOrder(event, 1.0, event.units)

    def stop(self):
        logger.info("Stopping Dummy Execution!")

    def start(self):
        logger.info("Starting Dummy Execution!")

    def process(self, event):
        return self.execute_order(event)


class DummyEventHandler(EventHandler):
    def process(self, event):
        if event is None:
            raise NotImplementedError('Cannot handle None event - [%s]' % str(self))
        else:
            return event

    def process_all(self, events):
        if events is None:
            raise NotImplementedError('Cannot handle None events - [%s]' % str(self))
        else:
            out_event = ''
            for event in events:
                if len(out_event) > 0:
                    out_event += ' '
                out_event += str(event)
            return out_event