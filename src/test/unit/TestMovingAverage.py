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
