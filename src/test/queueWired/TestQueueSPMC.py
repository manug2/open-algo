__author__ = 'ManuGarg'

import sys

sys.path.append('../../main')
import unittest
from com.open.algo.journal import Journaler
from com.open.algo.wiring.queue_spmc import *


class TestNonBlockingPutMethod(unittest.TestCase):

    def setUp(self):
        self.spmc_q = QueueSPMC(Journaler())
        self.consumer_queues = list()
        self.spmc_put_method = self.spmc_q.put_nowait

    def tearDown(self):
        pass

    def append_consumers(self, count):
        for i in range(0, count):
            cons = Queue()
            self.consumer_queues.append(cons)
            self.spmc_q.add_consumer(cons)

    def test_single_consumer_can_get_event(self):
        self.append_consumers(1)
        event = 'this is an event'
        self.spmc_put_method(event)

        try:
            out = self.consumer_queues[0].get_nowait()
            self.assertEqual(event, out)
        except Empty:
            self.fail('should have one event in the consumer queue')

    def test_two_consumers_can_get_event(self):
        self.append_consumers(2)
        event = 'this is an event'
        self.spmc_put_method(event)

        try:
            out = self.consumer_queues[0].get_nowait()
            self.assertEqual(event, out)
        except Empty:
            self.fail('should have one event in the 1st consumer queue')

        try:
            out = self.consumer_queues[1].get_nowait()
            self.assertEqual(event, out)
        except Empty:
            self.fail('should have one event in the 2nd consumer queue')

    def test_5_consumers_can_get_event(self):
        count = 5
        self.append_consumers(count)
        event = 'this is an event'
        self.spmc_put_method(event)

        for i in range(0, count):
            try:
                out = self.consumer_queues[i].get_nowait()
                self.assertEqual(event, out)
            except Empty:
                self.fail('should have one event in the consumer queue # %s' % i)

    def test_should_log_journal_when_single_consumer_is_full(self):
        cons = Queue(maxsize=1)
        self.consumer_queues.append(cons)
        self.spmc_q.add_consumer(cons)
        other_event = 'there is some other event'
        cons.put(other_event)

        event = 'this is an event'
        self.spmc_put_method(event)
        last_journal = self.spmc_q.journaler.get_last_event()
        jounrnal_orig_event = parse_journal(last_journal)
        self.assertEqual(event, jounrnal_orig_event)

        try:
            out = self.consumer_queues[0].get_nowait()
            self.assertNotEquals(event, out)
            self.assertEqual(other_event, out)

        except Empty:
            self.fail('should have one other event in the consumer queue')

    def test_should_log_journal_when_first_consumer_is_full(self):
        cons1 = Queue(maxsize=1)
        self.consumer_queues.append(cons1)
        self.spmc_q.add_consumer(cons1)

        cons2 = Queue()
        self.consumer_queues.append(cons2)
        self.spmc_q.add_consumer(cons2)

        other_event = 'there is some other event'
        cons1.put(other_event)

        event = 'this is an event'
        self.spmc_put_method(event)
        last_journal = self.spmc_q.journaler.get_last_event()
        jounrnal_orig_event = parse_journal(last_journal)
        self.assertEqual(event, jounrnal_orig_event)

        try:
            out = cons1.get_nowait()
            self.assertNotEquals(event, out)
            self.assertEqual(other_event, out)

        except Empty:
            self.fail('should have one other event in the consumer queue')

        try:
            out = cons2.get_nowait()
            self.assertEqual(event, out)
        except Empty:
            self.fail('should have one event in the 2nd consumer queue')

    def test_should_log_journal_when_second_consumer_is_full(self):
        cons1 = Queue()
        self.consumer_queues.append(cons1)
        self.spmc_q.add_consumer(cons1)

        cons2 = Queue(maxsize=1)
        self.consumer_queues.append(cons2)
        self.spmc_q.add_consumer(cons2)

        other_event = 'there is some other event'
        cons2.put(other_event)

        event = 'this is an event'
        self.spmc_put_method(event)
        last_journal = self.spmc_q.journaler.get_last_event()
        jounrnal_orig_event = parse_journal(last_journal)
        self.assertEqual(event, jounrnal_orig_event)

        try:
            out = cons1.get_nowait()
            self.assertEqual(event, out)
        except Empty:
            self.fail('should have one other event in the consumer queue')

        try:
            out = cons2.get_nowait()
            self.assertNotEquals(event, out)
            self.assertEqual(other_event, out)
        except Empty:
            self.fail('should have one event in the 2nd consumer queue')


class TestBlockingPutMethod(TestNonBlockingPutMethod):

    def setUp(self):
        self.spmc_q = QueueSPMC(Journaler())
        self.consumer_queues = list()
        self.spmc_put_method = self.spmc_q.put

    def tearDown(self):
        pass


class TestBlockingThreadedPutMethod(TestNonBlockingPutMethod):

    def setUp(self):
        self.spmc_q = QueueThreadedSPMC(Journaler())
        self.consumer_queues = list()
        self.spmc_put_method = self.spmc_q.put

    def tearDown(self):
        self.spmc_q.stop()
