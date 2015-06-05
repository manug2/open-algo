__author__ = 'ManuGarg'

import sys

sys.path.append('../../main')
import unittest

from com.open.algo.utils import read_settings
from com.open.algo.journal import Journaler
from com.open.algo.oanda.environments import ENVIRONMENTS, CONFIG_PATH_FOR_UNIT_TESTS
from com.open.algo.oanda.history import *

TARGET_ENV = "practice"


class TestHistoric(unittest.TestCase):

    def setUp(self):
        self.journaler = Journaler()
        domain = ENVIRONMENTS['api'][TARGET_ENV]
        settings = read_settings(CONFIG_PATH_FOR_UNIT_TESTS, TARGET_ENV)

        self.streamer = HistoricForexPrices(
            domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID']
        )

    def test_should_query_prices(self):
        rates = self.streamer.query('EUR_USD')
        print(rates)
        self.assertIsNotNone(rates)
