__author__ = 'ManuGarg'

import sys

sys.path.append('../../main')
import unittest
from com.open.algo.oanda.parser import parse_event_str
from com.open.algo.strategy import AbstractStrategy
from com.open.algo.strategies.crossOver import BidsMACrossoverStrategy
from com.open.algo.utils import get_time
from com.open.algo.calcs.ma import sma
from com.open.algo.trading.fxEvents import ORDER_SIDE_SELL, ORDER_SIDE_BUY, OrderEvent


class TestMACrossoverStrategyClass(unittest.TestCase):
    def setUp(self):
        self.strategy = BidsMACrossoverStrategy(2, 3)

        self.ticks = []
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.12404,"ask":1.1242}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:50:08.543570Z","bid":1.12403,"ask":1.12421}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:50:08.633262Z","bid":1.12406,"ask":1.12423}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:50:08.754773Z","bid":1.12405,"ask":1.12425}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:50:10.243141Z","bid":1.12411,"ask":1.12429}}')

    def test_should_default_period1(self):
        self.assertTrue(BidsMACrossoverStrategy().period1 > 0)

    def test_should_default_period2(self):
        self.assertTrue(BidsMACrossoverStrategy().period2 > 0)

    def test_should_default_period2_greater_than_period1(self):
        strategy = BidsMACrossoverStrategy()
        self.assertTrue(strategy.period2 > strategy.period1)

    def test_should_default_function_for_calculating_moving_average(self):
        self.assertEqual(BidsMACrossoverStrategy().ma_function, sma)

    def test_should_be_instance_of_AbstractStrategy(self):
        self.assertIsInstance(BidsMACrossoverStrategy(), AbstractStrategy)

    def test_should_not_allow_period2_equal_to_period1(self):
        try:
            BidsMACrossoverStrategy(5, 5)
            self.fail('should have failed when period1 = period2')
        except ValueError:
            pass

    def test_should_not_allow_period2_less_than_period1(self):
        try:
            BidsMACrossoverStrategy(15, 5)
            self.fail('should have failed when period1 > period2')
        except ValueError:
            pass

    def test_should_not_generate_order_after_one_tick_event(self):
        tick = parse_event_str(get_time(), self.ticks[0])
        order = self.strategy.calculate_signals(tick)
        self.assertIsNone(order)

    def test_should_not_generate_order_when_ticks_are_enough_for_period1_ma(self):
        for i in range(0, self.strategy.period1):
            tick = parse_event_str(get_time(), self.ticks[i])
            order = self.strategy.calculate_signals(tick)
            self.assertIsNone(order)

    def test_should_not_generate_order_when_ticks_are_not_enough_for_period2_ma(self):
        for i in range(0, self.strategy.period2 - 1):
            tick = parse_event_str(get_time(), self.ticks[i])
            order = self.strategy.calculate_signals(tick)
            self.assertIsNone(order)


class TestMACrossoverSignals(unittest.TestCase):
    def test_should_generate_order_when_ticks_are_enough_for_2_3_period_ma(self):
        strategy = BidsMACrossoverStrategy(2, 3)

        ticks = []
        ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.12404,"ask":1.1242}}')
        ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:50:08.543570Z","bid":1.12403,"ask":1.12421}}')
        ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:50:08.633262Z","bid":1.12406,"ask":1.12423}}')
        # ticks.append(
        # '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:50:08.754773Z","bid":1.12405,"ask":1.12425}}')

        for i in range(0, strategy.period2 - 1):
            self.assertIsNone(
                strategy.calculate_signals(parse_event_str(get_time(), ticks[i])))

        tick = parse_event_str(get_time(), ticks[strategy.period2 - 1])
        self.assertIsNotNone(strategy.calculate_signals(tick))

    def test_should_generate_order_when_ticks_are_enough_for_5_10_period_ma(self):
        strategy = BidsMACrossoverStrategy(5, 10)

        ticks = []
        ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.12404,"ask":1.1242}}')
        ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:50:08.543570Z","bid":1.12403,"ask":1.12421}}')
        ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:50:08.633262Z","bid":1.12406,"ask":1.12423}}')
        ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:50:08.754773Z","bid":1.12405,"ask":1.12425}}')
        ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:50:10.243141Z","bid":1.12411,"ask":1.12429}}')
        ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:50:10.221148Z","bid":1.12409,"ask":1.12427}}')
        ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:50:25.349546Z","bid":1.12415,"ask":1.12433}}')
        ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:50:48.074682Z","bid":1.12411,"ask":1.12431}}')
        ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:51:52.351710Z","bid":1.12409,"ask":1.12428}}')
        ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:51:52.526526Z","bid":1.12407,"ask":1.12424}}')
        # ticks.append(
        # '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:51:52.721429Z","bid":1.12404,"ask":1.12423}}')

        for i in range(0, strategy.period2 - 1):
            self.assertIsNone(
                strategy.calculate_signals(parse_event_str(get_time(), ticks[i])))

        tick = parse_event_str(get_time(), ticks[strategy.period2 - 1])
        self.assertIsNotNone(strategy.calculate_signals(tick))


class TestMACrossoverSignals23(unittest.TestCase):
    def setUp(self):
        self.strategy = BidsMACrossoverStrategy(2, 3)

    def test_should_not_generate_order_when_ma_and_previous_ma_are_same_for_the_first_period(self):
        order = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.024,"ask":1.01}}'))
        self.assertIsNone(order)
        order = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.026,"ask":1.07}}'))
        self.assertIsNone(order)
        order = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.024,"ask":1.09}}'))
        self.assertIsNone(order)

    def test_should_generate_sell_order_when_ticks_are_enough_for_period2_ma(self):
        order = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.024,"ask":1.01}}'))
        self.assertIsNone(order)
        order = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.026,"ask":1.07}}'))
        self.assertIsNone(order)
        order = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.023,"ask":1.09}}'))
        self.assertIsNotNone(order)
        self.assertEqual(ORDER_SIDE_SELL, order.side)

    def test_should_generate_buy_order_when_ticks_are_enough_for_period2_ma(self):
        order = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.024,"ask":1.01}}'))
        self.assertIsNone(order)
        order = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.023,"ask":1.07}}'))
        self.assertIsNone(order)
        order = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.026,"ask":1.09}}'))
        self.assertIsNotNone(order)
        self.assertEqual(ORDER_SIDE_BUY, order.side)

    def test_should_not_generate_order_when_no_cross_over(self):
        order = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.024,"ask":1.01}}'))
        self.assertIsNone(order)
        order = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.026,"ask":1.07}}'))
        self.assertIsNone(order)
        order = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.028,"ask":1.09}}'))
        self.assertIsNone(order)

    def test_should_generate_buy_order_then_sell_order(self):
        order = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.024,"ask":1.01}}'))
        self.assertIsNone(order)
        order = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.023,"ask":1.07}}'))
        self.assertIsNone(order)
        order = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.026,"ask":1.09}}'))
        self.assertIsNotNone(order)
        self.assertEqual(ORDER_SIDE_BUY, order.side)

        order = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.026,"ask":1.07}}'))
        self.assertIsNone(order)
        order = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.023,"ask":1.09}}'))
        self.assertIsNotNone(order)
        self.assertEqual(ORDER_SIDE_SELL, order.side)
