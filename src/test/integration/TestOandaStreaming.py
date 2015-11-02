__author__ = 'ManuGarg'

import sys

sys.path.append('../../main')
import unittest
from testUtils import *

from queue import Queue
from threading import Thread
from com.open.algo.utils import read_settings
from com.open.algo.journal import Journaler
from com.open.algo.oanda.environments import ENVIRONMENTS, CONFIG_PATH_FOR_UNIT_TESTS

from com.open.algo.oanda.streaming import *
from com.open.algo.oanda.history import *
from com.open.algo.wiring.commandListener import QueueCommandListener

TARGET_ENV = "practice"
MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM=5


class TestStreaming(unittest.TestCase):

    def setUp(self):
        self.journaler = Journaler()
        domain = ENVIRONMENTS['streaming'][TARGET_ENV]
        settings = read_settings(CONFIG_PATH_FOR_UNIT_TESTS, TARGET_ENV)

        self.events = Queue()
        self.heartbeat_q = Queue()
        self.exceptions = Queue()
        self.streamer = OandaEventStreamer(domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID'], self.journaler)
        self.streamer.set_events_q(self.events).set_heartbeat_q(self.heartbeat_q).set_exception_q(self.exceptions)
        self.streamer.set_instruments('EUR_USD')
        self.streaming_thread = Thread(target=self.streamer.stream, args=[])
        self.streaming_thread.start()

    def tearDown(self):
        self.streamer.stop()
        self.streaming_thread.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)

    def test_should_receive_streaming_ticks(self):
        out_event = await_event_receipt(self, self.events, 'did not get any tick')
        self.assertIsNotNone(out_event)
        self.assertTrue(isinstance(out_event, TickEvent))

    def test_should_not_allow_change_of_context_when_already_streaming(self):
        self.streamer.streaming = True
        try:
            self.streamer.set_context(OANDA_CONTEXT_EVENTS)
            self.fail('should have failed when changing context after streaming was started')
        except RuntimeError:
            pass


class TestStreamingExecutionEvents(unittest.TestCase):

    def setUp(self):
        self.journaler = Journaler()
        domain = ENVIRONMENTS['streaming'][TARGET_ENV]
        settings = read_settings(CONFIG_PATH_FOR_UNIT_TESTS, TARGET_ENV)

        self.events = Queue()
        self.heartbeat_q = Queue()
        self.exceptions = Queue()
        self.streamer = OandaEventStreamer(domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID'], self.journaler)
        self.streamer.set_events_q(self.events).set_heartbeat_q(self.heartbeat_q).set_exception_q(self.exceptions)
        self.streamer.set_context(OANDA_CONTEXT_EVENTS)
        self.streaming_thread = Thread(target=self.streamer.stream, args=[])
        self.streaming_thread.start()

    def tearDown(self):
        self.streamer.stop()
        self.streaming_thread.join(timeout=5)

    def test_should_be_able_to_connect_for_receiving_streaming_account_events(self):
        out_event = await_event_receipt(self, self.heartbeat_q, 'did not get any heartbeat', 20)
        self.assertIsNotNone(out_event)
        self.assertTrue(isinstance(out_event, Heartbeat))


class TestCommandEvents(unittest.TestCase):

    def setUp(self):
        domain = ENVIRONMENTS['streaming'][TARGET_ENV]
        settings = read_settings(CONFIG_PATH_FOR_UNIT_TESTS, TARGET_ENV)

        self.streamer = OandaEventStreamer(domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID'], Journaler())
        self.streamer.set_events_q(Queue()).set_heartbeat_q(Queue()).set_exception_q(Queue())
        self.streamer.set_context(OANDA_CONTEXT_EVENTS)
        self.streaming_thread = Thread(target=self.streamer.stream, args=[])

        self.command_q = Queue()
        self.listener = QueueCommandListener(self.command_q, self.streamer.on_command)
        self.command_thread = self.listener.start_thread()

        self.streaming_thread.start()

    def tearDown(self):
        if self.streamer.streaming:
            self.streamer.stop()
            self.command_thread.join(timeout=5)
            self.streaming_thread.join(timeout=5)

    def test_should_be_able_to_connect_for_receiving_streaming_account_events(self):
        self.command_q.put_nowait(COMMAND_STOP)
        self.streaming_thread.join(timeout=5)
        self.command_thread.join(timeout=5)
        self.assertFalse(self.streamer.streaming, 'streaming should have stopped, but did not')

