__author__ = 'ManuGarg'

import unittest
from com.open.algo.trading.fxPortfolio import *
from com.open.algo.trading.fxEvents import *
from com.open.algo.trading.fxPricesCache import FxPricesCache
from com.open.algo.utils import get_time
from com.open.algo.risk.ccyExposureLimitRisk import CcyExposureLimitRiskEvaluator
from queue import Queue, Empty


class TestFxPortfolio(unittest.TestCase):

    def setUp(self):
        self.portfolio = FxPortfolio('USD', 5000)
        self.cache = FxPricesCache()
        self.ccy_exposure_manager = CcyExposureLimitRiskEvaluator('USD', self.cache)
        self.portfolio.set_price_cache(self.cache)
        self.portfolio.set_ccy_exposure_manager(self.ccy_exposure_manager)
        self.order_q = Queue()
        self.portfolio.set_order_q(self.order_q)

        self.large_buy_order = OrderEvent('EUR_USD', 1000000000, 'buy')
        self.large_sell_order = OrderEvent('EUR_USD', 1000000000, 'sell')

        self.buy_order = OrderEvent('EUR_USD', 1000, 'buy')
        self.sell_order = OrderEvent('EUR_USD', 1000, 'sell')

    def test_should_reduce_units_of_very_large_buy_order(self):
        self.cache.set_rate(TickEvent('EUR_USD', get_time(), 1.0, 1.0))
        try:
            filtered_order = self.portfolio.check_order(self.large_buy_order)
            self.assertEqual(self.ccy_exposure_manager.ccy_limit, filtered_order.units)
        except RuntimeError as e:
            self.fail('Expecting a filtered order per currency manager\'s limit, but got exception - [%s]' % e)

    def test_should_reduce_units_of_very_large_sell_order(self):
        self.cache.set_rate(TickEvent('EUR_USD', get_time(), 1.0, 1.0))
        try:
            filtered_order = self.portfolio.check_order(self.large_sell_order)
            self.assertEqual(self.ccy_exposure_manager.ccy_limit_short, -1 * filtered_order.units)
        except RuntimeError as e:
            self.fail('Expecting a filtered order per currency manager\'s limit, but got exception - [%s]' % e)

    def test_should_return_correct_order_after_checking(self):
        self.cache.set_rate(TickEvent('EUR_USD', get_time(), 1.0, 1.0))
        try:
            filtered_order = self.portfolio.check_order(self.buy_order)
            self.assertEqual(self.buy_order.units, filtered_order.units)
            self.assertEqual(self.buy_order.instrument, filtered_order.instrument)
            self.assertEqual(self.buy_order.side, filtered_order.side)
            self.assertEqual(self.buy_order.order_type, filtered_order.order_type)
        except RuntimeError as e:
            self.fail('Expecting a filtered order per currency manager\'s limit, but got exception - [%s]' % e)

    def test_should_send_buy_order_to_queue(self):
        self.cache.set_rate(TickEvent('EUR_USD', get_time(), 1.0, 1.0))
        order = self.buy_order
        try:
            self.portfolio.check_and_issue_order(order)
            try:
                order_for_execution = self.order_q.get_nowait()
                self.assertEqual(order.units, order_for_execution.units)
                self.assertEqual(order.instrument, order_for_execution.instrument)
                self.assertEqual(order.side, order_for_execution.side)
                self.assertEqual(order.order_type, order_for_execution.order_type)
            except Empty:
                self.fail('Expecting order in queue but was empty - [%s]')
        except RuntimeError as e:
            self.fail('Expecting a filtered order per currency manager\'s limit, but got exception - [%s]' % e)

    def test_should_send_sell_order_to_queue(self):
        self.cache.set_rate(TickEvent('EUR_USD', get_time(), 1.0, 1.0))
        order = self.sell_order
        try:
            self.portfolio.check_and_issue_order(order)
            try:
                order_for_execution = self.order_q.get_nowait()
                self.assertEqual(order.units, order_for_execution.units)
                self.assertEqual(order.instrument, order_for_execution.instrument)
                self.assertEqual(order.side, order_for_execution.side)
                self.assertEqual(order.order_type, order_for_execution.order_type)
            except Empty:
                self.fail('Expecting order in queue but was empty - [%s]')
        except RuntimeError as e:
            self.fail('Expecting a filtered order per currency manager\'s limit, but got exception - [%s]' % e)

    def test_should_raise_error_when_order_queue_is_full(self):
        # fill a queue and use as portfolio order queue
        little_q = Queue(maxsize=1)
        little_q.put_nowait(self.buy_order)
        self.portfolio.set_order_q(little_q)

        self.cache.set_rate(TickEvent('EUR_USD', get_time(), 1.0, 1.0))
        try:
            self.portfolio.check_and_issue_order(self.sell_order)
            self.fail('Expecting exception due to full order queue, but was processed - [%s]')
        except RuntimeError as e:
            self.assertTrue(e.args[0].find('order execution queue is full') >= 0)
