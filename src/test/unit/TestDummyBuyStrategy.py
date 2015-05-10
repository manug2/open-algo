import sys

sys.path.append('../../main')
import unittest
import queue

from com.open.algo.utils import get_time
from com.open.algo.dummy import *
from com.open.algo.trading.fxEvents import *
from com.open.algo.eventLoop import Journaler


class TestDummyBuyStrategy(unittest.TestCase):
    def setUp(self):
        self.events = queue.Queue()
        self.journaler = Journaler()
        self.strategy = DummyBuyStrategy(self.events, 100, self.journaler)

    def testSetup(self):
        pass

    def testCalcSignals(self):
        tick = TickEvent("EUR_GBP", get_time(), 0.87, 0.88)
        self.strategy.calculate_signals(tick)
        outEvent = self.journaler.get_last_event()
        self.assertEquals(tick.instrument, outEvent.instrument)
        self.assertEquals(outEvent.TYPE, 'ORDER')
        self.assertEquals(self.strategy.units, outEvent.units)


class TestRandomStrategy(unittest.TestCase):
    def setUp(self):
        self.events = queue.Queue()
        self.journaler = Journaler()
        self.strategy = BuyOrSellAt5thTickStrategy(self.events, 100, self.journaler)

    def testSetup(self):
        pass

    def testCalcSignalsWithOneEvent(self):
        tick = TickEvent("EUR_GBP", get_time(), 0.87, 0.88)
        self.strategy.calculate_signals(tick)
        outEvent = self.journaler.get_last_event()
        self.assertEquals(tick, outEvent)

    def testCalcSignalsWithOneEvent(self):
        for i in range(1, 5):
            tick = TickEvent("EUR_GBP", get_time(), 0.87 + i, 0.88 + i)
            self.strategy.calculate_signals(tick)
            outEvent = self.journaler.get_last_event()
            self.assertEquals(None, outEvent)

        tick = TickEvent("EUR_GBP", get_time(), 0.874, 0.885)
        self.strategy.calculate_signals(tick)
        outEvent = self.journaler.get_last_event()

        self.assertIsNotNone(outEvent)
        self.assertEquals(tick.instrument, outEvent.instrument)
        self.assertEquals(outEvent.TYPE, 'ORDER')
        self.assertEquals(self.strategy.units, outEvent.units)


