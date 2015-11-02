__author__ = 'ManuGarg'

import sys
sys.path.append('../../../main')

import unittest
from testUtils import *

from queue import Queue
from threading import Thread
from com.open.algo.utils import read_settings
from com.open.algo.oanda.environments import ENVIRONMENTS, CONFIG_PATH_FOR_UNIT_TESTS

from com.open.algo.oanda.streaming import *
from com.open.algo.oanda.parser import *
from com.open.algo.model import Heartbeat
from com.open.algo.wiring.eventLoop import *
from com.open.algo.journal import *

TARGET_ENV = "practice"
OUTPUT_DIR = '../output/'


class TestStreaming(unittest.TestCase):

    def setUp(self):
        self.journaler = Journaler()
        domain = ENVIRONMENTS['streaming'][TARGET_ENV]
        settings = read_settings(CONFIG_PATH_FOR_UNIT_TESTS, TARGET_ENV)

        self.ticks_q = Queue()
        self.heartbeat_q = Queue()
        self.exception_q = Queue()
        self.prices = OandaEventStreamer(domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID'], self.journaler)
        self.prices.set_instruments('EUR_USD')
        self.prices.set_events_q(self.ticks_q).set_heartbeat_q(self.heartbeat_q).set_exception_q(self.exception_q)
        self.price_thread = Thread(target=self.prices.start, args=[])

    def tearDown(self):
        self.prices.stop()
        self.price_thread.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)

    def test_journaler_should_log_streaming_events(self):
        self.price_thread.start()
        await_event_receipt(self, self.ticks_q, 'did not get any tick')
        out_event = self.journaler.get_last_event()
        self.assertIsNotNone(out_event)

    def test_should_receive_streaming_heartbeat_events(self):
        self.price_thread.start()
        out_event = await_event_receipt(self, self.heartbeat_q, 'did not get any heartbeat', timeout=10)
        self.assertIsNotNone(out_event)
        self.assertTrue(isinstance(out_event, Heartbeat))

    def test_should_log_oanda_streaming_ticks_to_file_journaler_q(self):
        filename = os.path.join(OUTPUT_DIR, 'journal_oanda_tick_ut.txt')
        try:
            os.remove(filename)
        except OSError:
            pass
        journaler = FileJournaler(full_path=filename)

        # plug the new file journaler
        self.prices.journaler = journaler
        self.price_thread.start()
        try:
            tick = await_event_receipt(self, self.ticks_q, 'did not get any tick')
        finally:
            self.prices.stop()

        try:
            while True:
                tick = self.ticks_q.get_nowait()
        except Empty:
            pass

        heartbeat = None
        try:
            while True:
                heartbeat = self.heartbeat_q.get_nowait()
        except Empty:
            pass

        journal_last_received = journaler.get_last_received()
        journal_last_event = journaler.get_last_event()
        self.assertIsNotNone(journal_last_event)

        out_event = parse_event(journal_last_received, json.loads(journal_last_event))
        if isinstance(out_event, Heartbeat):
            self.assertEqual(heartbeat, out_event)
        elif isinstance(out_event, TickEvent):
            self.assertEqual(tick, out_event)
        else:
            self.fail('unknown event received from Oanda? - %s' % out_event)
