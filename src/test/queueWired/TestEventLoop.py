__author__ = 'ManuGarg'

import sys

sys.path.append('../../main')
import unittest
from queue import Queue
from threading import Thread
from com.open.algo.wiring.eventLoop import *
from com.open.algo.utils import get_time
from com.open.algo.dummy import DummyEventHandler
from com.open.algo.journal import *
OUTPUT_DIR = '../output/'


class TestEventLoop(unittest.TestCase):

    def setUp(self):
        self.events = Queue()
        self.handler = DummyEventHandler()
        self.looper = EventLoop(self.events, self.handler, 0.3)

        self.batched_input_events = list()
        self.batched_input_events.append('Hello')
        self.batched_input_events.append('World')
        self.batched_input_events.append('!!')

    def test_input_event_should_have_been_consumed(self):
        thread = Thread(target=self.looper.start, args=[])
        thread.start()
        self.events.put('dummy event')
        sleep(2*self.looper.heartbeat)
        self.looper.stop()
        thread.join(timeout=2*self.looper.heartbeat)
        try:
            ev = self.events.get_nowait()
            self.fail('should have been empty, got event %s' % ev)
        except Empty:
            pass

    def test_all_input_events_should_have_been_consumed(self):
        price_thread = Thread(target=self.looper.start, args=[])
        price_thread.start()
        self.events.put('dummy event #1')
        self.events.put('dummy event #2')
        self.events.put('dummy event #3')
        sleep(2*self.looper.heartbeat)
        self.looper.stop()
        price_thread.join(timeout=2*self.looper.heartbeat)
        try:
            ev = self.events.get_nowait()
            self.fail('should have been empty, got event %s' % ev)
        except Empty:
            pass

    def test_exception_queue_should_get_event_when_processing_none(self):
        exceptions_q = Queue()
        looper = EventLoop(self.events, self.handler, 0.1, exceptions_q)
        price_thread = Thread(target=looper.start, args=[])
        price_thread.start()
        self.events.put(None)
        sleep(2*looper.heartbeat)
        looper.stop()
        price_thread.join(timeout=2*looper.heartbeat)
        out_event = exceptions_q.get_nowait()
        self.assertIsNone(out_event.orig_event)

    def test_exception_message_has_correct_caller(self):
        exceptions_q = Queue()
        looper = EventLoop(self.events, self.handler, 0.1, exceptions_q)
        price_thread = Thread(target=looper.start, args=[])
        price_thread.start()
        self.events.put(None)
        sleep(2*looper.heartbeat)
        looper.stop()
        price_thread.join(timeout=2*looper.heartbeat)
        out_event = exceptions_q.get_nowait()
        self.assertEqual('EventLoop[DummyEventHandler]', out_event.caller)

    def test_forwarded_event_should_be_same_as_input_event(self):
        events = Queue()
        forward_q = Queue()
        looper = EventLoop(events, DummyEventHandler(), forward_q=forward_q)
        price_thread = Thread(target=looper.start, args=[])
        price_thread.start()
        events.put('dummy event')
        sleep(2*looper.heartbeat)
        looper.stop()
        price_thread.join(timeout=2*looper.heartbeat)
        out_event = forward_q.get_nowait()
        self.assertEqual('dummy event', out_event)

    def test_should_not_forwarded_event_when_forward_q_is_full(self):
        events = Queue()
        dummy_forwarded_event = 'i was forwarded earlier'
        forward_q = Queue(maxsize=1)
        looper = EventLoop(events, DummyEventHandler(), forward_q=forward_q)

        forward_q.put_nowait(dummy_forwarded_event)
        price_thread = Thread(target=looper.start, args=[])
        price_thread.start()
        events.put('dummy event')
        sleep(2*looper.heartbeat)
        looper.stop()
        price_thread.join(timeout=2*looper.heartbeat)
        out_event = forward_q.get_nowait()
        self.assertEqual(dummy_forwarded_event, out_event)
        try:
            forward_q.get_nowait()
            self.fail('forward_q should be empty as the previous dummy message would have filled it')
        except Empty:
            pass

    def test_processed_event_should_be_same_as_input_event_when_dummy_handler(self):
        events = Queue()
        processed_event_q = Queue()
        looper = EventLoop(events, DummyEventHandler(), processed_event_q=processed_event_q)
        price_thread = Thread(target=looper.start, args=[])
        price_thread.start()
        ev = 'dummy event'
        events.put(ev)
        sleep(2*looper.heartbeat)
        looper.stop()
        price_thread.join(timeout=2*looper.heartbeat)
        out_event = processed_event_q.get_nowait()
        self.assertEqual(ev, out_event)

    def test_forwarded_and_processed_event_should_be_same_as_input_event_when_dummy_handler(self):
        events = Queue()
        forward_q = Queue()
        processed_event_q = Queue()
        looper = EventLoop(events, DummyEventHandler(), forward_q=forward_q, processed_event_q=processed_event_q)
        price_thread = Thread(target=looper.start, args=[])
        price_thread.start()
        ev = 'dummy event'
        events.put(ev)
        sleep(2*looper.heartbeat)
        looper.stop()
        price_thread.join(timeout=2*looper.heartbeat)
        self.assertEqual(ev, forward_q.get_nowait())
        self.assertEqual(ev, processed_event_q.get_nowait())

    def test_exception_and_forwarded_and_processed_queues_behave_correctly_when_dummy_handler_and_bad_event(self):
        events = Queue()
        exceptions_q = Queue()
        forward_q = Queue()
        processed_event_q = Queue()
        looper = EventLoop(events, DummyEventHandler(), exceptions_q=exceptions_q,
                           forward_q=forward_q, processed_event_q=processed_event_q)
        price_thread = Thread(target=looper.start, args=[])
        price_thread.start()
        ev = None
        events.put(ev)
        sleep(2*looper.heartbeat)
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

    def test_input_event_should_have_been_consumed_when_set_process_all_is_off(self):
        self.looper.set_process_all_off()
        thread = Thread(target=self.looper.start, args=[])
        thread.start()
        self.events.put('dummy event')
        sleep(2*self.looper.heartbeat)
        self.looper.stop()
        thread.join(timeout=2*self.looper.heartbeat)
        try:
            ev = self.events.get_nowait()
            self.fail('should have been empty, got event %s' % ev)
        except Empty:
            pass

    def test_should_process_one_available_event_when_set_process_all_is_on(self):
        events = Queue()
        forward_q = Queue()
        looper = EventLoop(events, DummyEventHandler(), forward_q=forward_q).set_process_all_on()
        price_thread = Thread(target=looper.start, args=[])
        price_thread.start()
        events.put('dummy event')
        sleep(2*looper.heartbeat)
        looper.stop()
        price_thread.join(timeout=2*looper.heartbeat)
        out_event = forward_q.get_nowait()
        self.assertEqual('dummy event', out_event)

    def test_should_process_all_events_in_one_go_when_set_process_all_is_on(self):
        expected_out_event = 'Hello World !!'

        events = Queue()
        processed_event_q = Queue()
        looper = EventLoop(events, DummyEventHandler(), processed_event_q=processed_event_q).set_process_all_on()

        for event in self.batched_input_events:
            events.put(event)

        price_thread = Thread(target=looper.start, args=[])
        price_thread.start()
        sleep(2*looper.heartbeat)
        looper.stop()
        price_thread.join(timeout=2*looper.heartbeat)
        out_event = processed_event_q.get_nowait()
        try:
            processed_event_q.get_nowait()
            self.fail('should have combined all inputs into one processed event and this queue should have been empty')
        except Empty:
            pass
        self.assertEqual(expected_out_event, out_event)

    def test_should_forward_all_events_when_set_process_all_is_on(self):
        events = Queue()
        forward_q = Queue()
        looper = EventLoop(events, DummyEventHandler(), forward_q=forward_q).set_process_all_on()

        for event in self.batched_input_events:
            events.put(event)

        price_thread = Thread(target=looper.start, args=[])
        price_thread.start()
        sleep(2*looper.heartbeat)
        looper.stop()
        price_thread.join(timeout=2*looper.heartbeat)
        try:
            for i in range(1, len(self.batched_input_events)+1):
                forwarded = forward_q.get_nowait()
                self.assertEqual(self.batched_input_events.pop(0), forwarded)
        except Empty:
            pass
        self.assertEqual(0, len(self.batched_input_events))

    def test_should_not_forward_all_events_when_queue_is_full_and_set_process_all_is_on(self):
        events = Queue()
        forward_q = Queue(maxsize=2)
        looper = EventLoop(events, DummyEventHandler(), forward_q=forward_q).set_process_all_on()

        for event in self.batched_input_events:
            events.put(event)

        price_thread = Thread(target=looper.start, args=[])
        price_thread.start()
        sleep(2*looper.heartbeat)
        looper.stop()
        price_thread.join(timeout=2*looper.heartbeat)
        try:
            for i in range(1, len(self.batched_input_events)+1):
                forwarded = forward_q.get_nowait()
                self.assertEqual(self.batched_input_events.pop(0), forwarded)
        except Empty:
            pass
        self.assertEqual(1, len(self.batched_input_events))
        self.assertEqual('!!', self.batched_input_events.pop(0))


class TestFileJounaler(unittest.TestCase):
    def setUp(self):
        pass

    def test_should_allow_logging_file_journaler(self):
        filename = os.path.join(OUTPUT_DIR, 'journal_ut.txt')
        try:
            os.remove(filename)
        except OSError:
            pass

        journaler = FileJournaler(Queue(), full_path=filename)
        journaler.start()
        journaler.log_event(get_time(), 'this is a test event #1')
        journaler.log_event(get_time(), 'this is a test event #2')
        journaler.log_event(get_time(), 'this is a test event #3')
        journaler.log_event(get_time(), 'this is a test event #4')
        journaler.log_event(get_time(), 'this is a test event #5')

        sleep(0.2)
        journaler.close()
        print('exit')

    def test_should_allow_to_read_string_journals(self):
        filename = os.path.join(OUTPUT_DIR, 'journal_read_ut.txt')
        try:
            os.remove(filename)
        except OSError:
            pass

        print('writing..')
        journaler = FileJournaler(Queue(), full_path=filename)
        journaler.start()
        event = 'this is a test event #1'
        journaler.log_event(get_time(), event)

        sleep(0.2)
        journaler.close()
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

        journaler = FileJournaler(Queue(), full_path=filename)
        journaler.start()
        journaler.close()
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

        journaler = FileJournaler(Queue(), name_scheme=scheme)
        journaler.start()
        journaler.close()
        self.assertTrue(os.path.exists(filename))

    def test_should_allow_running_journal_in_an_event_loop(self):
        scheme = JournalNamingScheme(path=OUTPUT_DIR, name='journal_ut')
        filename = scheme.get_file_name()
        try:
            os.remove(filename)
        except OSError:
            pass

        eq = Queue()
        journaler = FileJournaler(eq, name_scheme=scheme)
        looper = EventLoop(eq, journaler)
        loop_thread = Thread(target=looper.start, args=[])
        loop_thread.start()
        event = 'this is a dummy event for running journaler in a evnt loop'
        journaler.log_event(get_time(), event)
        sleep(looper.heartbeat*2)
        journaler.stop()
        looper.stop()
        loop_thread.join(looper.heartbeat*2)
        journaler.close()
        self.assertTrue(event, journaler.get_last_event())
