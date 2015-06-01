__author__ = 'ManuGarg'

import sys

sys.path.append('../../main')
import unittest

import queue, threading, time

from com.open.algo.utils import read_settings
from com.open.algo.eventLoop import Journaler
from com.open.algo.oanda.environments import ENVIRONMENTS, CONFIG_PATH_FOR_UNIT_TESTS

from com.open.algo.oanda.streaming import *
from com.open.algo.oanda.parser import *
from com.open.algo.oanda.history import *

TARGET_ENV = "practice"


class TestStreaming(unittest.TestCase):

    def setUp(self):
        self.journaler = Journaler()
        domain = ENVIRONMENTS['streaming'][TARGET_ENV]
        settings = read_settings(CONFIG_PATH_FOR_UNIT_TESTS, TARGET_ENV)

        self.events = queue.Queue()
        self.heartbeat_q = queue.Queue()
        exceptions = queue.Queue()
        self.prices = StreamingForexPrices(
            domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID'],
            'EUR_USD', self.events, self.heartbeat_q, self.journaler, exceptions
        )

    def test_should_receive_streaming_ticks(self):
        price_thread = threading.Thread(target=self.prices.stream, args=[])
        price_thread.start()
        time.sleep(2.5)
        self.prices.stop()
        price_thread.join(timeout=2)
        try:
            while True:
                out_event = self.events.get_nowait()
        except queue.Empty:
            pass
        self.assertIsNotNone(out_event)
        self.assertTrue(isinstance(out_event, TickEvent))

    def test_should_receive_streaming_ticks(self):
        price_thread = threading.Thread(target=self.prices.stream, args=[])
        price_thread.start()
        time.sleep(2.5)
        self.prices.stop()
        price_thread.join(timeout=2)
        out_event = None
        try:
            while True:
                out_event = self.events.get_nowait()
        except queue.Empty:
            pass
        self.assertIsNotNone(out_event)
        self.assertTrue(isinstance(out_event, TickEvent))


class TestHistoric(unittest.TestCase):

    def setUp(self):
        self.journaler = Journaler()
        domain = ENVIRONMENTS['api'][TARGET_ENV]
        settings = read_settings(CONFIG_PATH_FOR_UNIT_TESTS, TARGET_ENV)

        self.prices = HistoricForexPrices(
            domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID']
        )

    def test_should_query_prices(self):
        rates = self.prices.query('EUR_USD')
        print(rates)
        self.assertIsNotNone(rates)


class TestParse(unittest.TestCase):

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
