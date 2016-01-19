__author__ = 'ManuGarg'

import sys

sys.path.append('../../main')
import unittest
from com.open.algo.calcs.twma import TWMA
from com.open.algo.utils import *


class TestMovingAverages(unittest.TestCase):

    def setUp(self):
        self.now = get_time_with_zero_millis()
        self.now1 = add_time(self.now, 1)
        self.now2 = add_time(self.now, 2)
        self.now3 = add_time(self.now, 3)

    def test_should_give_ma_for_2_ticks_and_2s_period(self):
        twma = TWMA(2, 'time', 'bid')
        ticks = list()
        ticks.append({'bid': 1.0, 'time': self.now})
        ticks.append({'bid': 2.0, 'time': self.now1})
        value = twma(self.now2, ticks)
        self.assertEqual(1.5, value)

    def test_should_give_ma_for_3_ticks_and_2s_period(self):
        twma = TWMA(2, 'time', 'bid')
        ticks = list()
        ticks.append({'bid': 1, 'time': self.now})
        ticks.append({'bid': 2, 'time': self.now1})
        ticks.append({'bid': 3, 'time': self.now2})
        value = twma(self.now3, ticks)
        self.assertEqual(2.5, value)

    def test_should_give_ma_for_3_ticks_and_3s_period(self):
        twma = TWMA(3, 'time', 'bid')
        ticks = list()
        ticks.append({'bid': 1, 'time': self.now})
        ticks.append({'bid': 2, 'time': self.now1})
        ticks.append({'bid': 3, 'time': self.now2})
        value = twma(self.now3, ticks)
        self.assertEqual(2.0, value)

    def test_should_give_ma_for_list_smaller_than_period(self):
        twma = TWMA(3, 'time', 'bid')
        ticks = list()
        ticks.append({'bid': 1, 'time': self.now})
        ticks.append({'bid': 4, 'time': self.now1})
        value = twma(self.now2, ticks)
        self.assertEqual(2.0, value)

    def test_should_give_ma_for_list_bigger_than_period(self):
        twma = TWMA(2, 'time', 'bid')
        ticks = list()
        ticks.append({'bid': 1, 'time': self.now})
        ticks.append({'bid': 2, 'time': self.now1})
        ticks.append({'bid': 3, 'time': self.now2})
        ticks.append({'bid': 4, 'time': self.now3})
        value = twma(add_time(self.now3, 1), ticks)
        self.assertEqual(3.5, value)

    def test_should_give_ma_for_custom_value_field(self):
        twma = TWMA(2, 'time', 'ask')
        ticks = list()
        ticks.append({'ask': 1.0, 'time': self.now})
        ticks.append({'ask': 2.0, 'time': self.now1})
        value = twma(self.now2, ticks)
        self.assertEqual(1.5, value)

    def test_should_give_ma_for_custom_time_field(self):
        twma = TWMA(2, 'tt', 'bid')
        ticks = list()
        ticks.append({'bid': 1.0, 'tt': self.now})
        ticks.append({'bid': 2.0, 'tt': self.now1})
        value = twma(self.now2, ticks)
        self.assertEqual(1.5, value)

    def test_should_give_ma_for_custom_time_and_value_field(self):
        twma = TWMA(2, 'tt', 'ask')
        ticks = list()
        ticks.append({'ask': 1.0, 'tt': self.now})
        ticks.append({'ask': 2.0, 'tt': self.now1})
        value = twma(self.now2, ticks)
        self.assertEqual(1.5, value)

    def test_should_give_ma_after_ignoring_subsequent_ticks_with_duplicate_time(self):
        twma = TWMA(3, 'time', 'bid')
        ticks = list()
        ticks.append({'bid': 1, 'time': self.now})
        ticks.append({'bid': 3, 'time': self.now1})
        ticks.append({'bid': 4, 'time': self.now1})
        value = twma(self.now2, ticks)
        self.assertEqual(2.0, value)

    def test_should_give_ma_after_ignoring_subsequent_ticks_with_higher_time(self):
        twma = TWMA(2, 'time', 'bid')
        ticks = list()
        ticks.append({'bid': 1, 'time': self.now})
        ticks.append({'bid': 4, 'time': self.now2})
        ticks.append({'bid': 3, 'time': self.now1})
        value = twma(self.now2, ticks)
        self.assertEqual(2.0, value)


class TestDataSufficiency(unittest.TestCase):

    def setUp(self):
        self.now = get_time_with_zero_millis()
        self.now1 = add_time(self.now, 1)
        self.now2 = add_time(self.now, 2)
        self.now3 = add_time(self.now, 3)

    def test_should_fail_when_time_period_not_given(self):
        try:
            TWMA()
            self.fail('should have failed as time period not given')
        except:
            pass

    def test_should_fail_when_time_attr_not_given(self):
        try:
            TWMA(2)
            self.fail('should have failed as time attribute not given')
        except:
            pass

    def test_should_fail_when_value_attr_not_given(self):
        try:
            TWMA(2, 'tt')
            self.fail('should have failed as value attribute not given')
        except:
            pass

    def test_should_fail_when_now_not_given(self):
        ticks = list()
        ticks.append({'ask': 1, 'time': self.now})
        ticks.append({'ask': 3, 'time': self.now1})
        twma = TWMA(2, 'time', 'ask')
        try:
            twma(ticks)
            self.fail('should have failed as now is not given')
        except:
            pass

    def test_should_fail_when_ticks_not_given(self):
        twma = TWMA(2, 'time', 'ask')
        try:
            twma()
            self.fail('should have failed as ticks are not given')
        except:
            pass

    def test_should_fail_when_ticks_are_empty(self):
        twma = TWMA(2, 'time', 'ask')
        try:
            twma(list())
            self.fail('should have failed as ticks are an empty list')
        except:
            pass

    def test_should_fail_for_list_of_ticks_when_value_attribute_not_present(self):
        twma = TWMA(2, 'time', 'bid')
        ticks = list()
        ticks.append({'ask': 1, 'time': self.now})
        ticks.append({'ask': 3, 'time': self.now1})
        try:
            twma(self.now3, ticks)
            self.fail('should have failed as "bid" field is not present in the data')
        except:
            pass

    def test_should_fail_for_list_of_ticks_when_time_attribute_not_present(self):
        twma = TWMA(2, 'tt', 'ask')
        ticks = list()
        ticks.append({'ask': 1, 'time': self.now})
        ticks.append({'ask': 3, 'time': self.now1})
        try:
            twma(self.now3, ticks)
            self.fail('should have failed as "tt" field is not present in the data')
        except:
            pass

