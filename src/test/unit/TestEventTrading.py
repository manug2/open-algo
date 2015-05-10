import unittest

from com.open.algo.trading.eventTrading import AlgoTrader
from com.open.algo.trading.fxEvents import *
from com.open.algo.utils import Journaler
from com.open.algo.eventLoop import EventLoop
from com.open.algo.dummy import *
import queue
from datetime import datetime


class TestStreamTrading(unittest.TestCase):
    def setUp(self):
        self.events = queue.Queue()
        self.journaler = Journaler()
        self.strategy = DummyBuyStrategy(self.events, 100, self.journaler)
        self.algo_trader = AlgoTrader(None, self.strategy, DummyExecutor())
        self.trader = EventLoop(self.events, self.algo_trader, 0.3, self.journaler)
        self.trader.started = True

    def testOrderGeneration(self):
        tick = TickEvent("EUR_GBP", str(datetime.now()), 0.87, 0.88)
        self.events.put(tick)
        self.trader.pull_process()

        outEvent = self.journaler.getLastEvent()
        self.assertEquals(tick.instrument, outEvent.instrument)
        self.assertEquals(outEvent.TYPE, 'ORDER')
        self.assertEquals(self.strategy.units, outEvent.units)


class TestStreamTradingRandom(unittest.TestCase):
    def setUp(self):
        self.events = queue.Queue()
        self.journaler = Journaler()
        self.strategy = BuyOrSellAt5thTickStrategy(self.events, 100, self.journaler)
        self.algo_trader = AlgoTrader(None, self.strategy, DummyExecutor())
        self.trader = EventLoop(self.events, self.algo_trader, 0.5, self.journaler)
        self.trader.started = True

    def testOrderGeneration(self):
        for i in range(1, 7):
            tick = TickEvent("EUR_GBP", str(datetime.now()), round(0.87 + (i / 100), 2), 0.88 + (i / 100))
            self.events.put(tick)

        self.trader.pull_process()

        outEvent = self.journaler.getLastEvent()
        self.assertEquals(tick.instrument, outEvent.instrument)
        self.assertEquals(outEvent.TYPE, 'ORDER')
        self.assertEquals(self.strategy.units, outEvent.units)

