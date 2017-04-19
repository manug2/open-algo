__author__ = 'ManuGarg'

import sys

sys.path.append('../../main')
import unittest

from com.open.algo.oanda.streaming import *
from com.open.algo.oanda.parser import *
from com.open.algo.oanda.history import *


class TestParseRates(unittest.TestCase):

    def setUp(self):
        self.tick_str = \
            '{"tick": {"instrument": "EUR_USD", "time": "2015-05-08T20:59:45.031348Z", "bid": 1.11975, "ask": 1.12089}}'
        self.tick_json = json.loads(self.tick_str)

        self.hb_str = '{"heartbeat":{"time":"2015-05-13T02:44:29.815629Z"}}'
        self.hb_json = json.loads(self.hb_str)

    def test_should_parse_tick_from_oanda(self):
        parsed = parse_tick(get_time(), self.tick_json)
        self.assertIsNotNone(parsed)
        self.assertTrue(isinstance(parsed, TickEvent))

    def test_should_parse_heartbeat_from_oanda(self):
        parsed = parse_heartbeat(get_time(), self.hb_json)
        self.assertIsNotNone(parsed)
        self.assertTrue(isinstance(parsed, Heartbeat))

    def test_should_detect_and_parse_tick_from_oanda(self):
        parsed = parse_event(get_time(), self.tick_json)
        self.assertIsNotNone(parsed)
        self.assertTrue(isinstance(parsed, TickEvent))

    def test_should_detect_and_parse_heartbeat_from_oanda(self):
        parsed = parse_event(get_time(), self.hb_json)
        self.assertIsNotNone(parsed)
        self.assertTrue(isinstance(parsed, Heartbeat))

    def test_should_raise_error_when_event_is_none(self):
        try:
            parse_event(None)
        except TypeError:
            pass

    def test_should_raise_error_when_event_is_string(self):
        try:
            parse_event(None, 'this is an invalid event')
        except ValueError:
            pass

    def test_should_raise_error_when_event_does_not_have_tick_or_heartbeat(self):
        event = {'name': 'tick', 'value': 'hb'}
        try:
            parse_event(None, event)
        except ValueError:
            pass

    def test_should_parse_tick_event_string_from_oanda(self):
        parsed = parse_event_str(get_time(), self.tick_str)
        self.assertIsNotNone(parsed)
        self.assertTrue(isinstance(parsed, TickEvent))

    def test_should_parse_heartbeat_event_string_from_oanda(self):
        parsed = parse_event_str(get_time(), self.hb_str)
        self.assertIsNotNone(parsed)
        self.assertTrue(isinstance(parsed, Heartbeat))


class TestParseExecutionResponse(unittest.TestCase):

    def setUp(self):
        self.executed_order_str = \
            '{"instrument": "EUR_USD", "time": "2015-05-08T20:59:45.031348Z", "bid": 1.11975, "ask": 1.12089}'
        self.executed_order_json = json.loads(self.executed_order_str)

    def should_give_executed_order_object(self):
        self.fail('not yet implemented')


class TestParseExecutionEvents(unittest.TestCase):

    def setUp(self):
        self.executed_order_str = \
            '{"instrument": "EUR_USD", "time": "2015-05-08T20:59:45.031348Z", "bid": 1.11975, "ask": 1.12089}'
        self.executed_order_json = json.loads(self.executed_order_str)

    def should_give_executed_order_object(self):
        self.fail('not yet implemented')