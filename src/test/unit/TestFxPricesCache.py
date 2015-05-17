__author__ = 'ManuGarg'


import sys
sys.path.append('../../main')

import unittest
from com.open.algo.trading.fxPricesCache import FxPricesCache
from com.open.algo.trading.fxEvents import TickEvent
from com.open.algo.utils import get_time
from com.open.algo.eventLoop import EventLoop

from queue import Queue
from time import sleep
from threading import Thread


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

    def test_give_unity_for_same_ccy(self):
        self.assertEqual(self.cache.get_rate('CHF_CHF'), {'bid': 1.0, 'ask': 1.0})

    def test_give_unity_tuple_for_same_ccy(self):
        self.assertEqual(self.cache.get_rate_tuple('CHF_CHF'), (1.0, 1.0))

    def test_should_not_accept_day_old_tick(self):
        cache = FxPricesCache()
        one_day_in_seconds = 86400
        one_day_ago = get_time(-1 * one_day_in_seconds)
        try:
            tick = TickEvent('CHF_USD', one_day_ago, 1.1, 1.2)
            cache.set_rate(tick)
            self.fail('FX price cache should not have accepted a day old tick - [%s]' % tick)
        except AssertionError:
            pass

    def test_should_not_accept_tick_older_than_max_acceptable_age(self):
        max_tick_age = 100
        cache = FxPricesCache(max_tick_age=max_tick_age)
        older_than_max_tick_age = get_time(-2 * max_tick_age)
        try:
            tick = TickEvent('CHF_USD', older_than_max_tick_age, 1.1, 1.2)
            cache.set_rate(tick)
            self.fail('FX price cache should not have accepted a tick older than [%s] seconds - [%s]'
                      % (max_tick_age, tick))
        except AssertionError:
            pass

    def test_accept_day_old_tick_if_less_than_max_acceptable_age(self):
        one_day_in_seconds = 86400
        cache = FxPricesCache(max_tick_age=2*one_day_in_seconds)
        one_day_ago = get_time(-1 * one_day_in_seconds)
        tick = TickEvent('CHF_USD', one_day_ago, 1.1, 1.2)
        cache.set_rate(tick)
