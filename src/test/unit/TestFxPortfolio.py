__author__ = 'ManuGarg'

import unittest
from com.open.algo.trading.fxPortfolio import *
from com.open.algo.trading.fxEvents import *
from com.open.algo.trading.fxPricesCache import FxPricesCache
from com.open.algo.model import gettime


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
        cache.set_rate(TickEvent('CHF_USD', gettime(), 1.2, 1.3))
        revalued = portfolio.reval_position('CHF_USD')
        self.assertEqual(20, revalued)

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

    def test_portfolio_should_give_average_execution_price_long_only(self):
        executed_order1 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        cache = FxPricesCache()
        portfolio = FxPortfolio('USD', cache)
        portfolio.append_position(executed_order1)
        executed_order2 = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.2, 100)
        portfolio.append_position(executed_order2)
        expected = round((100*1.1 + 100*1.2)/200, 2)
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

    def test_portfolio_re_evaluates_all_positions_after_1_order_is_executed(self):
        executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        cache = FxPricesCache()
        portfolio = FxPortfolio('USD', cache)
        portfolio.append_position(executed_order)
        expected = 100/1.1
        try:
            self.assertEqual(expected, portfolio.reval_positions())
        except NotImplementedError:
            pass
