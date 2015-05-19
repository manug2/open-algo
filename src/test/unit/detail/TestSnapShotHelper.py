__author__ = 'ManuGarg'

import unittest
from com.open.algo.trading.fxPortfolio import *
from com.open.algo.trading.fxEvents import *
from com.open.algo.snapShotHelper import SnapShotHelper


class TestPortfolioCreate(unittest.TestCase):

    def setUp(self):
        self.executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio = FxPortfolio('USD')
        self.portfolio.append_position(self.executed_order)
        self.snap_shot_helper = SnapShotHelper()

    def test_should_have_realized_pnl_in_snap_shot(self):
        snap_shot = self.snap_shot_helper.create_portfolio_snap_shot(self.portfolio)
        self.assertTrue('realized pnl' in snap_shot)

    def test_should_have_open_positions_in_snap_shot(self):
        snap_shot = self.snap_shot_helper.create_portfolio_snap_shot(self.portfolio)
        self.assertTrue('positions' in snap_shot)

    def test_should_have_executions_in_snap_shot(self):
        snap_shot = self.snap_shot_helper.create_portfolio_snap_shot(self.portfolio)
        self.assertTrue('executions' in snap_shot)

    def test_should_have_average_price_in_snap_shot(self):
        snap_shot = self.snap_shot_helper.create_portfolio_snap_shot(self.portfolio)
        self.assertTrue('avg price' in snap_shot)

    def test_should_have_0_realized_pnl_in_snap_shot(self):
        snap_shot = self.snap_shot_helper.create_portfolio_snap_shot(self.portfolio)
        self.assertEqual(0.0, snap_shot['realized pnl'])

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
        self.assertDictEqual({'CHF_USD': self.executed_order.price}, snap_shot['avg price'])


class TestPortfolioLoad(unittest.TestCase):

    def setUp(self):
        self.executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)
        self.portfolio = FxPortfolio('USD')
        self.snap_shot_helper = SnapShotHelper()
        self.snap_shot = dict()
        self.snap_shot['positions'] = {'CHF_USD', 100}
        self.snap_shot['executions'] = [self.executed_order]
        self.snap_shot['realized pnl'] = 1.4
        self.snap_shot['avg price'] = {'CHF_USD', 1.1}

