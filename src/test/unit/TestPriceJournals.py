__author__ = 'ManuGarg'

import sys

sys.path.append('../../main')
import unittest
from com.open.algo.eventLoop import *
import time, os, json
from com.open.algo.oanda.streaming import parse_tick_event


class TestPriceJournals(unittest.TestCase):

    def test_should_allow_to_read_oanda_tick_journals(self):
        filename = 'journal_oanda_tick_ut.txt'
        try:
            os.remove(filename)
        except OSError:
            pass

        tick_str = '{\"tick\": {\"instrument\": \"EUR_USD\", \"time\": \"2015-05-08T20:59:45.031348Z\", \"bid\": 1.11975, \"ask\": 1.12089}}'
        tev = parse_tick_event(json.loads(tick_str))

        print('writing..')
        journaler = FileJournaler(full_path=filename)
        journaler.start()
        journaler.log_event(tick_str)

        time.sleep(0.2)
        journaler.stop()
        print('reading..')

        eq = Queue()
        reader = FileJournalerReader(eq, full_path=filename)
        reader.read_events()
        try:
            ev_dict = eq.get()
        except Empty:
            pass
        ev = parse_tick_event(ev_dict)
        self.assertEqual(tev, ev)

