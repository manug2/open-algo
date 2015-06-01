__author__ = 'ManuGarg'

import sys
sys.path.append('../../../main')

import unittest
from queue import Queue

from threading import Thread

from com.open.algo.utils import read_settings
from com.open.algo.oanda.environments import ENVIRONMENTS, CONFIG_PATH_FOR_UNIT_TESTS

from com.open.algo.oanda.streaming import *
from com.open.algo.oanda.parser import *
from com.open.algo.model import Heartbeat
from com.open.algo.eventLoop import *

TARGET_ENV = "practice"
OUTPUT_DIR = '../output/'
TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM=2.5


class TestStreaming(unittest.TestCase):

    def setUp(self):
        self.journaler = Journaler()
        domain = ENVIRONMENTS['streaming'][TARGET_ENV]
        settings = read_settings(CONFIG_PATH_FOR_UNIT_TESTS, TARGET_ENV)

        self.events = Queue()
        self.heartbeat_q = Queue()
        exceptions = Queue()
        self.prices = StreamingForexPrices(
            domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID'],
            'EUR_USD', self.events, self.heartbeat_q, self.journaler, exceptions
        )

    def test_journaler_should_log_streaming_events(self):
        price_thread = Thread(target=self.prices.stream, args=[])
        price_thread.start()
        sleep(TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        self.prices.stop()
        price_thread.join(timeout=2)
        out_event = self.journaler.get_last_event()
        self.assertIsNotNone(out_event)

    def test_should_receive_streaming_heartbeat_events(self):
        price_thread = Thread(target=self.prices.stream, args=[])
        price_thread.start()
        sleep(TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        self.prices.stop()
        price_thread.join(timeout=2)
        out_event = None
        try:
            while True:
                out_event = self.heartbeat_q.get_nowait()
        except Empty:
            pass
        self.assertIsNotNone(out_event)
        self.assertTrue(isinstance(out_event, Heartbeat))

    def test_should_log_oanda_streaming_ticks_to_journal_file(self):
        filename = os.path.join(OUTPUT_DIR, 'journal_oanda_tick_ut.txt')
        try:
            os.remove(filename)
        except OSError:
            pass
        journal_q = Queue()
        journaler = FileJournaler(journal_q, full_path=filename)

        domain = ENVIRONMENTS['streaming'][TARGET_ENV]
        settings = read_settings(CONFIG_PATH_FOR_UNIT_TESTS, TARGET_ENV)

        ticks_q = Queue()
        hb_q = Queue()
        prices = StreamingForexPrices(
            domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID'],
            'EUR_USD', ticks_q, hb_q, journaler, None)

        looper = EventLoop(journal_q, journaler)
        loop_thread = Thread(target=looper.start, args=[])
        loop_thread.start()
        price_thread = Thread(target=prices.stream, args=[])
        price_thread.start()
        sleep(TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        prices.stop()
        price_thread.join(timeout=2)

        looper.stop()
        loop_thread.join(2*looper.heartbeat)
        journaler.close()

        out_str = journaler.get_last_event()
        self.assertIsNotNone(out_str)
        out_json = json.loads(out_str)
        out_event = parse_event(journaler.get_last_received(), out_json)
        tick = None
        try:
            while True:
                tick = ticks_q.get_nowait()
        except Empty:
            pass
        self.assertIsNotNone(tick)
        heartbeat = None
        try:
            while True:
                heartbeat = hb_q.get_nowait()
        except Empty:
            pass
        self.assertIsNotNone(heartbeat)

        if isinstance(out_event, Heartbeat):
            self.assertEqual(heartbeat, out_event)
        elif isinstance(out_event, TickEvent):
            self.assertEqual(tick, out_event)
        else:
            self.fail('unknown event received from Oanda? - %s' % out_event)
