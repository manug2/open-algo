import sys

sys.path.append('../../main')
import unittest

from com.open.algo.utils import get_time
from com.open.algo.dummy import DummyBuyStrategy
from com.open.algo.trading.fxEvents import *
from com.open.algo.utils import EVENT_TYPES_ORDER
from queue import Queue
from com.open.algo.wiring.eventLoop import EventLoop
from threading import Thread
from testUtils import *
from com.open.algo.strategy import StrategyOrderManager


class TestDummyBuyStrategy(unittest.TestCase):
    def setUp(self):

        self.ticks_and_ack_q = Queue()
        self.signal_output_q = Queue()
        self.strategy = StrategyOrderManager(DummyBuyStrategy(), 100)
        self.strategy_loop = EventLoop(self.ticks_and_ack_q, self.strategy, processed_event_q=self.signal_output_q)
        self.strategy_thread = Thread(target=self.strategy_loop.start, args=[])

        # ticks and events for testing
        self.tick = TickEvent('EUR_GBP', get_time(), 0.87, 0.88)

    def tearDown(self):
        self.strategy_loop.stop()
        self.strategy_thread.join(MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)

    def test_should_output_signals(self):
        self.strategy_thread.start()
        self.ticks_and_ack_q.put_nowait(self.tick)

        order = await_event_receipt(self, self.signal_output_q, 'should receive one order in output q')
        self.assertEquals(self.tick.instrument, order.instrument)
        self.assertEquals(EVENT_TYPES_ORDER, order.TYPE)
        self.assertEquals(self.strategy.units, order.units)

