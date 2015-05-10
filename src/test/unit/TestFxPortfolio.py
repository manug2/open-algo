__author__ = 'ManuGarg'

import unittest
from com.open.algo.trading.fxPortfolio import *
from com.open.algo.trading.fxEvents import *
from com.open.algo.trading.fxPricesCache import FxPricesCache
from com.open.algo.utils import get_time
from com.open.algo.risk.ccyExposureLimitRisk import CcyExposureLimitRiskEvaluator


class TestFxPortfolio(unittest.TestCase):

    def setUp(self):
        self.portfolio = FxPortfolio('USD')
        self.cache = FxPricesCache()

    def test_portfolio_yields_positions_list_with_1_item_when_appended_executed_order(self):
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio.append_position(executed_order)
        self.assertEqual(len(self.portfolio.list_positions()), 1)

    def test_portfolio_yields_positions_list_with_1_item_when_appended_2_executed_order(self):
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 50, 'buy'), 1.15, 50)
        self.portfolio.append_position(executed_order2)
        self.assertEqual(len(self.portfolio.list_positions()), 1)

    def test_portfolio_yields_executions_list_with_2_matching_executions_when_appended_2_executions(self):
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 50, 'buy'), 1.15, 50)
        self.portfolio.append_position(executed_order2)
        executions = self.portfolio.list_executions()
        self.assertEqual(executed_order1, executions[0])
        self.assertEqual(executed_order2, executions[1])

    def test_portfolio_yields_position_with_expected_units_when_appended_2_executed_buy_and_sell_order(self):
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 50, 'sell'), 1.15, 50)
        self.portfolio.append_position(executed_order2)
        self.assertEqual(50, self.portfolio.list_position('CHF_USD'))

    def test_portfolio_should_re_evaluate_long_position_when_new_market_rate_goes_up(self):
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        cache = FxPricesCache()
        portfolio = FxPortfolio('USD', cache)
        portfolio.append_position(executed_order)
        cache.set_rate(TickEvent('CHF_USD', get_time(), 1.2, 1.3))
        revalued = portfolio.reval_position('CHF_USD')
        self.assertEqual(20, revalued)

    def test_portfolio_should_give_average_execution_price_long_only(self):
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        cache = FxPricesCache()
        portfolio = FxPortfolio('USD', cache)
        portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.2, 100)
        portfolio.append_position(executed_order2)
        expected = round((100*1.1 + 100*1.2)/200, 2)
        self.assertEqual(expected, portfolio.get_avg_price('CHF_USD'))

    def test_portfolio_re_evaluates_all_positions_after_1_order_is_executed(self):
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        cache = FxPricesCache()
        cache.set_rate(TickEvent('CHF_USD', get_time(), 1.21, 1.22))
        portfolio = FxPortfolio('USD', cache, CcyExposureLimitRiskEvaluator('USD', cache))
        portfolio.append_position(executed_order)
        expected = round(100/1.22 - 100, 2)
        self.assertEqual(expected, portfolio.reval_positions())

    def test_portfolio_re_evaluates_all_positions_after_2_orders_are_executed_net_long(self):
        cache = FxPricesCache()
        portfolio = FxPortfolio('USD', cache, CcyExposureLimitRiskEvaluator('USD', cache))
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 50, 'sell'), 1.15, 50)
        portfolio.append_position(executed_order2)
        cache.set_rate(TickEvent('CHF_USD', get_time(), 1.21, 1.22))
        expected = round(50/1.22 - 50, 2)
        self.assertEqual(expected, portfolio.reval_positions())

    def test_portfolio_re_evaluates_all_positions_after_2_orders_are_executed_in_diff_ccy(self):
        cache = FxPricesCache()
        portfolio = FxPortfolio('USD', cache, CcyExposureLimitRiskEvaluator('USD', cache))
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('EUR_USD', 100, 'buy'), 0.9, 100)
        portfolio.append_position(executed_order2)
        cache.set_rate(TickEvent('CHF_USD', get_time(), 1.21, 1.22))
        cache.set_rate(TickEvent('EUR_USD', get_time(), 0.91, 0.92))
        expected = round(100/1.22 + 100/0.92 - 200, 2)
        self.assertEqual(expected, portfolio.reval_positions())

    def test_portfolio_re_evaluates_all_positions_after_2_orders_are_executed_in_diff_ccy_buy_sell(self):
        cache = FxPricesCache()
        portfolio = FxPortfolio('USD', cache, CcyExposureLimitRiskEvaluator('USD', cache))
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('EUR_USD', 50, 'sell'), 0.9, 50)
        portfolio.append_position(executed_order2)
        cache.set_rate(TickEvent('CHF_USD', get_time(), 1.21, 1.22))
        cache.set_rate(TickEvent('EUR_USD', get_time(), 0.91, 0.92))
        expected = round(100/1.22 - 50/0.91 - 50, 2)
        self.assertEqual(expected, portfolio.reval_positions())

    def test_portfolio_re_evaluates_all_positions_after_2_orders_are_executed_net_short(self):
        cache = FxPricesCache()
        portfolio = FxPortfolio('USD', cache, CcyExposureLimitRiskEvaluator('USD', cache))
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'sell'), 1.1, 100)
        portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 50, 'buy'), 1.15, 50)
        portfolio.append_position(executed_order2)
        cache.set_rate(TickEvent('CHF_USD', get_time(), 1.21, 1.22))
        expected = round(-50/1.21 + 50, 2)
        self.assertEqual(expected, portfolio.reval_positions())

    def test_should_not_allow_ccy_exposure_manager_of_different_base_ccy(self):
        try:
            FxPortfolio('USD', ccy_exposure_manager=CcyExposureLimitRiskEvaluator('CHF', self.cache))
        except ValueError:
            pass
