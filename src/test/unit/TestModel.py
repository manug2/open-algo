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
        self.assertIsNotNone(Event())

    def testEventIsTypeNone(self):
        self.assertEquals(Event().TYPE, None)


    # DATA HANDLER
    def testDataHandlerClassExists(self):
        self.assertNotEquals(DataHandler(), None)

    def testDataHandlerIsTypeNone(self):
        self.assertEquals(DataHandler().TYPE, None)

    def testRStreamDataHandlerClassExists(self):
        self.assertNotEquals(StreamDataHandler(), None)

    def testStreamDataHandlerIsTypeNone(self):
        self.assertEquals(StreamDataHandler().TYPE, None)


    # EXECUTION HANDLER
    def testExecutionHandlerClassExists(self):
        self.assertNotEquals(ExecutionHandler(), None)


    # PORTFOLIO HANDLER
    def testPortfolioClassExists(self):
        self.assertNotEquals(Portfolio(), None)


    # RISKMANAGER HANDLER
    def testRiskManagerClassExists(self):
        self.assertNotEquals(RiskManager(), None)
