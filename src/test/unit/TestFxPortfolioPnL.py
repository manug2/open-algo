__author__ = 'ManuGarg'

import unittest
from com.open.algo.trading.fxPortfolio import *
from com.open.algo.trading.fxEvents import *
from com.open.algo.trading.fxPricesCache import FxPricesCache
from com.open.algo.utils import get_time
from com.open.algo.risk.ccyExposureLimitRisk import CcyExposureLimitRiskEvaluator


class TestFxPortfolio(unittest.TestCase):

    def setUp(self):
        self.portfolio = FxPortfolio('USD', 5000)
        self.cache = FxPricesCache()
        self.ccy_exposure_manager = CcyExposureLimitRiskEvaluator('USD', self.cache)
        self.portfolio.set_price_cache(self.cache)
        self.portfolio.set_ccy_exposure_manager(self.ccy_exposure_manager)

        self.buy_100_CHF_USD = OrderEvent('CHF_USD', 100, 'buy')
        self.sell_100_CHF_USD = OrderEvent('CHF_USD', 100, 'sell')
        self.buy_50_CHF_USD = OrderEvent('CHF_USD', 50, 'buy')
        self.sell_50_CHF_USD = OrderEvent('CHF_USD', 50, 'sell')

        self.buy_100_EUR_USD = OrderEvent('EUR_USD', 100, 'buy')
        self.sell_100_EUR_USD = OrderEvent('EUR_USD', 100, 'sell')
        self.buy_50_EUR_USD = OrderEvent('EUR_USD', 50, 'buy')
        self.sell_50_EUR_USD = OrderEvent('EUR_USD', 50, 'sell')

    def test_should_yield_positions_list_with_1_item_when_appended_executed_order(self):
        executed_order = ExecutedOrder(self.buy_100_CHF_USD, 1.1, 100)
        self.portfolio.append_position(executed_order)
        self.assertEqual(len(self.portfolio.list_positions()), 1)

    def test_should_yield_positions_list_with_1_item_when_appended_2_executed_order(self):
        executed_order1 = ExecutedOrder(self.buy_100_CHF_USD, 1.1, 100)
        self.portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(self.buy_50_CHF_USD, 1.15, 50)
        self.portfolio.append_position(executed_order2)
        self.assertEqual(len(self.portfolio.list_positions()), 1)

    def test_should_yield_executions_list_with_2_matching_executions_when_appended_2_executions(self):
        executed_order1 = ExecutedOrder(self.buy_100_CHF_USD, 1.1, 100)
        self.portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(self.buy_50_CHF_USD, 1.15, 50)
        self.portfolio.append_position(executed_order2)
        executions = self.portfolio.list_executions()
        self.assertEqual(executed_order1, executions[0])
        self.assertEqual(executed_order2, executions[1])

    def test_should_yield_position_with_expected_units_when_appended_2_executed_buy_and_sell_order(self):
        executed_order1 = ExecutedOrder(self.buy_100_CHF_USD, 1.1, 100)
        self.portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(self.sell_50_CHF_USD, 1.15, 50)
        self.portfolio.append_position(executed_order2)
        self.assertEqual(50, self.portfolio.list_position('CHF_USD'))

    def test_should_re_evaluate_long_position_when_new_market_rate_goes_up(self):
        executed_order = ExecutedOrder(self.buy_100_CHF_USD, 1.1, 100)
        self.portfolio.append_position(executed_order)
        self.cache.set_rate(TickEvent('CHF_USD', get_time(), 1.2, 1.3))
        revalued = self.portfolio.reval_position('CHF_USD')
        self.assertEqual(20, revalued)

    def test_should_give_average_execution_price_long_only(self):
        executed_order1 = ExecutedOrder(self.buy_100_CHF_USD, 1.1, 100)
        self.portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(self.buy_100_CHF_USD, 1.2, 100)
        self.portfolio.append_position(executed_order2)
        expected = round((100*1.1 + 100*1.2)/200, 2)
        self.assertEqual(expected, self.portfolio.get_avg_price('CHF_USD'))

    def test_should_re_evaluates_all_positions_after_1_order_is_executed(self):
        executed_order = ExecutedOrder(self.buy_100_CHF_USD, 1.1, 100)
        self.cache.set_rate(TickEvent('CHF_USD', get_time(), 1.21, 1.22))
        self.portfolio.append_position(executed_order)
        expected = round(100/1.22 - 100, 2)
        self.assertEqual(expected, self.portfolio.reval_positions())

    def test_should_re_evaluates_all_positions_after_2_orders_are_executed_net_long(self):
        executed_order1 = ExecutedOrder(self.buy_100_CHF_USD, 1.1, 100)
        self.portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(self.sell_50_CHF_USD, 1.15, 50)
        self.portfolio.append_position(executed_order2)
        self.cache.set_rate(TickEvent('CHF_USD', get_time(), 1.21, 1.22))
        expected = round(50/1.22 - 50, 2)
        self.assertEqual(expected, self.portfolio.reval_positions())

    def test_should_re_evaluates_all_positions_after_2_orders_are_executed_in_diff_ccy(self):
        executed_order1 = ExecutedOrder(self.buy_100_CHF_USD, 1.1, 100)
        self.portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(self.buy_100_EUR_USD, 0.9, 100)
        self.portfolio.append_position(executed_order2)
        self.cache.set_rate(TickEvent('CHF_USD', get_time(), 1.21, 1.22))
        self.cache.set_rate(TickEvent('EUR_USD', get_time(), 0.91, 0.92))
        expected = round(100/1.22 + 100/0.92 - 200, 2)
        self.assertEqual(expected, self.portfolio.reval_positions())

    def test_should_re_evaluates_all_positions_after_2_orders_are_executed_in_diff_ccy_buy_sell(self):
        executed_order1 = ExecutedOrder(self.buy_100_CHF_USD, 1.1, 100)
        self.portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(self.sell_50_EUR_USD, 0.9, 50)
        self.portfolio.append_position(executed_order2)
        self.cache.set_rate(TickEvent('CHF_USD', get_time(), 1.21, 1.22))
        self.cache.set_rate(TickEvent('EUR_USD', get_time(), 0.91, 0.92))
        expected = round(100/1.22 - 50/0.91 - 50, 2)
        self.assertEqual(expected, self.portfolio.reval_positions())

    def test_should_re_evaluates_all_positions_after_2_orders_are_executed_net_short(self):
        executed_order1 = ExecutedOrder(self.sell_100_CHF_USD, 1.1, 100)
        self.portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(self.buy_50_CHF_USD, 1.15, 50)
        self.portfolio.append_position(executed_order2)
        self.cache.set_rate(TickEvent('CHF_USD', get_time(), 1.21, 1.22))
        expected = round(-50/1.21 + 50, 2)
        self.assertEqual(expected, self.portfolio.reval_positions())

    def test_should_not_allow_ccy_exposure_manager_of_different_base_ccy(self):
        try:
            portfolio = FxPortfolio('USD', 100)
            portfolio.set_ccy_exposure_manager(CcyExposureLimitRiskEvaluator('CHF', self.cache))
        except ValueError:
            pass

    def test_should_update_realized_pnl_when_appending_long_first_and_equal_short_second(self):
        executed_order = ExecutedOrder(self.buy_100_EUR_USD, 1.4, 100)
        executed_order2 = ExecutedOrder(self.sell_100_EUR_USD, 1.5, 100)
        self.portfolio.append_position(executed_order)
        self.portfolio.append_position(executed_order2)
        self.assertEqual(10, self.portfolio.get_realized_pnl())

    def test_should_update_realized_pnl_when_appending_short_first_and_equal_long_second(self):
        executed_order = ExecutedOrder(self.sell_100_EUR_USD, 1.4, 100)
        executed_order2 = ExecutedOrder(self.buy_100_EUR_USD, 1.5, 100)
        self.portfolio.append_position(executed_order)
        self.portfolio.append_position(executed_order2)
        self.assertEqual(10, self.portfolio.get_realized_pnl())

    def test_should_not_update_realized_pnl_when_execution_opposite_of_previously_open_position_but_diff_instrument(self):
        executed_order = ExecutedOrder(self.buy_100_EUR_USD, 1.4, 100)
        executed_order2 = ExecutedOrder(self.sell_100_CHF_USD, 1.1, 100)
        self.portfolio.append_position(executed_order)
        self.portfolio.append_position(executed_order2)
        self.assertEqual(0, self.portfolio.get_realized_pnl())

    def test_should_update_realized_pnl_when_closing_one_position_while_another_open_position_in_diff_instrument_exists(self):
        executed_order = ExecutedOrder(self.buy_100_EUR_USD, 1.4, 100)
        executed_order2 = ExecutedOrder(self.sell_100_CHF_USD, 1.1, 100)
        executed_order3 = ExecutedOrder(self.sell_100_EUR_USD, 1.45, 100)
        self.portfolio.append_position(executed_order)
        self.portfolio.append_position(executed_order2)
        self.portfolio.append_position(executed_order3)
        self.assertEqual(5, self.portfolio.get_realized_pnl())

    def test_should_update_negative_realized_pnl_when_appending_closing_position_at_loss(self):
        executed_order = ExecutedOrder(self.buy_100_EUR_USD, 1.4, 100)
        executed_order2 = ExecutedOrder(self.sell_100_EUR_USD, 1.3, 100)
        self.portfolio.append_position(executed_order)
        self.portfolio.append_position(executed_order2)
        self.assertEqual(-10, self.portfolio.get_realized_pnl())

    def test_should_have_zero_unrealized_pnl_after_closing_position(self):
        executed_order = ExecutedOrder(self.buy_100_EUR_USD, 1.4, 100)
        executed_order2 = ExecutedOrder(self.sell_100_EUR_USD, 1.3, 100)
        self.portfolio.append_position(executed_order)
        self.portfolio.append_position(executed_order2)
        self.cache.set_rate(TickEvent('EUR_USD', get_time(), 0.91, 0.92))
        self.assertEqual(0, self.portfolio.reval_positions())

    def test_should_have_correct_realized_pnl_after_partial_close(self):
        executed_order = ExecutedOrder(self.buy_100_EUR_USD, 1.4, 100)
        executed_order2 = ExecutedOrder(self.sell_50_EUR_USD, 1.3, 50)
        self.portfolio.append_position(executed_order)
        self.portfolio.append_position(executed_order2)
        self.cache.set_rate(TickEvent('EUR_USD', get_time(), 0.91, 0.92))
        self.assertEqual(-5, self.portfolio.get_realized_pnl())

    def test_should_have_correct_unrealized_pnl_after_partial_close(self):
        executed_order = ExecutedOrder(self.buy_100_EUR_USD, 0.905, 100)
        executed_order2 = ExecutedOrder(self.sell_50_EUR_USD, 0.900, 50)
        self.portfolio.append_position(executed_order)
        self.portfolio.append_position(executed_order2)
        self.cache.set_rate(TickEvent('EUR_USD', get_time(), 0.910, 0.920))
        expected = round(50/0.920 - 50, 2)
        self.assertEqual(expected, self.portfolio.reval_positions())
