import unittest
import sys

sys.path.append('../../main')

from com.open.algo.trading.eventTrading import ListenAndTradeBot
from com.open.algo.trading.fxEvents import *
from com.open.algo.utils import Journaler
from com.open.algo.dummy import *
import threading, time
import queue
from datetime import datetime


class TestStreamTrading(unittest.TestCase):
    def setUp(self):
        self.events = queue.Queue()
        self.journaler = Journaler()
        self.strategy = DummyBuyStrategy(self.events, 100, self.journaler)
        self.trader = ListenAndTradeBot(0.5, self.events, None, self.strategy, DummyExecutor())
        self.trader.trading = True

    def testOrderGeneration(self):
        tick = TickEvent("EUR_GBP", str(datetime.now()), 0.87, 0.88)
        self.events.put(tick)
        self.trader.pullAndProcess()

        outEvent = self.journaler.getLastEvent()
        self.assertEquals(tick.instrument, outEvent.instrument)
        self.assertEquals(outEvent.TYPE, 'ORDER')
        self.assertEquals(self.strategy.units, outEvent.units)


class TestStreamTradingRandom(unittest.TestCase):
    def setUp(self):
        self.events = queue.Queue()
        self.journaler = Journaler()
        self.strategy = RandomStrategy(self.events, 100, self.journaler)
        self.trader = ListenAndTradeBot(0.5, self.events, None, self.strategy, DummyExecutor())
        self.trader.trading = True

    def testOrderGeneration(self):
        for i in range(1, 7):
            tick = TickEvent("EUR_GBP", str(datetime.now()), 0.87 + (i / 100), 0.88 + (i / 100))
            self.events.put(tick)

        self.trader.pullAndProcess()

        outEvent = self.journaler.getLastEvent()
        self.assertEquals(tick.instrument, outEvent.instrument)
        self.assertEquals(outEvent.TYPE, 'ORDER')
        self.assertEquals(self.strategy.units, outEvent.units)

