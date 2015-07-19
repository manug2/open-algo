__author__ = 'ManuGarg'

import sys

sys.path.append('../../main')
import unittest
from com.open.algo.calcs.ma import sma
from com.open.algo.trading.fxEvents import TickEvent


class TestMA(unittest.TestCase):

    def setUp(self):
        pass

    def test_should_give_sma_for_list_of_numbers(self):
        numbers = [1, 2, 3, 4, 5]
        value = sma(numbers)
        self.assertEqual(3.0, value)

    def test_should_give_sma_for_list_of_neg_numbers(self):
        numbers = [-1, -2, -3, -4, -5]
        value = sma(numbers)
        self.assertEqual(-3.0, value)

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

    def test_should_give_sma_for_list_bigger_than_period3(self):
        numbers = [1, 2, 3, 4]
        value = sma(numbers, period=3)
        self.assertEqual(3.0, value)

    def test_should_give_sma_for_list_bigger_than_period4(self):
        numbers = [1, 2, 3, 4, 5, 6]
        value = sma(numbers, period=4)
        self.assertEqual(4.5, value)

    def test_should_give_sma_for_diff_period(self):
        numbers = [1.02, 1.03, 1.04]
        ma1 = sma(numbers, 2)
        self.assertEqual(0, round(1.035 - ma1, 3))
        ma2 = sma(numbers, 3)
        self.assertEqual(0, round(1.030 - ma2, 3))

    def test_should_give_sma_for_diff_period_with_4_items(self):
        numbers = [1.02, 1.03, 1.04, 1.03]
        ma1 = sma(numbers, 2)
        self.assertEqual(0, round(1.035 - ma1, 3))
        ma2 = sma(numbers, 3)
        self.assertEqual(0, round(1.033 - ma2, 3))

    def test_should_detect_sma_crossover_for_3_period(self):
        numbers = [1.024, 1.026, 1.024]
        ma1 = sma(numbers, 2)
        self.assertEqual(0, round(1.0250 - ma1, 4))
        ma2 = sma(numbers, 3)
        self.assertEqual(0, round(1.0247 - ma2, 4))
        diff = abs(round(ma1-ma2, 4))
        self.assertTrue(diff < 0.001)

    def test_should_detect_sma_crossover_for_4_period(self):
        numbers = [1.024, 1.026, 1.024, 1.025]
        ma1 = sma(numbers, 2)
        self.assertEqual(0, round(1.0245 - ma1, 4))
        ma2 = sma(numbers, 3)
        self.assertEqual(0, round(1.0250 - ma2, 4))
        diff = abs(round(ma1-ma2, 4))
        self.assertTrue(diff < 0.001)
