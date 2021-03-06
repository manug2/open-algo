import sys

sys.path.append('../../main')
import unittest

from com.open.algo.model import *


class TestModel(unittest.TestCase):
    def setUp(self):
        pass

    def testNothing(self):
        self.assertEquals(None, None)

        # EVENT

    def testEventClassExists(self):
        self.assertIsNotNone(Event(None))

    def testEventHasType(self):
        self.assertEquals(Event('some').TYPE, 'some')


    # DATA HANDLER
    def testDataHandlerClassExists(self):
        self.assertNotEquals(DataProvider(), None)

    def testDataHandlerIsTypeNone(self):
        self.assertEquals(DataProvider().TYPE, None)

    def testRStreamDataHandlerClassExists(self):
        self.assertNotEquals(StreamDataProvider(), None)

    def testStreamDataHandlerIsTypeNone(self):
        self.assertEquals(StreamDataProvider().TYPE, None)


    # EXECUTION HANDLER
    def testExecutionHandlerClassExists(self):
        self.assertNotEquals(ExecutionHandler(), None)


    # PORTFOLIO HANDLER
    def testPortfolioClassExists(self):
        self.assertNotEquals(Portfolio(), None)


    # RISKMANAGER HANDLER
    def testRiskManagerClassExists(self):
        self.assertNotEquals(RiskManager(), None)
