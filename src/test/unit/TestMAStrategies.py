__author__ = 'ManuGarg'

import sys

sys.path.append('../../main')
import unittest
from com.open.algo.oanda.parser import parse_event_str
from com.open.algo.strategy import *
from com.open.algo.utils import get_time


class TestMACrossover(unittest.TestCase):

    def setUp(self):
        self.strategy = MACrossoverStrategy(2, 3)

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
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:50:10.221148Z","bid":1.12409,"ask":1.12427}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:50:25.349546Z","bid":1.12415,"ask":1.12433}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:50:48.074682Z","bid":1.12411,"ask":1.12431}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:51:52.351710Z","bid":1.12409,"ask":1.12428}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:51:52.526526Z","bid":1.12407,"ask":1.12424}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:51:52.721429Z","bid":1.12404,"ask":1.12423}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:52:06.122081Z","bid":1.12401,"ask":1.12421}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:52:06.503775Z","bid":1.124,"ask":1.12417}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:52:14.434802Z","bid":1.12403,"ask":1.12421}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:58:10.652795Z","bid":1.12404,"ask":1.12421}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:58:36.304307Z","bid":1.12403,"ask":1.12419}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:58:36.574454Z","bid":1.124,"ask":1.12417}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:58:41.905831Z","bid":1.12397,"ask":1.12415}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:58:49.035049Z","bid":1.12395,"ask":1.12412}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:58:49.073787Z","bid":1.12391,"ask":1.12412}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:58:52.120459Z","bid":1.1239,"ask":1.12409}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:58:52.701578Z","bid":1.12388,"ask":1.12406}}')
        self.ticks.append(
            '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T23:10:28.083390Z","bid":1.12445,"ask":1.12463}}')

    def test_should_default_period1(self):
        self.assertTrue(MACrossoverStrategy().period1 > 0)

    def test_should_default_period2(self):
        self.assertTrue(MACrossoverStrategy().period2 > 0)

    def test_should_default_period2_greater_than_period1(self):
        strategy = MACrossoverStrategy()
        self.assertTrue(strategy.period2 > strategy.period1)

    def test_should_default_function_for_calculating_moving_average(self):
        self.assertEqual(MACrossoverStrategy().ma_function, sma)

    def test_should_be_instance_of_AbstractStrategy(self):
        self.assertIsInstance(MACrossoverStrategy(), AbstractStrategy)

    def test_should_not_allow_period2_equal_to_period1(self):
        try:
            MACrossoverStrategy(5, 5)
            self.fail('should have failed when period1 = period2')
        except ValueError:
            pass

    def test_should_not_allow_period2_less_than_period1(self):
        try:
            MACrossoverStrategy(15, 5)
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
        for i in range(0, self.strategy.period2-1):
            tick = parse_event_str(get_time(), self.ticks[i])
            order = self.strategy.calculate_signals(tick)
            self.assertIsNone(order)

    def test_should_generate_order_when_ticks_are_enough_for_period2_ma(self):
        for i in range(0, self.strategy.period2-1):
            self.assertIsNone(
                self.strategy.calculate_signals(parse_event_str(get_time(), self.ticks[i])))

        tick = parse_event_str(get_time(), self.ticks[self.strategy.period2-1])
        order = self.strategy.calculate_signals(tick)
        self.assertIsNotNone(order)

"""
    def test_should_fail_sma_for_list_of_ticks_without_mention_of_attribute(self):
        ticks = []
        ticks.append({'bid': 1})
        try:
            sma(ticks)
        except:
            pass


    def test_should_give_sma_for_list_of_ticks_bids(self):
        ticks = []
        ticks.append({'bid': 1})
        ticks.append({'bid': 3})
        value = sma(ticks, attribute='bid')
        self.assertEqual(2.0, value)


    def test_should_fail_sma_for_list_of_ticks_asks_when_not_present(self):
        ticks = []
        ticks.append({'ask': 1})
        ticks.append({'ask': 3})
        ticks.append({'ask': 5})
        try:
            sma(ticks, attribute='bid')
        except:
            pass


    def test_should_give_sma_for_list_of_ticks_asks(self):
        ticks = []
        ticks.append({'ask': 1})
        ticks.append({'ask': 3})
        ticks.append({'ask': 5})
        value = sma(ticks, attribute='ask')
        self.assertEqual(3.0, value)


    def test_should_give_sma_for_list_of_ticks_bids_when_asks_also_present(self):
        ticks = []
        ticks.append({'bid': 1, 'ask': 1})
        ticks.append({'bid': 1, 'ask': 3})
        ticks.append({'bid': 1, 'ask': 5})
        value = sma(ticks, attribute='ask')
        self.assertEqual(3.0, value)


    def test_should_give_sma_for_list_of_ticks_bids_and_asks(self):
        ticks = []
        ticks.append({'bid': 1, 'ask': 1})
        ticks.append({'bid': 1, 'ask': 3})
        ticks.append({'bid': 1, 'ask': 5})
        value = sma(ticks, attributes=['bid', 'ask'])
        self.assertEqual(1.0, value['bid'])
        self.assertEqual(3.0, value['ask'])


    def test_should_give_sma_for_list_of_tick_objects_bids_and_asks(self):
        ticks = []
        ticks.append(TickEvent('CHF_USD', None, 1.01, 1.02))
        ticks.append(TickEvent('CHF_USD', None, 1.03, 1.04))
        value = sma(ticks, attributes=['bid', 'ask'])
        self.assertEqual(1.02, value['bid'])
        self.assertEqual(1.03, value['ask'])


    def test_should_give_sma_for_list_smaller_than_period(self):
        ticks = []
        ticks.append({'bid': 1})
        ticks.append({'bid': 3})
        value = sma(ticks, period=14, attribute='bid')
        self.assertEqual(2.0, value)

"""