__author__ = 'ManuGarg'

import sys

sys.path.append('../../main')
import unittest
from com.open.algo.oanda.parser import parse_event_str
from com.open.algo.strategy import AbstractStrategy
from com.open.algo.strategies.twco import TWMACrossoverStrategy
from com.open.algo.utils import get_time
from com.open.algo.trading.fxEvents import ORDER_SIDE_SELL, ORDER_SIDE_BUY


class TestTWMACrossoverStrategyClass(unittest.TestCase):
    def setUp(self):
        self.strategy = TWMACrossoverStrategy(120, 180, 'time', 'bid')

        self.ticks = []
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.000000","bid":1.12404,"ask":1.1242}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:50:08.000000","bid":1.12403,"ask":1.12421}}')

    def test_should_be_instance_of_AbstractStrategy(self):
        self.assertIsInstance(TWMACrossoverStrategy(5, 10), AbstractStrategy)

    def test_should_not_allow_period2_equal_to_period1(self):
        try:
            TWMACrossoverStrategy(5, 5)
            self.fail('should have failed when period1 = period2')
        except AssertionError:
            pass

    def test_should_not_allow_period2_less_than_period1(self):
        try:
            TWMACrossoverStrategy(15, 5)
            self.fail('should have failed when period1 > period2')
        except AssertionError:
            pass

    def test_should_not_generate_signal_after_one_tick_event(self):
        tick = parse_event_str(get_time(), self.ticks[0])
        self.assertIsNone(self.strategy.calculate_signals(tick))


class TestTWMACrossoverSignals(unittest.TestCase):

    def test_should_generate_signal_when_ticks_are_enough_for_2_3_period_ma(self):
        strategy = TWMACrossoverStrategy(2, 3, 'time', 'bid')

        ticks = list()
        ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:03.000000Z","bid":1.1000,"ask":1.1242}}')
        ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:04.00000Z","bid":1.2000,"ask":1.12421}}')
        ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:05.000000Z","bid":1.3000,"ask":1.12423}}')
        # ticks.append(
        # '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:50:08.754773Z","bid":1.12405,"ask":1.12425}}')

        for i in range(0, len(ticks) - 1):
            self.assertIsNone(
                strategy.calculate_signals(parse_event_str(get_time(), ticks[i])))

        tick = parse_event_str(get_time(), ticks[len(ticks)-1])
        self.assertIsNotNone(strategy.calculate_signals(tick))

    def test_should_generate_signal_when_ticks_are_enough_for_5_10_period_ma(self):
        strategy = TWMACrossoverStrategy(5, 10)

        ticks = list()
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

        for i in range(0, 10 - 1):
            self.assertIsNone(
                strategy.calculate_signals(parse_event_str(get_time(), ticks[i])))

        #sending another tick will trigger MA crossover detection
        tick = parse_event_str(get_time(), ticks[10 - 1])
        self.assertIsNotNone(strategy.calculate_signals(tick))


class TestTWMACrossoverSignals23(unittest.TestCase):
    def setUp(self):
        self.strategy = TWMACrossoverStrategy(2, 3)

    def test_should_not_generate_signal_when_ma_and_previous_ma_are_same_for_the_first_period(self):
        signal = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.024,"ask":1.01}}'))
        self.assertIsNone(signal)
        signal = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.026,"ask":1.07}}'))
        self.assertIsNone(signal)
        signal = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.024,"ask":1.09}}'))
        self.assertIsNone(signal)

    def test_should_generate_sell_signal_when_ticks_are_enough_for_period2_ma(self):
        signal = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.026,"ask":1.01}}'))
        self.assertIsNone(signal)
        signal = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:03.024026Z","bid":1.024,"ask":1.07}}'))
        self.assertIsNone(signal)
        signal = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:04.024026Z","bid":1.023,"ask":1.09}}'))
        self.assertIsNotNone(signal)
        self.assertEqual(ORDER_SIDE_SELL, signal)

    def test_should_generate_buy_signal_when_ticks_are_enough_for_period2_ma(self):
        signal = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.023,"ask":1.01}}'))
        self.assertIsNone(signal)
        signal = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:03.024026Z","bid":1.024,"ask":1.07}}'))
        self.assertIsNone(signal)
        signal = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:04.024026Z","bid":1.026,"ask":1.09}}'))
        self.assertIsNotNone(signal)
        self.assertEqual(ORDER_SIDE_BUY, signal)

    def test_should_not_generate_signal_when_no_cross_over(self):
        signal = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.02400,"ask":1.01}}'))
        self.assertIsNone(signal)
        signal = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:03.024026Z","bid":1.02401,"ask":1.07}}'))
        self.assertIsNone(signal)
        signal = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:04.024026Z","bid":1.02402,"ask":1.09}}'))
        self.assertIsNone(signal)

    def test_should_generate_buy_signal_then_sell_signal(self):
        signal = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.024026Z","bid":1.021,"ask":1.01}}'))
        self.assertIsNone(signal)
        signal = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:03.024026Z","bid":1.026,"ask":1.07}}'))
        self.assertIsNone(signal)
        signal = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:04.024026Z","bid":1.026,"ask":1.09}}'))
        self.assertIsNotNone(signal)
        self.assertEqual(ORDER_SIDE_BUY, signal)

        signal = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:05.024026Z","bid":1.024,"ask":1.07}}'))
        #self.assertIsNone(signal)
        signal = self.strategy.calculate_signals(parse_event_str(get_time(),
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:06.024026Z","bid":1.023,"ask":1.09}}'))
        self.assertIsNotNone(signal)
        self.assertEqual(ORDER_SIDE_SELL, signal)
