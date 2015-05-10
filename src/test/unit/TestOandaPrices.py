__author__ = 'ManuGarg'

import sys

sys.path.append('../../main')
import unittest

import queue, threading, time

from com.open.algo.utils import read_settings
from com.open.algo.eventLoop import Journaler
from com.open.algo.oanda.environments import ENVIRONMENTS, CONFIG_PATH_FOR_UNIT_TESTS

from com.open.algo.oanda.streaming import *
from com.open.algo.oanda.history import *


TARGET_ENV = "practice"


class TestStreaming(unittest.TestCase):

    def setUp(self):
        self.journaler = Journaler()
        domain = ENVIRONMENTS['streaming'][TARGET_ENV]
        settings = read_settings(CONFIG_PATH_FOR_UNIT_TESTS, TARGET_ENV)

        events = queue.Queue()
        exceptions = queue.Queue()
        self.prices = StreamingForexPrices(
            domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID'],
            'EUR_USD', events, self.journaler, exceptions
        )

    def test_should_stream_prices(self):
        price_thread = threading.Thread(target=self.prices.stream, args=[])
        price_thread.start()
        time.sleep(2.5)
        self.prices.stop()
        price_thread.join(timeout=2)
        out_event = self.journaler.getLastEvent()
        self.assertIsNotNone(out_event)


class TestHistoric(unittest.TestCase):

    def setUp(self):
        self.journaler = Journaler()
        domain = ENVIRONMENTS['api'][TARGET_ENV]
        settings = read_settings(CONFIG_PATH_FOR_UNIT_TESTS, TARGET_ENV)

        self.prices = HistoricForexPrices(
            domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID']
        )

    def test_should_stream_prices(self):
        rates = self.prices.query('EUR_USD')
        print (rates)
        self.assertIsNotNone(rates)