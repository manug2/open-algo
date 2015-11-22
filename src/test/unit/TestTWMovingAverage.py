__author__ = 'ManuGarg'

import sys

sys.path.append('../../main')
import unittest
from com.open.algo.calcs.twma import TWMA
from com.open.algo.utils import get_time


class TestTWMA(unittest.TestCase):

    def setUp(self):
        pass

    def test_should_give_twma_when_same_time_same_value(self):
        last_value = 1.0
        last_time = get_time()
        twma = TWMA(period=2, base_time=last_time, base_value=last_value)
        result = twma(last_time, last_value)
        self.assertAlmostEqual(last_value, result)

    def test_should_give_twma_when_same_time_diff_value(self):
        last_value = 1.0
        last_time = get_time()
        twma = TWMA(period=2, base_time=last_time, base_value=last_value)
        result = twma(last_time, 2.0)
        self.assertAlmostEqual(last_value, result)

    def test_should_give_twma_when_diff_time_same_value(self):
        last_value = 1.0
        last_time = get_time()
        new_time = get_time(1)
        twma = TWMA(period=2, base_time=last_time, base_value=last_value)
        result = twma(new_time, last_value)
        self.assertAlmostEqual(last_value, result)

    def test_should_give_twma_when_diff_time_diff_value(self):
        last_time = get_time()
        new_time = get_time(1)
        twma = TWMA(period=10, base_time=last_time, base_value=1.0)
        result = twma(new_time, 2.0)
        self.assertAlmostEqual(1.1, result)

    def test_should_give_new_value_when_age_more_than_lookback_period_new_value(self):
        last_time = get_time()
        new_time = get_time(5)
        twma = TWMA(period=2, base_time=last_time, base_value=1.0)
        result = twma(new_time, 2.0)
        self.assertAlmostEqual(2.0, result)

    def test_should_give_new_value_when_age_equals_lookback_period_new_value(self):
        last_time = get_time()
        new_time = get_time(10)
        twma = TWMA(period=10, base_time=last_time, base_value=1.0)
        result = twma(new_time, 2.0)
        self.assertAlmostEqual(2.0, result)


from com.open.algo.calcs.twma import TickTWMA
from com.open.algo.oanda.parser import parse_event_str


class TestTickTWMA(unittest.TestCase):

    def setUp(self):
        self.last_tick = parse_event_str(get_time(),
                '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.000000Z","bid":1.0,"ask":1.1242}}')

    def test_should_give_twma_when_same_time_same_value(self):
        twma = TickTWMA(period=2, base_tick=self.last_tick, attribute="bid")
        new_tick = parse_event_str(get_time(),
                '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.000000Z","bid":1.0,"ask":1.1242}}')
        result = twma(new_tick)
        self.assertAlmostEqual(self.last_tick.bid, result)

    def test_should_give_twma_when_same_time_diff_value(self):
        twma = TickTWMA(period=2, base_tick=self.last_tick, attribute="bid")
        new_tick = parse_event_str(get_time(),
                '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:02.000000Z","bid":1.2,"ask":1.1242}}')
        result = twma(new_tick)
        self.assertAlmostEqual(self.last_tick.bid, result)

    def test_should_give_twma_when_diff_time_same_value(self):
        twma = TickTWMA(period=2, base_tick=self.last_tick, attribute="bid")
        new_tick = parse_event_str(get_time(),
                '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:03.000000Z","bid":1.0,"ask":1.1242}}')
        result = twma(new_tick)
        self.assertAlmostEqual(self.last_tick.bid, result)

    def test_should_give_twma_when_diff_time_diff_value(self):
        twma = TickTWMA(period=10, base_tick=self.last_tick, attribute="bid")
        new_tick = parse_event_str(get_time(),
                '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:03.000000Z","bid":2.0,"ask":1.1242}}')
        result = twma(new_tick)
        self.assertAlmostEqual(1.1, result)

    def test_should_give_new_value_when_age_more_than_lookback_period_new_value(self):
        twma = TickTWMA(period=10, base_tick=self.last_tick, attribute="bid")
        new_tick = parse_event_str(get_time(),
                '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:15.000000Z","bid":2.0,"ask":1.1242}}')
        result = twma(new_tick)
        self.assertAlmostEqual(2.0, result)

    def test_should_give_new_value_when_age_equals_lookback_period_new_value(self):
        twma = TickTWMA(period=10, base_tick=self.last_tick, attribute="bid")
        new_tick = parse_event_str(get_time(),
                '{"tick":{"instrument":"EUR_USD","time":"2015-06-11T22:48:12.000000Z","bid":2.0,"ask":1.1242}}')
        result = twma(new_tick)
        self.assertAlmostEqual(2.0, result)

