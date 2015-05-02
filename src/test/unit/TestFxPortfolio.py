__author__ = 'ManuGarg'

import unittest
from com.open.algo.trading.fxPortfolio import *
from com.open.algo.trading.fxEvents import *

class TestFxPortfolio(unittest.TestCase):

    def setUp(self):
        self.portfolio = FxPortfolio('USD')

    def test_portfolio_yields_positions_list_with_1_item_when_appended_executed_order(self):
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio.append_position(executed_order)
        self.assertEqual(len(self.portfolio.list_positions()), 1)

    def test_portfolio_yields_positions_list_with_1_item_when_appended_2_executed_order(self):
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.15, 50)
        self.portfolio.append_position(executed_order2)
        self.assertEqual(len(self.portfolio.list_positions()), 1)

    def test_portfolio_yields_executions_list_with_2_matching_executions_when_appended_2_executions(self):
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.15, 50)
        self.portfolio.append_position(executed_order2)
        executions = self.portfolio.list_executions()
        self.assertEqual(executed_order1, executions[0])
        self.assertEqual(executed_order2, executions[1])

    def test_portfolio_yields_position_with_expected_units_when_appended_2_executed_buy_and_sell_order(self):
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'sell'), 1.15, 50)
        self.portfolio.append_position(executed_order2)
        self.assertEqual(50, self.portfolio.list_position('CHF_USD'))





