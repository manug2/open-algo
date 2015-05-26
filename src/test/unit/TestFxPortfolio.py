__author__ = 'ManuGarg'

import unittest
from com.open.algo.trading.fxPortfolio import *
from com.open.algo.trading.fxEvents import *
from com.open.algo.trading.fxPricesCache import FxPricesCache
from com.open.algo.utils import get_time
from com.open.algo.risk.ccyExposureLimitRisk import CcyExposureLimitRiskEvaluator
from com.open.algo.risk.fxPositionLimitRisk import FxPositionLimitRiskEvaluator


class TestFxPortfolio(unittest.TestCase):

    def setUp(self):
        self.portfolio = FxPortfolio('USD', 5000)
        self.cache = FxPricesCache()
        self.ccy_exposure_manager = \
            CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit=5000, ccy_limit_short=-5000)
        self.portfolio.set_price_cache(self.cache)
        self.portfolio.set_ccy_exposure_manager(self.ccy_exposure_manager)

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

    def test_should_return_correct_order_after_processing(self):
        self.cache.set_rate(TickEvent('EUR_USD', get_time(), 1.0, 1.0))
        try:
            filtered_order = self.portfolio.process(self.buy_order)
            self.assertEqual(self.buy_order.units, filtered_order.units)
            self.assertEqual(self.buy_order.instrument, filtered_order.instrument)
            self.assertEqual(self.buy_order.side, filtered_order.side)
            self.assertEqual(self.buy_order.order_type, filtered_order.order_type)
        except RuntimeError as e:
            self.fail('Expecting a filtered order per currency manager\'s limit, but got exception - [%s]' % e)

    def test_should_reduce_units_of_large_buy_order_using_position_limit_manager(self):
        rm = FxPositionLimitRiskEvaluator(posLimit=100)
        self.portfolio.add_risk_manager(rm)
        order = OrderEvent('EUR_USD', 1000, 'buy')
        self.cache.set_rate(TickEvent('EUR_USD', get_time(), 1.0, 1.0))
        try:
            filtered_order = self.portfolio.check_order(order)
            self.assertEqual(rm.posLimit, filtered_order.units)
        except RuntimeError as e:
            self.fail('Expecting a filtered order per currency manager\'s limit, but got exception - [%s]' % e)

    def test_should_reduce_units_of_large_sell_order_using_position_limit_manager(self):
        rm = FxPositionLimitRiskEvaluator(posLimitShort=-100)
        self.portfolio.add_risk_manager(rm)
        order = OrderEvent('EUR_USD', 1000, 'sell')
        self.cache.set_rate(TickEvent('EUR_USD', get_time(), 1.0, 1.0))
        try:
            filtered_order = self.portfolio.check_order(order)
            self.assertEqual(rm.posLimitShort, -1 * filtered_order.units)
        except RuntimeError as e:
            self.fail('Expecting a filtered order per currency manager\'s limit, but got exception - [%s]' % e)

    def test_should_reduce_units_of_large_buy_order_using_ccy_exposure_manager_when_pos_limit_manager_is_generous(self):
        rm = FxPositionLimitRiskEvaluator(posLimit=1000000)
        self.portfolio.add_risk_manager(rm)
        self.cache.set_rate(TickEvent('EUR_USD', get_time(), 1.0, 1.0))
        try:
            filtered_order = self.portfolio.check_order(self.large_buy_order)
            self.assertEqual(self.ccy_exposure_manager.ccy_limit, filtered_order.units)
        except RuntimeError as e:
            self.fail('Expecting a filtered order per currency manager\'s limit, but got exception - [%s]' % e)

    def test_should_reduce_units_of_large_sell_order_using_ccy_exposure_manager_when_pos_limit_manager_is_generous(self):
        rm = FxPositionLimitRiskEvaluator(posLimitShort=-1000000)
        self.portfolio.add_risk_manager(rm)
        self.cache.set_rate(TickEvent('EUR_USD', get_time(), 1.0, 1.0))
        try:
            filtered_order = self.portfolio.check_order(self.large_sell_order)
            self.assertEqual(self.ccy_exposure_manager.ccy_limit_short, -1 * filtered_order.units)
        except RuntimeError as e:
            self.fail('Expecting a filtered order per currency manager\'s limit, but got exception - [%s]' % e)


