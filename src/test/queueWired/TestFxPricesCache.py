__author__ = 'ManuGarg'


import sys
sys.path.append('../../main')

import unittest
from com.open.algo.trading.fxPricesCache import FxPricesCache
from com.open.algo.trading.fxEvents import TickEvent
from com.open.algo.utils import get_time
from com.open.algo.wiring.eventLoop import EventLoop

from queue import Queue
from time import sleep
from threading import Thread


class TestFxPricesCache(unittest.TestCase):

    def setUp(self):
        self.cache = FxPricesCache()

    def play_event_loop(self, tick):
        events = Queue()
        cache = FxPricesCache()
        looper = EventLoop(events, cache)

        price_thread = Thread(target=looper.start, args=[])
        price_thread.start()

        events.put(tick)
        sleep(2*looper.heartbeat)
        looper.stop()
        price_thread.join(timeout=2*looper.heartbeat)
        return cache

    def test_should_give_correct_rates_after_event_is_queued_using_event_loop(self):
        cache = self.play_event_loop(TickEvent('EUR_GBP', get_time(), 0.87, 0.88))
        rates = cache.get_rate('EUR_GBP')
        self.assertEqual(0.87, rates['bid'])
        self.assertEqual(0.88, rates['ask'])

    def test_should_give_correct_rate_tuple_after_event_is_queued_using_event_loop(self):
        cache = self.play_event_loop(TickEvent('EUR_GBP', get_time(), 0.87, 0.88))
        rates = cache.get_rate_tuple('EUR_GBP')
        self.assertEqual((0.87, 0.88), rates)

