__author__ = 'ManuGarg'

import sys

sys.path.append('../../main')
import unittest
from com.open.algo.journal import FileJournaler, FileJournalerReader
from com.open.algo.oanda.streaming import *
from com.open.algo.oanda.parser import *
from com.open.algo.utils import get_time
from queue import Queue, Empty

TARGET_ENV = "practice"
OA_OUTPUT_DIR = '../output/'


class TestPriceJournals(unittest.TestCase):

    def setUp(self):
        self.filename = os.path.join(OA_OUTPUT_DIR, 'journal_tick_ut.txt')
        try:
            os.remove(self.filename)
        except OSError:
            pass

        self.tick_str = \
            '{"tick": {"instrument": "EUR_USD", "time": "2015-05-08T20:59:45.031348Z", "bid": 1.11975, "ask": 1.12089}}'
        self.tick_json = json.loads(self.tick_str)
        self.tick_event = parse_tick(None, self.tick_json)

        self.write_q = Queue()
        self.journal_q = Queue()
        self.journaler = FileJournaler(self.journal_q, full_path=self.filename)

        self.read_q = Queue()
        self.reader = FileJournalerReader(self.read_q, full_path=self.filename)

    def play_event_queue(self):
        try:
            while True:
                e = self.journal_q.get_nowait()
                self.journaler.process(e)
        except Empty:
            pass
        self.journaler.close()

    def test_should_allow_to_read_oanda_like_tick_journals_from_file(self):
        print('writing..')
        self.journaler.start()
        self.journaler.log_event(get_time(), self.tick_str)
        self.play_event_queue()

        print('reading..')
        self.reader.read_events()
        try:
            ev_str = self.read_q.get_nowait()
            self.assertEqual(self.tick_str, ev_str)
        except Empty:
            self.fail('expecting a message from read queue')

    def test_should_allow_to_read_oanda_like_tick_journals_from_file_using_thread(self):
        print('writing..')
        self.journaler.start()
        self.journaler.log_event(get_time(), self.tick_str)
        self.play_event_queue()

        print('reading..')
        self.reader.read_events()
        try:
            ev_str = self.read_q.get_nowait()
            self.assertEqual(self.tick_str, ev_str)
        except Empty:
            self.fail('expecting a message from read queue')

    def test_should_allow_to_read_oanda_tick_journals_from_file_when_loaded_as_json(self):
        print('writing..')
        self.journaler.start()
        self.journaler.log_event(get_time(), self.tick_str)
        self.play_event_queue()

        print('reading..')
        self.reader.read_events()
        try:
            ev_str = self.read_q.get_nowait()
            ev_json = json.loads(ev_str)
            self.assertEqual(self.tick_json, ev_json)
        except Empty:
            self.fail('expecting a message from read queue')

    def test_should_allow_to_read_oanda_like_tick_journals_from_file_when_loaded_as_tick_event(self):
        print('writing..')
        self.journaler.start()
        self.journaler.log_event(get_time(), self.tick_str)
        self.play_event_queue()

        print('reading..')
        self.reader.read_events()
        try:
            ev_str = self.read_q.get_nowait()
            ev_json = json.loads(ev_str)
            ev_tick = parse_tick(None, ev_json)
            self.assertEqual(self.tick_event, ev_tick)
        except Empty:
            self.fail('expecting a message from read queue')

