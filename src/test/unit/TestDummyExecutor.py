import sys

sys.path.append('../../main')
import unittest

from com.open.algo.dummy import DummyExecutor
from com.open.algo.trading.fxEvents import *


class TestDummyExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = DummyExecutor()
        self.buy_order = OrderEvent('EUR_USD', 1000, ORDER_SIDE_BUY)
        self.executed_order = ExecutedOrder(self.buy_order, 1.0, self.buy_order.units)

    def test_should_return_executed_order(self):
        executed_order = self.executor.execute_order(self.buy_order)
        self.assertEquals(self.buy_order, executed_order.order)
        self.assertEquals(self.executed_order, executed_order)
