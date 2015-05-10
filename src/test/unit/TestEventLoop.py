__author__ = 'ManuGarg'

import sys

sys.path.append('../../main')
import unittest

import threading, time
from queue import Queue
from com.open.algo.utils import EventHandler
from com.open.algo.eventLoop import EventLoop, Journaler

TARGET_ENV = "practice"


class TestEventLoop(unittest.TestCase):

    def setUp(self):
        self.journaler = Journaler()
        self.events = Queue()
        self.handler = EventHandler()
        self.looper = EventLoop(self.events, self.handler, 0.3, self.journaler)

    def test_journaler_should_not_get_event_when_none_is_present(self):
        price_thread = threading.Thread(target=self.looper.start, args=[])
        price_thread.start()
        time.sleep(0.2)
        self.looper.stop()
        price_thread.join(timeout=0.2)
        out_event = self.journaler.getLastEvent()
        self.assertIsNone(out_event)

    def test_journaler_should_get_event_when_input_event(self):
        price_thread = threading.Thread(target=self.looper.start, args=[])
        price_thread.start()
        self.events.put('dummy event')
        time.sleep(0.2)
        self.looper.stop()
        price_thread.join(timeout=0.2)
        out_event = self.journaler.getLastEvent()
        self.assertIsNotNone(out_event)

    def test_journaler_should_get_event_same_as_input_event(self):
        price_thread = threading.Thread(target=self.looper.start, args=[])
        price_thread.start()
        self.events.put('dummy event')
        time.sleep(0.2)
        self.looper.stop()
        price_thread.join(timeout=0.2)
        out_event = self.journaler.getLastEvent()
        self.assertEqual('dummy event', out_event)

    def test_exception_queue_should_get_event_when_process_method_not_implemented(self):
        exceptions_q = Queue()
        looper = EventLoop(self.events, self.handler, 0.3, self.journaler, exceptions_q)
        price_thread = threading.Thread(target=looper.start, args=[])
        price_thread.start()
        self.events.put('dummy event')
        time.sleep(0.2)
        looper.stop()
        price_thread.join(timeout=0.2)
        out_event = exceptions_q.get_nowait()
        self.assertEqual('dummy event', out_event.orig_event)

    def test_exception_message_has_correct_caller(self):
        exceptions_q = Queue()
        looper = EventLoop(self.events, self.handler, 0.3, self.journaler, exceptions_q)
        price_thread = threading.Thread(target=looper.start, args=[])
        price_thread.start()
        self.events.put('dummy event')
        time.sleep(0.2)
        looper.stop()
        price_thread.join(timeout=0.2)
        out_event = exceptions_q.get_nowait()
        self.assertEqual('EventLoop[EventHandler]', out_event.caller)
