__author__ = 'ManuGarg'

import sys

sys.path.append('../../main')
import unittest

import queue, threading, time

from com.open.algo.utils import read_settings
from com.open.algo.journal import Journaler
from com.open.algo.oanda.environments import ENVIRONMENTS, CONFIG_PATH_FOR_UNIT_TESTS

from com.open.algo.oanda.streaming import *
from com.open.algo.oanda.history import *

TARGET_ENV = "practice"


class TestStreaming(unittest.TestCase):

    def setUp(self):
        self.journaler = Journaler()
        domain = ENVIRONMENTS['streaming'][TARGET_ENV]
        settings = read_settings(CONFIG_PATH_FOR_UNIT_TESTS, TARGET_ENV)

        self.events = queue.Queue()
        self.heartbeat_q = queue.Queue()
        self.exceptions = queue.Queue()
        self.streamer = OandaEventStreamer(domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID'], self.journaler)
        self.streamer.set_events_q(self.events).set_heartbeat_q(self.heartbeat_q).set_exception_q(self.exceptions)
        self.streaming_thread = threading.Thread(target=self.streamer.stream, args=[])

    def test_should_receive_streaming_ticks(self):
        self.streamer.set_instruments('EUR_USD')
        self.streaming_thread.start()
        time.sleep(2.5)
        self.streamer.stop()
        self.streaming_thread.join(timeout=2)
        out_event = None
        try:
            while True:
                out_event = self.events.get_nowait()
        except queue.Empty:
            pass
        self.assertIsNotNone(out_event)
        self.assertTrue(isinstance(out_event, TickEvent))

    def test_should_not_allow_change_of_context_when_already_streaming(self):
        self.streamer.set_instruments('EUR_USD')
        self.streaming_thread.start()
        time.sleep(2)
        try:
            self.streamer.set_context(OANDA_CONTEXT_EVENTS)
            self.fail('should have failed when changing context after streaming was started')
        except RuntimeError:
            pass
        time.sleep(2)
        self.streamer.stop()
        self.streaming_thread.join(timeout=2)

    def test_should_be_able_to_connect_for_receiving_streaming_account_events(self):
        self.streamer.set_context(OANDA_CONTEXT_EVENTS)
        self.streaming_thread.start()
        out_event = None
        try:
            out_event = self.heartbeat_q.get(timeout=20)
        except queue.Empty:
            pass
        self.streamer.stop()
        self.streaming_thread.join(timeout=5)
        self.assertIsNotNone(out_event)
        self.assertTrue(isinstance(out_event, Heartbeat))


class TestHistoric(unittest.TestCase):

    def setUp(self):
        self.journaler = Journaler()
        domain = ENVIRONMENTS['api'][TARGET_ENV]
        settings = read_settings(CONFIG_PATH_FOR_UNIT_TESTS, TARGET_ENV)

        self.streamer = HistoricForexPrices(
            domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID']
        )

    def test_should_query_prices(self):
        rates = self.streamer.query('EUR_USD')
        print(rates)
        self.assertIsNotNone(rates)

