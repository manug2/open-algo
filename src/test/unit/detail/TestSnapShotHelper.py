__author__ = 'ManuGarg'

import unittest
from com.open.algo.trading.fxPortfolio import *
from com.open.algo.trading.fxEvents import *
from com.open.algo.snapShotHelper import SnapShotHelper


class TestPortfolioCreate(unittest.TestCase):

    def setUp(self):
        self.executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio = FxPortfolio('USD', 1000)
        self.portfolio.append_position(self.executed_order)
        self.snap_shot_helper = SnapShotHelper()

    def test_should_have_balance_in_snap_shot(self):
        snap_shot = self.snap_shot_helper.create_portfolio_snap_shot(self.portfolio)
        self.assertTrue('opening_balance' in snap_shot)
        self.assertEqual(self.portfolio.opening_balance, snap_shot['opening_balance'])

    def test_should_have_balance_in_snap_shot(self):
        snap_shot = self.snap_shot_helper.create_portfolio_snap_shot(self.portfolio)
        self.assertTrue('balance' in snap_shot)
        self.assertEqual(self.portfolio.get_balance(), snap_shot['balance'])

    def test_should_have_realized_pnl_in_snap_shot(self):
        snap_shot = self.snap_shot_helper.create_portfolio_snap_shot(self.portfolio)
        self.assertTrue('realized_pnl' in snap_shot)
        self.assertEqual(self.portfolio.get_realized_pnl(), snap_shot['realized_pnl'])

    def test_should_have_open_positions_in_snap_shot(self):
        snap_shot = self.snap_shot_helper.create_portfolio_snap_shot(self.portfolio)
        self.assertTrue('positions' in snap_shot)

    def test_should_have_executions_in_snap_shot(self):
        snap_shot = self.snap_shot_helper.create_portfolio_snap_shot(self.portfolio)
        self.assertTrue('executions' in snap_shot)

    def test_should_have_average_price_in_snap_shot(self):
        snap_shot = self.snap_shot_helper.create_portfolio_snap_shot(self.portfolio)
        self.assertTrue('avg_price' in snap_shot)

    def test_should_have_0_realized_pnl_in_snap_shot(self):
        snap_shot = self.snap_shot_helper.create_portfolio_snap_shot(self.portfolio)
        self.assertEqual(0.0, snap_shot['realized_pnl'])

    def test_should_have_correct_open_positions_in_snap_shot(self):
        snap_shot = self.snap_shot_helper.create_portfolio_snap_shot(self.portfolio)
        self.assertDictEqual({'CHF_USD': self.executed_order.units}, snap_shot['positions'])

    def test_should_have_correct_executions_in_snap_shot(self):
        snap_shot = self.snap_shot_helper.create_portfolio_snap_shot(self.portfolio)
        executions = list()
        executions.append(self.executed_order)
        self.assertListEqual(executions, snap_shot['executions'])

    def test_should_have_correct_avg_price_in_snap_shot(self):
        snap_shot = self.snap_shot_helper.create_portfolio_snap_shot(self.portfolio)
        self.assertDictEqual({'CHF_USD': self.executed_order.price}, snap_shot['avg_price'])


class TestPortfolioLoad(unittest.TestCase):

    def setUp(self):
        self.executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.snap_shot_helper = SnapShotHelper()
        self.snap_shot = dict()
        self.snap_shot['base_ccy'] = 'USD'
        self.snap_shot['opening_balance'] = 10000
        self.snap_shot['balance'] = 11000
        self.snap_shot['positions'] = {'CHF_USD', 100}
        self.snap_shot['executions'] = [self.executed_order]
        self.snap_shot['realized_pnl'] = 1.4
        self.snap_shot['avg_price'] = {'CHF_USD', 1.1}

    def test_should_load_portfolio_from_snap_shot(self):
        portfolio = self.snap_shot_helper.load_portfolio_snap_shot(self.snap_shot)
        self.assertIsNotNone(portfolio)

    def test_loaded_portfolio_should_have_correct_base_currency(self):
        portfolio = self.snap_shot_helper.load_portfolio_snap_shot(self.snap_shot)
        self.assertEqual(self.snap_shot['base_ccy'], portfolio.get_base_ccy())

    def test_loaded_portfolio_should_have_correct_opening_balance(self):
        portfolio = self.snap_shot_helper.load_portfolio_snap_shot(self.snap_shot)
        self.assertEqual(self.snap_shot['opening_balance'], portfolio.opening_balance)

    def test_loaded_portfolio_should_have_correct_balance(self):
        portfolio = self.snap_shot_helper.load_portfolio_snap_shot(self.snap_shot)
        self.assertEqual(self.snap_shot['balance'], portfolio.get_balance())

