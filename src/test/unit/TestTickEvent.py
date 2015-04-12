import sys
sys.path.append('../../main')
import unittest

from com.open.algo.trading.fxEvents import TickEvent

class TestTickEvents(unittest.TestCase):

	def setUp(self):
		pass

	def testTickEventClassExists(self):
		self.assertNotEquals(TickEvent(None, None, None, None), None)

	def testTickEventHasExpectedType(self):
		self.assertEquals(TickEvent(None, None, None, None).TYPE, "TICK")

	def testTickEventHasExpectedInstrument(self):
		self.assertEquals(TickEvent("ABC", None, None, None).instrument, "ABC")

	def testTickEventHasExpectedTime(self):
		self.assertEquals(TickEvent(None, "12-33-45", None, None).time, "12-33-45")

	def testTickEventHasExpectedBid(self):
		self.assertEquals(TickEvent(None, None, 33.34, None).bid, 33.34)

	def testTickEventHasExpectedAsk(self):
		self.assertEquals(TickEvent(None, None, None, 123.4).ask, 123.4)
