import sys

sys.path.append('../../main')
import unittest

from com.open.algo.utils import get_time
from com.open.algo.dummy import *
from com.open.algo.strategy import StrategyOrderManager
from com.open.algo.trading.fxEvents import *
from com.open.algo.utils import EVENT_TYPES_ORDER


class TestDummyBuyStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = DummyBuyStrategy()

    def test_should_calculate_signals(self):
        self.assertEquals(ORDER_SIDE_BUY, self.strategy.calculate_signals('some tick'))

    def test_should_calculate_signals_for_two_ticks(self):
        self.assertEquals(ORDER_SIDE_BUY, self.strategy.calculate_signals('some tick'))
        self.assertEquals(ORDER_SIDE_BUY, self.strategy.calculate_signals('some new tick'))


class TestRandomStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = BuyOrSellAt5thTickStrategy()
        self.tick = 'some tick'

    def test_should_not_give_signal_on_first_tick(self):
        self.assertIsNone(self.strategy.calculate_signals(self.tick))

    def test_should_give_signal_when_calculating_5_ticks(self):
        for i in range(1, 5):
            self.assertEquals(None, self.strategy.calculate_signals(self.tick))

        signal = self.strategy.calculate_signals(self.tick)
        self.assertIsNotNone(signal)


class TestAlternateBuySellRandomStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = AlternateBuySellAt5thTickStrategy()
        self.tick = 'some tick'

    def test_should_not_give_signal_on_first_tick(self):
        self.assertIsNone(self.strategy.calculate_signals(self.tick))

    def test_should_give_buy_signal_when_calculating_5_ticks(self):
        for i in range(1, 5):
            self.strategy.calculate_signals(self.tick)

        signal = self.strategy.calculate_signals(self.tick)
        self.assertIsNotNone(signal)
        self.assertEquals(ORDER_SIDE_BUY, signal)

    def test_should_give_sell_signal_when_calculating_10_ticks(self):
        for i in range(1, 10):
            self.strategy.calculate_signals(self.tick)

        signal = self.strategy.calculate_signals(self.tick)
        self.assertIsNotNone(signal)
        self.assertEquals(ORDER_SIDE_SELL, signal)
