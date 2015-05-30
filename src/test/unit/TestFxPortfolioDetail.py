__author__ = 'ManuGarg'

import unittest
from com.open.algo.trading.fxPortfolio import *
from com.open.algo.trading.fxEvents import *
from com.open.algo.trading.fxPricesCache import FxPricesCache
from com.open.algo.utils import get_time


class TestFxPortfolio(unittest.TestCase):

    def setUp(self):
        self.portfolio = FxPortfolio('USD', 10000)
        self.cache = FxPricesCache()
        self.portfolio.set_price_cache(self.cache)

    def test_should_yields_empty_list_when_no_trade_exists(self):
        self.assertIsNotNone(self.portfolio.list_positions())
        self.assertEqual(0, len(self.portfolio.list_positions()))

    def test_should_append_executed_order(self):
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio.append_position(executed_order)

    def test_should_yield_not_none_positions_list_when_appended_executed_order(self):
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio.append_position(executed_order)
        self.assertIsNotNone(self.portfolio.list_positions())

    def test_should_yield_non_empty_positions_list_when_appended_executed_order(self):
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio.append_position(executed_order)
        self.assertIsNotNone(self.portfolio.list_positions())
        self.assertTrue(len(self.portfolio.list_positions()) > 0)

    def test_should_yield_not_none_executions_list_when_appended_executed_order(self):
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio.append_position(executed_order)
        self.assertIsNotNone(self.portfolio.list_executions())

    def test_should_yield_non_empty_executions_list_when_appended_executed_order(self):
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio.append_position(executed_order)
        self.assertIsNotNone([], self.portfolio.list_positions())
        self.assertTrue(len(self.portfolio.list_executions()) > 0)

    def test_should_yield_executions_list_with_1_item_when_appended_executed_order(self):
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio.append_position(executed_order)
        self.assertEqual(len(self.portfolio.list_executions()), 1)

    def test_should_yield_executions_list_with_2_items_when_appended_2_executed_order(self):
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.15, 50)
        self.portfolio.append_position(executed_order2)
        self.assertEqual(len(self.portfolio.list_executions()), 2)

    def test_should_yield_position_with_expected_units_when_appended_executed_order(self):
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio.append_position(executed_order)
        self.assertEqual(100, self.portfolio.list_position('CHF_USD'))

    def test_should_yield_position_with_expected_units_when_appended_2_executed_order(self):
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.15, 50)
        self.portfolio.append_position(executed_order2)
        self.assertEqual(150, self.portfolio.list_position('CHF_USD'))

    def test_should_yield_position_with_expected_units_when_appended_2_executed_buy_and_sell_order_negative_pos(self):
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'sell'), 1.1, 100)
        self.portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 50, 'buy'), 1.15, 50)
        self.portfolio.append_position(executed_order2)
        self.assertEqual(-50, self.portfolio.list_position('CHF_USD'))

    def test_should_give_average_execution_price_long_short(self):
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 50, 'sell'), 1.2, 50)
        self.portfolio.append_position(executed_order2)
        expected = 1.1
        self.assertEqual(50, self.portfolio.list_position('CHF_USD'))
        self.assertEqual(expected, self.portfolio.get_avg_price('CHF_USD'))

    def test_should_give_average_execution_price_short_long(self):
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 50, 'sell'), 1.1, 50)
        self.portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.2, 100)
        self.portfolio.append_position(executed_order2)
        expected = 1.2
        self.assertEqual(50, self.portfolio.list_position('CHF_USD'))
        self.assertEqual(expected, self.portfolio.get_avg_price('CHF_USD'))

    def test_should_give_average_execution_price_long_less_than_short(self):
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 150, 'sell'), 1.2, 150)
        self.portfolio.append_position(executed_order2)
        expected = 1.2
        self.assertEqual(-50, self.portfolio.list_position('CHF_USD'))
        self.assertEqual(expected, self.portfolio.get_avg_price('CHF_USD'))

    def test_should_give_average_execution_price_short_only(self):
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'sell'), 1.1, 100)
        self.portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'sell'), 1.2, 100)
        self.portfolio.append_position(executed_order2)
        expected = abs(round((-100*1.1 - 100*1.2)/200, 2))
        self.assertEqual(expected, self.portfolio.get_avg_price('CHF_USD'))

    def test_should_re_evaluate_short_position_when_new_market_rate_goes_up(self):
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'sell'), 1.1, 100)
        self.portfolio.append_position(executed_order)
        self.cache.set_rate(TickEvent('CHF_USD', get_time(), 1.2, 1.3))
        revalued = self.portfolio.reval_position('CHF_USD')
        self.assertEqual(-10, revalued)

    def test_should_re_evaluate_long_position_when_new_market_rate_goes_down(self):
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio.append_position(executed_order)
        self.cache.set_rate(TickEvent('CHF_USD', get_time(), 1.051, 1.064))
        revalued = self.portfolio.reval_position('CHF_USD')
        expected = round(100 * (1.064-1.1), 2)
        self.assertEqual(expected, revalued)

    def test_should_re_evaluate_short_position_when_new_market_rate_goes_down(self):
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'sell'), 1.1, 100)
        self.portfolio.append_position(executed_order)
        self.cache.set_rate(TickEvent('CHF_USD', get_time(), 1.051, 1.064))
        revalued = self.portfolio.reval_position('CHF_USD')
        expected = round(-100 * (1.051-1.1), 2)
        self.assertEqual(expected, revalued)

    def test_should_have_portfolio_limit(self):
        self.assertIsNotNone(self.portfolio)

    def test_should_have_default_portfolio_limit(self):
        self.assertTrue(self.portfolio.port_limit > 0)

    def test_should_have_preset_portfolio_limit(self):
        portfolio = FxPortfolio('USD', 10000, port_limit=1230)
        self.assertEquals(portfolio.port_limit, 1230)

    def test_should_give_realized_pnl(self):
        self.assertIsNotNone(self.portfolio.get_realized_pnl())

    def test_should_have_balance(self):
        self.assertIsNotNone(self.portfolio.get_balance())
