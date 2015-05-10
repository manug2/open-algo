__author__ = 'ManuGarg'

import sys

sys.path.append('../../main')
import unittest

import threading, time
from com.open.algo.eventLoop import *
import os


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
        out_event = self.journaler.get_last_event()
        self.assertIsNone(out_event)

    def test_journaler_should_get_event_when_input_event(self):
        price_thread = threading.Thread(target=self.looper.start, args=[])
        price_thread.start()
        self.events.put('dummy event')
        time.sleep(0.2)
        self.looper.stop()
        price_thread.join(timeout=0.2)
        out_event = self.journaler.get_last_event()
        self.assertIsNotNone(out_event)

    def test_journaler_should_get_event_same_as_input_event(self):
        price_thread = threading.Thread(target=self.looper.start, args=[])
        price_thread.start()
        self.events.put('dummy event')
        time.sleep(0.2)
        self.looper.stop()
        price_thread.join(timeout=0.2)
        out_event = self.journaler.get_last_event()
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


class TestFileJounaler(unittest.TestCase):
    def setUp(self):
        pass

    def test_should_allow_logging_file_journaler(self):
        filename = 'journal_ut.txt'
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
        filename = 'journal_read_ut.txt'
        try:
            os.remove(filename)
        except OSError:
            pass

        print('writing..')
        journaler = FileJournaler(full_path=filename)
        journaler.start()
        journaler.log_event('this is a test event #1')

        time.sleep(0.2)
        journaler.stop()
        print('reading..')

        eq = Queue()
        reader = FileJournalerReader(eq, full_path=filename)
        reader.read_events()
        try:
            message = eq.get()
            self.assertEqual('this is a test event #1', message)
        except Empty:
            pass

    def test_should_allow_creation_of_journal_file_using_full_path(self):
        filename = 'journal_ut.txt'
        try:
            os.remove(filename)
        except OSError:
            pass

        journaler = FileJournaler(full_path=filename)
        journaler.start()
        journaler.stop()
        self.assertTrue(os.path.exists(filename))

    def test_scheme_should_give_correct_name_for_default_path(self):
        scheme = FileJournalerNamingScheme()
        self.assertEqual('journal.txt', scheme.get_file_name())

    def test_scheme_should_give_correct_name_for_specific_path(self):
        scheme = FileJournalerNamingScheme(path='/tmp')
        self.assertEqual('/tmp/journal.txt', scheme.get_file_name())

    def test_scheme_should_give_correct_name_for_specific_path_with_prefix(self):
        scheme = FileJournalerNamingScheme(path='/tmp', name='jjj', prefix='aaa', suffix='qqq', ext='.lst')
        self.assertEqual('/tmp/aaajjjqqq.lst', scheme.get_file_name())


    def test_should_allow_creation_of_journal_file_using_name_scheme(self):
        scheme = FileJournalerNamingScheme(name='journal_ut')
        filename = scheme.get_file_name()
        try:
            os.remove(filename)
        except OSError:
            pass

        journaler = FileJournaler(name_scheme=scheme)
        journaler.start()
        journaler.stop()
        self.assertTrue(os.path.exists(filename))
