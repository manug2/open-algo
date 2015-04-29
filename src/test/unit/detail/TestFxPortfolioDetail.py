__author__ = 'ManuGarg'

import unittest
from com.open.algo.trading.fxPortfolio import *
from com.open.algo.trading.fxEvents import *


class TestFxPortfolio(unittest.TestCase):

    def setUp(self):
        pass

    def test_portfolio_module_exists(self):
        FxPortfolio()

    def test_portfolio_yields_empty_list_when_no_trade_exists(self):
        portfolio = FxPortfolio()
        self.assertIsNotNone(portfolio.list_positions())
        self.assertEqual(0, len(portfolio.list_positions()))

    def test_portfolio_can_append_executed_order(self):
        portfolio = FxPortfolio()
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        portfolio.append_position(executed_order)

    def test_portfolio_yields_not_none_positions_list_when_appended_executed_order(self):
        portfolio = FxPortfolio()
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        portfolio.append_position(executed_order)
        self.assertIsNotNone(portfolio.list_positions())

    def test_portfolio_yields_non_empty_positions_list_when_appended_executed_order(self):
        portfolio = FxPortfolio()
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        portfolio.append_position(executed_order)
        self.assertIsNotNone(portfolio.list_positions())
        self.assertTrue(len(portfolio.list_positions()) > 0)

    def test_portfolio_yields_not_none_executions_list_when_appended_executed_order(self):
        portfolio = FxPortfolio()
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        portfolio.append_position(executed_order)
        self.assertIsNotNone(portfolio.list_executions())

    def test_portfolio_yields_non_empty_executions_list_when_appended_executed_order(self):
        portfolio = FxPortfolio()
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        portfolio.append_position(executed_order)
        self.assertIsNotNone([], portfolio.list_positions())
        self.assertTrue(len(portfolio.list_executions()) > 0)

    def test_portfolio_yields_executions_list_with_1_item_when_appended_executed_order(self):
        portfolio = FxPortfolio()
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        portfolio.append_position(executed_order)
        self.assertEqual(len(portfolio.list_executions()), 1)

    def test_portfolio_yields_executions_list_with_2_items_when_appended_2_executed_order(self):
        portfolio = FxPortfolio()
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.15, 50)
        portfolio.append_position(executed_order2)
        self.assertEqual(len(portfolio.list_executions()), 2)

    def test_portfolio_yields_position_with_expected_units_when_appended_executed_order(self):
        portfolio = FxPortfolio()
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        portfolio.append_position(executed_order)
        self.assertEqual(100, portfolio.list_position('CHF_USD'))

    def test_portfolio_yields_position_with_expected_units_when_appended_2_executed_order(self):
        portfolio = FxPortfolio()
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.15, 50)
        portfolio.append_position(executed_order2)
        self.assertEqual(150, portfolio.list_position('CHF_USD'))

    def test_portfolio_yields_position_with_expected_units_when_appended_2_executed_buy_and_sell_order_negative_pos(self):
        portfolio = FxPortfolio()
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'sell'), 1.1, 100)
        portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 50, 'buy'), 1.15, 50)
        portfolio.append_position(executed_order2)
        self.assertEqual(-50, portfolio.list_position('CHF_USD'))




