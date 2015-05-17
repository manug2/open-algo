__author__ = 'ManuGarg'

import sys

sys.path.append('../../main')
import unittest

from threading import Thread
import time
from com.open.algo.eventLoop import *
import os
OUTPUT_DIR = '../output/'


class TestEventLoop(unittest.TestCase):

    def setUp(self):
        self.events = Queue()
        self.handler = EventHandler()
        self.looper = EventLoop(self.events, self.handler, 0.3)

    def test_input_event_should_have_been_consumed_same_as_input_event(self):
        price_thread = Thread(target=self.looper.start, args=[])
        price_thread.start()
        self.events.put('dummy event')
        time.sleep(0.2)
        self.looper.stop()
        price_thread.join(timeout=0.2)
        try:
            ev = self.events.get_nowait()
            self.fail('should have been empty, got event %s' % ev)
        except Empty:
            pass

    def test_all_input_events_should_have_been_consumed_same_as_input_event(self):
        price_thread = Thread(target=self.looper.start, args=[])
        price_thread.start()
        self.events.put('dummy event #1')
        self.events.put('dummy event #2')
        self.events.put('dummy event #3')
        time.sleep(0.2)
        self.looper.stop()
        price_thread.join(timeout=0.2)
        try:
            ev = self.events.get_nowait()
            self.fail('should have been empty, got event %s' % ev)
        except Empty:
            pass

    def test_exception_queue_should_get_event_when_process_method_not_implemented(self):
        exceptions_q = Queue()
        looper = EventLoop(self.events, self.handler, 0.1, exceptions_q)
        price_thread = Thread(target=looper.start, args=[])
        price_thread.start()
        self.events.put(None)
        time.sleep(0.2)
        looper.stop()
        price_thread.join(timeout=0.2)
        out_event = exceptions_q.get_nowait()
        self.assertIsNone(out_event.orig_event)

    def test_exception_message_has_correct_caller(self):
        exceptions_q = Queue()
        looper = EventLoop(self.events, self.handler, 0.1, exceptions_q)
        price_thread = Thread(target=looper.start, args=[])
        price_thread.start()
        self.events.put(None)
        time.sleep(2*looper.heartbeat)
        looper.stop()
        price_thread.join(timeout=2*looper.heartbeat)
        out_event = exceptions_q.get_nowait()
        self.assertEqual('EventLoop[EventHandler]', out_event.caller)

    def test_forwarded_event_should_be_same_as_input_event(self):
        events = Queue()
        forward_q = Queue()
        looper = EventLoop(events, EventHandler(), forward_q=forward_q)
        price_thread = Thread(target=looper.start, args=[])
        price_thread.start()
        events.put('dummy event')
        time.sleep(2*looper.heartbeat)
        looper.stop()
        price_thread.join(timeout=2*looper.heartbeat)
        out_event = forward_q.get_nowait()
        self.assertEqual('dummy event', out_event)

    def test_processed_event_should_be_same_as_input_event_when_dummy_handler(self):
        events = Queue()
        processed_event_q = Queue()
        looper = EventLoop(events, EventHandler(), processed_event_q=processed_event_q)
        price_thread = Thread(target=looper.start, args=[])
        price_thread.start()
        ev = 'dummy event'
        events.put(ev)
        time.sleep(2*looper.heartbeat)
        looper.stop()
        price_thread.join(timeout=2*looper.heartbeat)
        out_event = processed_event_q.get_nowait()
        self.assertEqual(ev, out_event)

    def test_forwarded_and_processed_event_should_be_same_as_input_event_when_dummy_handler(self):
        events = Queue()
        forward_q = Queue()
        processed_event_q = Queue()
        looper = EventLoop(events, EventHandler(), forward_q=forward_q, processed_event_q=processed_event_q)
        price_thread = Thread(target=looper.start, args=[])
        price_thread.start()
        ev = 'dummy event'
        events.put(ev)
        time.sleep(2*looper.heartbeat)
        looper.stop()
        price_thread.join(timeout=2*looper.heartbeat)
        self.assertEqual(ev, forward_q.get_nowait())
        self.assertEqual(ev, processed_event_q.get_nowait())

    def test_exception_and_forwarded_and_processed_queues_behave_correctly_when_dummy_handler_and_bad_event(self):
        events = Queue()
        exceptions_q = Queue()
        forward_q = Queue()
        processed_event_q = Queue()
        looper = EventLoop(events, EventHandler(), exceptions_q=exceptions_q,
                           forward_q=forward_q, processed_event_q=processed_event_q)
        price_thread = Thread(target=looper.start, args=[])
        price_thread.start()
        ev = None
        events.put(ev)
        time.sleep(2*looper.heartbeat)
        looper.stop()
        price_thread.join(timeout=2*looper.heartbeat)

        out_event = exceptions_q.get_nowait()
        self.assertIsNone(out_event.orig_event)

        self.assertIsNone(ev, forward_q.get_nowait())

        try:
            processed_event_q.get_nowait()
            self.fail('got processed event when exception happened')
        except Empty:
            pass


class TestFileJounaler(unittest.TestCase):
    def setUp(self):
        pass

    def test_should_allow_logging_file_journaler(self):
        filename = os.path.join(OUTPUT_DIR, 'journal_ut.txt')
        try:
            os.remove(filename)
        except OSError:
            pass

        journaler = FileJournaler(full_path=filename)
        journaler.start()
        journaler.log_event('this is a test event #1')
        journaler.log_event('this is a test event #2')
        journaler.log_event('this is a test event #3')
        journaler.log_event('this is a test event #4')
        journaler.log_event('this is a test event #5')

        time.sleep(0.2)
        journaler.stop()
        print('exit')

    def test_should_allow_to_read_string_journals(self):
        filename = os.path.join(OUTPUT_DIR, 'journal_read_ut.txt')
        try:
            os.remove(filename)
        except OSError:
            pass

        print('writing..')
        journaler = FileJournaler(full_path=filename)
        journaler.start()
        event = 'this is a test event #1'
        journaler.log_event(event)

        time.sleep(0.2)
        journaler.stop()
        print('reading..')

        eq = Queue()
        reader = FileJournalerReader(eq, full_path=filename)
        reader.read_events()
        try:
            message = eq.get_nowait()
            self.assertEqual(event, message)
        except Empty:
            pass

    def test_should_allow_creation_of_journal_file_using_full_path(self):
        filename = os.path.join(OUTPUT_DIR, 'journal_ut.txt')
        try:
            os.remove(filename)
        except OSError:
            pass

        journaler = FileJournaler(full_path=filename)
        journaler.start()
        journaler.stop()
        self.assertTrue(os.path.exists(filename))

    def test_scheme_should_give_correct_name_for_default_path(self):
        scheme = JournalNamingScheme()
        self.assertEqual('journal.txt', scheme.get_file_name())

    def test_scheme_should_give_correct_name_for_specific_path(self):
        scheme = JournalNamingScheme(path='/tmp')
        self.assertEqual('/tmp/journal.txt', scheme.get_file_name())

    def test_scheme_should_give_correct_name_for_specific_path_with_prefix(self):
        scheme = JournalNamingScheme(path='/tmp', name='jjj', prefix='aaa', suffix='qqq', ext='.lst')
        self.assertEqual('/tmp/aaajjjqqq.lst', scheme.get_file_name())

    def test_should_allow_creation_of_journal_file_using_name_scheme(self):
        scheme = JournalNamingScheme(path=OUTPUT_DIR, name='journal_ut')
        filename = scheme.get_file_name()
        try:
            os.remove(filename)
        except OSError:
            pass

        journaler = FileJournaler(name_scheme=scheme)
        journaler.start()
        journaler.stop()
        self.assertTrue(os.path.exists(filename))

    def test_should_allow_running_journal_in_an_event_loop(self):
        scheme = JournalNamingScheme(path=OUTPUT_DIR, name='journal_ut')
        filename = scheme.get_file_name()
        try:
            os.remove(filename)
        except OSError:
            pass

        eq = Queue()
        journaler = FileJournaler(name_scheme=scheme)
        looper = EventLoop(eq, journaler)
        loop_thread = Thread(target=looper.start, args=[])
        loop_thread.start()
        event = 'this is a dummy event for running journaler in a evnt loop'
        journaler.log_event(event)
        time.sleep(looper.heartbeat*2)
        journaler.stop()
        looper.stop()
        loop_thread.join(looper.heartbeat*2)
        self.assertTrue(event, journaler.get_last_event())
