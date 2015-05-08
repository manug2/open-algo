__author__ = 'ManuGarg'

import unittest
from com.open.algo.trading.fxPortfolio import *
from com.open.algo.trading.fxEvents import *
from com.open.algo.trading.fxPricesCache import FxPricesCache
from com.open.algo.model import gettime


class TestFxPortfolio(unittest.TestCase):

    def setUp(self):
        pass

    def test_portfolio_module_exists(self):
        FxPortfolio('USD')

    def test_portfolio_yields_empty_list_when_no_trade_exists(self):
        portfolio = FxPortfolio('USD')
        self.assertIsNotNone(portfolio.list_positions())
        self.assertEqual(0, len(portfolio.list_positions()))

    def test_portfolio_can_append_executed_order(self):
        portfolio = FxPortfolio('USD')
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        portfolio.append_position(executed_order)

    def test_portfolio_yields_not_none_positions_list_when_appended_executed_order(self):
        portfolio = FxPortfolio('USD')
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        portfolio.append_position(executed_order)
        self.assertIsNotNone(portfolio.list_positions())

    def test_portfolio_yields_non_empty_positions_list_when_appended_executed_order(self):
        portfolio = FxPortfolio('USD')
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        portfolio.append_position(executed_order)
        self.assertIsNotNone(portfolio.list_positions())
        self.assertTrue(len(portfolio.list_positions()) > 0)

    def test_portfolio_yields_not_none_executions_list_when_appended_executed_order(self):
        portfolio = FxPortfolio('USD')
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        portfolio.append_position(executed_order)
        self.assertIsNotNone(portfolio.list_executions())

    def test_portfolio_yields_non_empty_executions_list_when_appended_executed_order(self):
        portfolio = FxPortfolio('USD')
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        portfolio.append_position(executed_order)
        self.assertIsNotNone([], portfolio.list_positions())
        self.assertTrue(len(portfolio.list_executions()) > 0)

    def test_portfolio_yields_executions_list_with_1_item_when_appended_executed_order(self):
        portfolio = FxPortfolio('USD')
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        portfolio.append_position(executed_order)
        self.assertEqual(len(portfolio.list_executions()), 1)

    def test_portfolio_yields_executions_list_with_2_items_when_appended_2_executed_order(self):
        portfolio = FxPortfolio('USD')
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.15, 50)
        portfolio.append_position(executed_order2)
        self.assertEqual(len(portfolio.list_executions()), 2)

    def test_portfolio_yields_position_with_expected_units_when_appended_executed_order(self):
        portfolio = FxPortfolio('USD')
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        portfolio.append_position(executed_order)
        self.assertEqual(100, portfolio.list_position('CHF_USD'))

    def test_portfolio_yields_position_with_expected_units_when_appended_2_executed_order(self):
        portfolio = FxPortfolio('USD')
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.15, 50)
        portfolio.append_position(executed_order2)
        self.assertEqual(150, portfolio.list_position('CHF_USD'))

    def test_portfolio_yields_position_with_expected_units_when_appended_2_executed_buy_and_sell_order_negative_pos(self):
        portfolio = FxPortfolio('USD')
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'sell'), 1.1, 100)
        portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 50, 'buy'), 1.15, 50)
        portfolio.append_position(executed_order2)
        self.assertEqual(-50, portfolio.list_position('CHF_USD'))

    def test_portfolio_should_give_average_execution_price_long_short(self):
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        cache = FxPricesCache()
        portfolio = FxPortfolio('USD', cache)
        portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 50, 'sell'), 1.2, 50)
        portfolio.append_position(executed_order2)
        expected = round((100*1.1 - 50*1.2)/50, 2)
        self.assertEqual(50, portfolio.list_position('CHF_USD'))
        self.assertEqual(expected, portfolio.get_avg_price('CHF_USD'))

    def test_portfolio_should_give_average_execution_price_short_long(self):
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 50, 'sell'), 1.1, 50)
        cache = FxPricesCache()
        portfolio = FxPortfolio('USD', cache)
        portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.2, 100)
        portfolio.append_position(executed_order2)
        expected = round((-50*1.1 + 100*1.2)/50, 2)
        self.assertEqual(50, portfolio.list_position('CHF_USD'))
        self.assertEqual(expected, portfolio.get_avg_price('CHF_USD'))

    def test_portfolio_should_give_average_execution_price_long_less_than_short(self):
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        cache = FxPricesCache()
        portfolio = FxPortfolio('USD', cache)
        portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 150, 'sell'), 1.2, 150)
        portfolio.append_position(executed_order2)
        expected = abs(round((100*1.1 - 150*1.2)/50, 2))
        self.assertEqual(-50, portfolio.list_position('CHF_USD'))
        self.assertEqual(expected, portfolio.get_avg_price('CHF_USD'))

    def test_portfolio_should_give_average_execution_price_short_only(self):
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'sell'), 1.1, 100)
        cache = FxPricesCache()
        portfolio = FxPortfolio('USD', cache)
        portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'sell'), 1.2, 100)
        portfolio.append_position(executed_order2)
        expected = abs(round((-100*1.1 - 100*1.2)/200, 2))
        self.assertEqual(expected, portfolio.get_avg_price('CHF_USD'))

    def test_portfolio_should_re_evaluate_short_position_when_new_market_rate_goes_up(self):
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'sell'), 1.1, 100)
        cache = FxPricesCache()
        portfolio = FxPortfolio('USD', cache)
        portfolio.append_position(executed_order)
        cache.set_rate(TickEvent('CHF_USD', gettime(), 1.2, 1.3))
        revalued = portfolio.reval_position('CHF_USD')
        self.assertEqual(-10, revalued)

    def test_portfolio_should_re_evaluate_long_position_when_new_market_rate_goes_down(self):
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        cache = FxPricesCache()
        portfolio = FxPortfolio('USD', cache)
        portfolio.append_position(executed_order)
        cache.set_rate(TickEvent('CHF_USD', gettime(), 1.051, 1.064))
        revalued = portfolio.reval_position('CHF_USD')
        expected = round(100 * (1.064-1.1), 2)
        self.assertEqual(expected, revalued)

    def test_portfolio_should_re_evaluate_short_position_when_new_market_rate_goes_down(self):
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'sell'), 1.1, 100)
        cache = FxPricesCache()
        portfolio = FxPortfolio('USD', cache)
        portfolio.append_position(executed_order)
        cache.set_rate(TickEvent('CHF_USD', gettime(), 1.051, 1.064))
        revalued = portfolio.reval_position('CHF_USD')
        expected = round(-100 * (1.051-1.1), 2)
        self.assertEqual(expected, revalued)


