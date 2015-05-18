__author__ = 'ManuGarg'

import sys

sys.path.append('../../main')
import unittest
from com.open.algo.eventLoop import *
import os
from threading import Thread
import queue, threading, time
from com.open.algo.oanda.streaming import *

TARGET_ENV = "practice"
OA_OUTPUT_DIR = '../output/'


class TestPriceJournals(unittest.TestCase):

    def setUp(self):
        self.filename = os.path.join(OA_OUTPUT_DIR, 'journal_oanda_tick_ut.txt')
        try:
            os.remove(self.filename)
        except OSError:
            pass

        self.tick_str = \
            '{"tick": {"instrument": "EUR_USD", "time": "2015-05-08T20:59:45.031348Z", "bid": 1.11975, "ask": 1.12089}}'
        self.tick_json = json.loads(self.tick_str)
        self.tick_event = parse_tick(self.tick_json)

        self.write_q = Queue()
        self.journaler = FileJournaler(full_path=self.filename)
        self.looper = EventLoop(self.write_q, self.journaler)
        self.loop_thread = Thread(target=self.looper.start, args=[])

        self.read_q = Queue()
        self.reader = FileJournalerReader(self.read_q, full_path=self.filename)

    def test_should_allow_to_read_oanda_tick_journals_from_file(self):
        print('writing..')
        self.loop_thread.start()
        self.write_q.put_nowait(self.tick_str)
        time.sleep(2*self.looper.heartbeat)
        self.looper.stop()
        self.loop_thread.join(2*self.looper.heartbeat)

        print('reading..')
        self.reader.read_events()
        try:
            ev_str = self.read_q.get_nowait()
            self.assertEqual(self.tick_str, ev_str)
        except Empty:
            self.fail('expecting a message from read queue')

    def test_should_allow_to_read_oanda_tick_journals_from_file_when_loaded_as_json(self):
        print('writing..')
        self.loop_thread.start()
        self.write_q.put_nowait(self.tick_str)
        time.sleep(2*self.looper.heartbeat)
        self.looper.stop()
        self.loop_thread.join(2*self.looper.heartbeat)

        print('reading..')
        self.reader.read_events()
        try:
            ev_str = self.read_q.get_nowait()
            ev_json = json.loads(ev_str)
            self.assertEqual(self.tick_json, ev_json)
        except Empty:
            self.fail('expecting a message from read queue')

    def test_should_allow_to_read_oanda_tick_journals_from_file_when_loaded_as_tick_event(self):
        print('writing..')
        self.loop_thread.start()
        self.write_q.put_nowait(self.tick_str)
        time.sleep(2*self.looper.heartbeat)
        self.looper.stop()
        self.loop_thread.join(2*self.looper.heartbeat)

        print('reading..')
        self.reader.read_events()
        try:
            ev_str = self.read_q.get_nowait()
            ev_json = json.loads(ev_str)
            ev_tick = parse_tick(ev_json)
            self.assertEqual(self.tick_event, ev_tick)
        except Empty:
            self.fail('expecting a message from read queue')

