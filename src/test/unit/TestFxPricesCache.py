__author__ = 'ManuGarg'


import unittest
from com.open.algo.trading.fxPricesCache import FxPricesCache
from com.open.algo.trading.fxEvents import TickEvent
from com.open.algo.utils import get_time
from com.open.algo.eventLoop import EventLoop

from queue import Queue
import threading, time


class TestFxPricesCache(unittest.TestCase):

    def setUp(self):
        self.cache = FxPricesCache()

    def test_prices_cache_exists(self):
        self.assertIsNotNone(FxPricesCache())

    def test_can_append_rate(self):
        cache = FxPricesCache()
        cache.set_rate(TickEvent('CHF_USD', get_time(), 1.1, 1.2))

    def test_should_have_appended_rate(self):
        cache = FxPricesCache()
        cache.set_rate(TickEvent('CHF_USD', get_time(), 1.1, 1.2))
        rates = cache.get_rate('CHF_USD')
        self.assertEqual(1.1, rates['bid'])
        self.assertEqual(1.2, rates['ask'])

    def test_should_have_appended_rate_tuple(self):
        cache = FxPricesCache()
        cache.set_rate(TickEvent('CHF_USD', get_time(), 1.1, 1.2))
        rates = cache.get_rate_tuple('CHF_USD')
        self.assertEqual((1.1, 1.2), rates)

    def test_should_have_latest_of_twice_appended_rate(self):
        cache = FxPricesCache()
        cache.set_rate(TickEvent('CHF_USD', get_time(), 1.1, 1.2))
        cache.set_rate(TickEvent('CHF_USD', get_time(), 1.15, 1.25))
        rates = cache.get_rate('CHF_USD')
        self.assertEqual(1.15, rates['bid'])
        self.assertEqual(1.25, rates['ask'])

    def test_should_have_latest_of_twice_appended_rate_tuple(self):
        cache = FxPricesCache()
        cache.set_rate(TickEvent('CHF_USD', get_time(), 1.1, 1.2))
        cache.set_rate(TickEvent('CHF_USD', get_time(), 1.15, 1.25))
        rates = cache.get_rate_tuple('CHF_USD')
        self.assertEqual((1.15, 1.25), rates)

    def test_should_give_error_when_rate_not_set(self):
        cache = FxPricesCache()
        try:
            cache.get_rate('CHF_USD')
        except KeyError:
            pass

    def test_should_give_error_when_rate_tuple_not_set(self):
        cache = FxPricesCache()
        try:
            cache.get_rate_tuple('CHF_USD')
        except KeyError:
            pass

    def play_event_loop(self, tick):
        events = Queue()
        cache = FxPricesCache()
        looper = EventLoop(events, cache)

        price_thread = threading.Thread(target=looper.start, args=[])
        price_thread.start()

        events.put(tick)
        time.sleep(0.2)
        looper.stop()
        price_thread.join(timeout=0.2)
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

    def test_give_unity_for_same_ccy(self):
        self.assertEqual(self.cache.get_rate('CHF_CHF'), {'bid': 1.0, 'ask': 1.0})

    def test_give_unity_tuple_for_same_ccy(self):
        self.assertEqual(self.cache.get_rate_tuple('CHF_CHF'), (1.0, 1.0))

    def test_can_warn_if_rates_are_not_current_in_live_trading_mode(self):
        self.fail('Not implemented')
