import sys
sys.path.append('../../main')
import unittest

from com.open.algo.trading.fxEvents import OrderEvent

class TestOrderEvents(unittest.TestCase):

	def setUp(self):
		pass

	def testOrderEventClassExists(self):
		self.assertNotEquals(OrderEvent(None, None, None, None), None)

	def testOrderEventHasExpectedType(self):
		self.assertEquals(OrderEvent(None, None, None, None).TYPE, "ORDER")

	def testOrderEventHasExpectedInstrument(self):
		self.assertEquals(OrderEvent("ABC", None, None, None).instrument, "ABC")

	def testOrderEventHasExpectedUnits(self):
		self.assertEquals(OrderEvent(None, "125", None, None).units, "125")

	def testOrderEventHasExpectedOrderType(self):
		self.assertEquals(OrderEvent(None, None, "MKT", None).order_type, "MKT")

	def testOrderEventHasExpectedSide(self):
		self.assertEquals(OrderEvent(None, None, None, "SELL").side, "SELL")
