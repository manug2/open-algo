__author__ = 'ManuGarg'

import os
import sys

sys.path.append('../../main')
import unittest
from configparser import ConfigParser

from com.open.algo.oanda.environments import ENVIRONMENTS, CONFIG_PATH
import queue, threading, time

from com.open.algo.utils import Journaler
from com.open.algo.oanda.streaming import *
from com.open.algo.oanda.history import *
from com.open.algo.oanda.environments import ENVIRONMENTS


TARGET_ENV = "practice"


class TestStreaming(unittest.TestCase):

    def setUp(self):
        self.journaler = Journaler()
        domain = ENVIRONMENTS['streaming'][TARGET_ENV]
        config = ConfigParser()
        config.read(os.path.join(CONFIG_PATH, TARGET_ENV + '.oanda.config'))
        ACCESS_TOKEN = config.get('CONFIG', 'ACCESS_TOKEN')
        ACCOUNT_ID = config.get('CONFIG', 'ACCOUNT_ID')

        events = queue.Queue()
        exceptions = queue.Queue()
        self.prices = StreamingForexPrices(
            domain, ACCESS_TOKEN, ACCOUNT_ID,
            'EUR_USD', events, self.journaler, exceptions
        )

    def should_stream_prices(self):
        price_thread = threading.Thread(target=self.prices.stream, args=[])
        price_thread.start()
        time.sleep(2.5)
        self.prices.stop()
        price_thread.join(timeout=2)
        outEvent = self.journaler.getLastEvent()
        self.assertIsNotNone(outEvent)


class TestHistoric(unittest.TestCase):

    def setUp(self):
        self.journaler = Journaler()
        domain = ENVIRONMENTS['api'][TARGET_ENV]
        config = ConfigParser()
        config.read(os.path.join(CONFIG_PATH, TARGET_ENV + '.oanda.config'))
        ACCESS_TOKEN = config.get('CONFIG', 'ACCESS_TOKEN')
        ACCOUNT_ID = config.get('CONFIG', 'ACCOUNT_ID')

        self.prices = HistoricForexPrices(
            domain, ACCESS_TOKEN, ACCOUNT_ID
        )

    def test_should_stream_prices(self):
        rates = self.prices.query('EUR_USD')
        print (rates)
        self.assertIsNotNone(rates)