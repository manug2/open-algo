import unittest
from queue import Queue

from com.open.algo.trading.eventTrading import AlgoTrader
from com.open.algo.trading.fxEvents import *
from com.open.algo.wiring.eventLoop import EventLoop
from com.open.algo.dummy import *
from com.open.algo.utils import get_time, EVENT_TYPES_ORDER


class TestStreamTrading(unittest.TestCase):
    def setUp(self):
        self.events = Queue()
        self.execution_q = Queue()
        self.strategy = DummyBuyStrategy(100)
        self.executor = DummyExecutor()
        self.algo_trader = AlgoTrader(None, self.strategy, self.executor)
        self.trader = EventLoop(self.events, self.algo_trader)
        self.trader.started = True

    def test_order_generation_in_separate_queue(self):
        self.trader.processed_event_q = self.execution_q
        tick = TickEvent('EUR_GBP', get_time(), 0.87, 0.88)
        self.events.put(tick)
        self.trader.pull_process()

        order = self.execution_q.get_nowait()
        self.assertEquals(tick.instrument, order.instrument)
        self.assertEquals(EVENT_TYPES_ORDER, order.TYPE)
        self.assertEquals(self.strategy.units, order.units)

    def test_order_generation_in_same_queue(self):
        self.trader.processed_event_q = self.events
        tick = TickEvent('EUR_GBP', get_time(), 0.87, 0.88)
        self.events.put(tick)
        self.trader.pull_process()

        order = self.executor.get_last_event()
        self.assertEquals(tick.instrument, order.instrument)
        self.assertEquals(EVENT_TYPES_ORDER, order.TYPE)
        self.assertEquals(self.strategy.units, order.units)


class TestStreamTradingRandom(unittest.TestCase):
    def setUp(self):
        self.events = Queue()
        self.execution_q = Queue()
        self.strategy = BuyOrSellAt5thTickStrategy(100)
        self.executor = DummyExecutor()
        self.algo_trader = AlgoTrader(None, self.strategy, self.executor)
        self.trader = EventLoop(self.events, self.algo_trader)
        self.trader.started = True

    def test_order_generation_in_separate_queue(self):
        self.trader.processed_event_q = self.execution_q
        for i in range(1, 7):
            tick = TickEvent("EUR_GBP", get_time(), round(0.87 + (i / 100), 2), 0.88 + (i / 100))
            self.events.put(tick)
        self.trader.pull_process()

        order = self.execution_q.get_nowait()
        self.assertEquals(tick.instrument, order.instrument)
        self.assertEquals(EVENT_TYPES_ORDER, order.TYPE)
        self.assertEquals(self.strategy.units, order.units)

    def test_order_generation_in_same_queue(self):
        self.trader.processed_event_q = self.events
        for i in range(1, 6):
            tick = TickEvent("EUR_GBP", get_time(), round(0.87 + (i / 100), 2), 0.88 + (i / 100))
            self.events.put(tick)
        self.trader.pull_process()

        # order should be generated at the 6th tick
        order = self.executor.get_last_event()
        self.assertEquals(tick.instrument, order.instrument)
        self.assertEquals(EVENT_TYPES_ORDER, order.TYPE)
        self.assertEquals(self.strategy.units, order.units)
