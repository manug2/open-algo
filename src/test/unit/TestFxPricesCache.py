__author__ = 'ManuGarg'


import unittest
from com.open.algo.trading.fxPricesCache import FxPricesCache
from com.open.algo.trading.fxEvents import TickEvent
from com.open.algo.model import gettime

import queue


class TestFxPricesCache(unittest.TestCase):

    def setUp(self):
        self.events = queue.Queue()
        self.cache = FxPricesCache(0.5, self.events)
        self.cache.started = True

    def test_prices_cache_exists(self):
        self.assertIsNotNone(FxPricesCache())

    def test_can_append_rate(self):
        cache = FxPricesCache()
        cache.set_rate(TickEvent('CHF_USD', gettime(), 1.1, 1.2))

    def test_should_have_appended_rate(self):
        cache = FxPricesCache()
        cache.set_rate(TickEvent('CHF_USD', gettime(), 1.1, 1.2))
        rates = cache.get_rate('CHF_USD')
        self.assertEqual(1.1, rates['bid'])
        self.assertEqual(1.2, rates['ask'])

    def test_should_have_appended_rate_tuple(self):
        cache = FxPricesCache()
        cache.set_rate(TickEvent('CHF_USD', gettime(), 1.1, 1.2))
        rates = cache.get_rate_tuple('CHF_USD')
        self.assertEqual((1.1, 1.2), rates)

    def test_should_have_latest_of_twice_appended_rate(self):
        cache = FxPricesCache()
        cache.set_rate(TickEvent('CHF_USD', gettime(), 1.1, 1.2))
        cache.set_rate(TickEvent('CHF_USD', gettime(), 1.15, 1.25))
        rates = cache.get_rate('CHF_USD')
        self.assertEqual(1.15, rates['bid'])
        self.assertEqual(1.25, rates['ask'])

    def test_should_have_latest_of_twice_appended_rate_tuple(self):
        cache = FxPricesCache()
        cache.set_rate(TickEvent('CHF_USD', gettime(), 1.1, 1.2))
        cache.set_rate(TickEvent('CHF_USD', gettime(), 1.15, 1.25))
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

    def test_should_give_correct_rates_after_event_is_queued(self):
        tick = TickEvent('EUR_GBP', gettime(), 0.87, 0.88)
        self.events.put(tick)
        self.cache.pull_process()
        rates = self.cache.get_rate('EUR_GBP')
        self.assertEqual(0.87, rates['bid'])
        self.assertEqual(0.88, rates['ask'])

    def test_should_give_correct_rate_tuple_after_event_is_queued(self):
        tick = TickEvent('EUR_GBP', gettime(), 0.87, 0.88)
        self.events.put(tick)
        self.cache.pull_process()
        rates = self.cache.get_rate_tuple('EUR_GBP')
        self.assertEqual((0.87, 0.88), rates)
