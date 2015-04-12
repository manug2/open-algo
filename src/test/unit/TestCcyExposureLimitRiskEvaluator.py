import sys
sys.path.append('../../main')
import unittest

from com.open.algo.risk.ccyExposureLimitRisk import CcyExposureLimitRiskEvaluator
from com.open.algo.trading.fxEvents import OrderEvent

class TestRiskManager(unittest.TestCase):

	def assignDummyRates(self, rm):
		rm.ratesMap['CHF'] = {}
		rm.ratesMap['CHF']['bid'] = 1.04
		rm.ratesMap['CHF']['ask'] = 1.05
		rm.ratesMap['EUR'] = {}
		rm.ratesMap['EUR']['bid'] = 1.08
		rm.ratesMap['EUR']['ask'] = 1.09
		rm.ratesMap['SGD'] = {}
		rm.ratesMap['SGD']['bid'] = 0.74
		rm.ratesMap['SGD']['ask'] = 0.75

	def setUp(self):
		self.rm = CcyExposureLimitRiskEvaluator('USD')
		self.assignDummyRates(self.rm)

	def testClassExists(self):
		self.assertNotEquals(CcyExposureLimitRiskEvaluator('BC'), None)

	def testHasBaseCurrency(self):
		self.assertNotEquals(CcyExposureLimitRiskEvaluator('BC').baseCcy, None)
		self.assertEquals(CcyExposureLimitRiskEvaluator('BC').baseCcy, 'BC')

	def testHasPositions(self):
		self.assertNotEquals(CcyExposureLimitRiskEvaluator('BC').positions, None)

	def testHasCcyExpLimit(self):
		self.assertNotEquals(CcyExposureLimitRiskEvaluator('BC').ccyLimit, None)

	def testHasPortfolioLimit(self):
		self.assertNotEquals(CcyExposureLimitRiskEvaluator('BC').portLimit, None)

	def testHasDefaultCcyExpLimit(self):
		rm = CcyExposureLimitRiskEvaluator('BC')
		self.assertTrue(rm.ccyLimit > 0)

	def testHasPresetCcyExpLimit(self):
		rm = CcyExposureLimitRiskEvaluator('BC', ccyLimit=123)
		self.assertEquals(rm.ccyLimit, 123)

	def testHasDefaultPortfolioLimit(self):
		rm = CcyExposureLimitRiskEvaluator('BC')
		self.assertTrue(rm.portLimit > 0)

	def testHasPresetPortfolioLimit(self):
		rm = CcyExposureLimitRiskEvaluator('BC', portLimit=1230)
		self.assertEquals(rm.portLimit, 1230)

	def testHasPerCcyExpLimit(self):
		self.assertNotEquals(CcyExposureLimitRiskEvaluator('BC').ccyLimits, None)

	def testCanInitWithPerCcyExpLimit(self):
		self.assertEquals(CcyExposureLimitRiskEvaluator('BC', ccyLimits={}).ccyLimits, {})

	def testCanInitWithPerCcyExpLimitCHF(self):
		ccyLimits = { 'CHF': 100.1}
		rm = CcyExposureLimitRiskEvaluator('BC', ccyLimits=ccyLimits)
		self.assertEquals(rm.ccyLimits['CHF'], 100.1)

	def testCannotFilterOrderWithoutRates(self):
		rmo = CcyExposureLimitRiskEvaluator('ABC')
		try:
			filtered = rmo.filter_order(OrderEvent('CHF_USD', 1000, 'market', 'buy'))
			self.fail('Filtered order without fx rates')
		except AssertionError:
			pass

	def testFilterOrder(self):
		filtered = self.rm.filter_order(OrderEvent('CHF_USD', 1000, 'market', 'buy'))
		self.assertNotEqual(None, filtered, 'Could not filter trade')

	def testFilterOrderHasCorrectInstrument(self):
		filtered = self.rm.filter_order(OrderEvent('CHF_USD', 100, 'market', 'buy'))
		self.assertEquals(filtered.instrument, 'CHF_USD')

	def testFilteredOrderHasCorrectSide(self):
		filtered = self.rm.filter_order(OrderEvent('CHF_USD', 100, 'market', 'buy'))
		self.assertEquals(filtered.side, 'buy')

	def testFilteredOrderHasCorrectSide2(self):
		filtered = self.rm.filter_order(OrderEvent('CHF_USD', 100, 'market', 'sell'))
		self.assertEquals(filtered.side, 'sell')

	def testFilteredOrderHasCorrectType(self):
		filtered = self.rm.filter_order(OrderEvent('CHF_USD', 100, 'market', 'buy'))
		self.assertEquals(filtered.order_type, 'market')

	def testFilterOrderCcyExpLimitNoBreach1stCcy(self):
		order = OrderEvent('CHF_USD', 100, 'market', 'buy')
		filtered = self.rm.filter_order(order)
		self.assertEquals(filtered.units, 100)

	def testFilterOrderPresetCcyExpLimitNoBreach1stCcy(self):
		rm = CcyExposureLimitRiskEvaluator('USD', ccyLimit=150)
		self.assignDummyRates(rm)
		order = OrderEvent('CHF_USD', 140, 'market', 'buy')
		filtered = self.rm.filter_order(order)
		self.assertEquals(filtered.units, 140)

	def testFilterOrderCcyExpLimitBreach1stCcy(self):
		order = OrderEvent('EUR_SGD', 10000, 'market', 'buy')
		filtered = self.rm.filter_order(order)
		self.assertNotEquals(filtered.units, 10000)
		amountInBase = round(self.rm.ccyLimit * self.rm.ratesMap['EUR']['ask'], 0)
		self.assertEquals(amountInBase, filtered.units)

	def testFilteredOrderSpecificLimitNoBreach1stCcy(self):
		ccyLimits = {'CHF': 1234}
		rm = CcyExposureLimitRiskEvaluator('USD', ccyLimit=100, ccyLimits=ccyLimits)
		self.assignDummyRates(rm)
		order = OrderEvent('CHF_USD', 1000, 'market', 'buy')
		filtered = rm.filter_order(order)
		self.assertEquals(filtered.units, 1000)

	def testFilteredOrderSpecificLimitBreach1stCcy(self):
		ccyLimits = {'CHF': 1234}
		rm = CcyExposureLimitRiskEvaluator('USD', ccyLimit=100, ccyLimits=ccyLimits)
		self.assignDummyRates(rm)
		order = OrderEvent('CHF_USD', 10000, 'market', 'buy')
		amountInBase = round(rm.ccyLimits['CHF'] * self.rm.ratesMap['CHF']['ask'], 0)
		filtered = rm.filter_order(order)
		self.assertEquals(amountInBase, filtered.units)

	def testFilterOrderCcyExpLimitNoBreach1stCcySell(self):
		order = OrderEvent('CHF_USD', 100, 'market', 'sell')
		filtered = self.rm.filter_order(order)

	def testFilteredOrderSpecificLimitNoBreach1stCcySell(self):
		ccyLimitsShort = {'CHF': -234}
		rm = CcyExposureLimitRiskEvaluator('USD', ccyLimit=100, ccyLimitsShort=ccyLimitsShort)
		self.assignDummyRates(rm)
		order = OrderEvent('CHF_USD', 100, 'market', 'sell')
		filtered = rm.filter_order(order)
		self.assertEquals(filtered.units, 100)

	def testFilterOrderPresetCcyExpLimitNoBreach1stCcySell(self):
		rm = CcyExposureLimitRiskEvaluator('USD', ccyLimitShort=-10)
		self.assignDummyRates(rm)
		order = OrderEvent('CHF_USD', 10, 'market', 'sell')
		filtered = self.rm.filter_order(order)
		self.assertEquals(filtered.units, 10)

	def testFilterOrderCcyExpLimitBreach1stCcySell(self):
		order = OrderEvent('EUR_SGD', 10000, 'market', 'sell')
		filtered = self.rm.filter_order(order)
		self.assertNotEquals(filtered.units, 10000)
		amountInBase = round(self.rm.ccyLimit * self.rm.ratesMap['EUR']['bid'], 0)
		self.assertEquals(amountInBase, filtered.units)

	def testFilteredOrderSpecificLimitLessThanDefault_Breach1stCcy(self):
		ccyLimits = {'CHF': 100}
		rm = CcyExposureLimitRiskEvaluator('USD', ccyLimit=1000, ccyLimits=ccyLimits)
		self.assignDummyRates(rm)
		order = OrderEvent('CHF_USD', 1000, 'market', 'buy')
		amountInBase = round(rm.ccyLimits['CHF'] * self.rm.ratesMap['CHF']['ask'], 0)
		filtered = rm.filter_order(order)
		self.assertEquals(amountInBase, filtered.units)

	def testFilteredOrderSpecificLimitMoreThanDefault_Breach1stCcy(self):
		ccyLimits = {'CHF': 10000}
		rm = CcyExposureLimitRiskEvaluator('USD', ccyLimit=1000, ccyLimits=ccyLimits)
		self.assignDummyRates(rm)
		order = OrderEvent('CHF_USD', 10000, 'market', 'buy')
		filtered = rm.filter_order(order)
		self.assertEquals(10000, filtered.units)

	def testFilteredOrderSpecificLimitLessThanDefault_Breach1stCcySell(self):
		ccyLimitsShort = {'CHF': -100}
		rm = CcyExposureLimitRiskEvaluator('USD', ccyLimitShort=-1000, ccyLimitsShort=ccyLimitsShort)
		self.assignDummyRates(rm)
		order = OrderEvent('CHF_USD', 1000, 'market', 'sell')
		amountInBase = round(-1 * rm.ccyLimitsShort['CHF'] * self.rm.ratesMap['CHF']['bid'], 0)
		filtered = rm.filter_order(order)
		self.assertEquals(amountInBase, filtered.units)
		self.assertEquals(filtered.instrument, 'CHF_USD')
		self.assertEquals(filtered.side, 'sell')

	def testFilteredOrderSpecificLimitMoreThanDefault_Breach1stCcySell(self):
		ccyLimitsShort = {'CHF': -10000}
		rm = CcyExposureLimitRiskEvaluator('USD', ccyLimitShort=-1000, ccyLimitsShort=ccyLimitsShort)
		self.assignDummyRates(rm)
		order = OrderEvent('CHF_USD', 10000, 'market', 'sell')
		filtered = rm.filter_order(order)
		self.assertEquals(10000, filtered.units)
		self.assertEquals(filtered.instrument, 'CHF_USD')
		self.assertEquals(filtered.side, 'sell')


	"""
	def testFilterOrderCcyExpLimitBreach_2Instruments(self):
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimit=100)
		order = OrderEvent('CHF_USD', 10000, 'market', 'buy')
		filtered = rm.filter_order(order)
		self.assertNotEquals(filtered.units, 10000)
		self.assertEquals(filtered.units, 100)

		order = OrderEvent('EUR_SGD', 10000, 'market', 'buy')
		filtered = rm.filter_order(order)
		self.assertNotEquals(filtered.units, 10000)
		self.assertEquals(filtered.units, 100)

	def testFilteredOrderSpecificLimitBreach_2Instruments(self):
		ccyLimits = {'CHF': 1234}
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimit=100, ccyLimits=ccyLimits)
		order = OrderEvent('CHF_USD', 10000, 'market', 'buy')
		filtered = rm.filter_order(order)
		self.assertEquals(filtered.units, 1234)

		order = OrderEvent('EUR_SGD', 1000, 'market', 'buy')
		filtered = rm.filter_order(order)
		self.assertNotEquals(filtered.units, 1000)
		self.assertEquals(filtered.units, 100)

	def testFilteredOrderSpecificLimit_2InstrumentsBreahces(self):
		ccyLimits = {'CHF': 1234, 'EUR':10000}
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimit=100, ccyLimits=ccyLimits)
		filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'market', 'buy'))
		self.assertEquals(filtered.units, 1234)

		filtered = rm.filter_order(OrderEvent('EUR_SGD', 5000, 'market', 'buy'))
		self.assertEquals(filtered.units, 5000)

		filtered = rm.filter_order(OrderEvent('EUR_SGD', 50000, 'market', 'buy'))
		self.assertEquals(filtered.units, 10000)

	def testFilterBasedOnCcyExposure(self):
		rm = CcyExposureLimitRiskEvaluator('ABC')
		self.assertNotEquals(rm.ccyLimit, None)

	def testHasDefaultCurrencyLimit(self):
		rm = CcyExposureLimitRiskEvaluator('BC')
		self.assertTrue(rm.ccyLimit > 0)

	def testFilterBasedOnCcyExposure(self):
		rm = CcyExposureLimitRiskEvaluator('ABC')
		rm.ratesMap['CHF'] = {}
		rm.ratesMap['CHF']['bid'] = 0.8123
		rm.ratesMap['CHF']['ask'] = 0.8120
		self.assertEquals(rm.ratesMap['CHF']['bid'], 0.8123)
		self.assertEquals(rm.ratesMap['CHF']['ask'], 0.8120)

	#Short limits
	def testHasDefaultShortCcyExpLimit(self):
		rm = CcyExposureLimitRiskEvaluator('BC')
		self.assertTrue(rm.ccyLimitShort <= 0)

	def testHasPresetShortCcyExpLimit(self):
		rm = CcyExposureLimitRiskEvaluator('BC', ccyLimit=123, ccyLimitShort=-100)
		self.assertEquals(rm.ccyLimitShort, -100)

	def testWrongPresetShortCcyExpLimitRaisesError(self):
		try:
			rm = CcyExposureLimitRiskEvaluator('BC', ccyLimitShort=100)
			self.fail('Should have failed using +ve short position limit')
		except AssertionError:
			pass

	def testWrongPresetCcyExpLimitRaisesError(self):
		try:
			rm = CcyExposureLimitRiskEvaluator('BC', ccyLimit=-12)
			self.fail('Should have failed using -ve short position limit')
		except AssertionError:
			pass

	def testHasPerPositionShortLimit(self):
		self.assertNotEquals(CcyExposureLimitRiskEvaluator('BC').ccyLimitsShort, None)

	def testCanInitWithPerPositionShortLimit(self):
		self.assertEquals(CcyExposureLimitRiskEvaluator('BC', ccyLimitsShort={}).ccyLimitsShort, {})

	def testCanInitWithPerPositionShortLimitCHF(self):
		ccyLimitsShort = { 'CHF': -12.1}
		rm = CcyExposureLimitRiskEvaluator('BC', ccyLimitsShort=ccyLimitsShort)
		self.assertEquals(rm.ccyLimitsShort['CHF_USD'], -12.1)

	def testFilterOrderDefaultShortCcyExpLimitBreach(self):
		rm = CcyExposureLimitRiskEvaluator('ABC')
		order = OrderEvent('CHF_USD', 10000, 'market', 'sell')
		print (order)
		filtered = rm.filter_order(order)
		self.assertNotEquals(filtered.units, 10000)
		self.assertEquals(filtered.units, 0)

	def testFilterOrderShortCcyExpLimitBreach(self):
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimitShort=-100)
		order = OrderEvent('CHF_USD', 10000, 'market', 'sell')
		print (order)
		filtered = rm.filter_order(order)
		self.assertNotEquals(filtered.units, 10000)
		self.assertEquals(filtered.units, 100)

	def testFilteredOrderSpecificLimitNoBreachShort(self):
		ccyLimitsShort = {'CHF': -234}
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimitShort=-100, ccyLimitsShort=ccyLimitsShort)
		filtered = rm.filter_order(OrderEvent('CHF_USD', 200, 'market', 'sell'))
		self.assertEquals(filtered.units, 200)

	def testFilteredOrderSpecificLimitBreachShort(self):
		ccyLimitsShort = {'CHF': -234}
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimitShort=-100, ccyLimitsShort=ccyLimitsShort)
		filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'market', 'sell'))
		self.assertEquals(filtered.units, 234)


	#Current positions
	def testHasEmptyPositions(self):
		rm = CcyExposureLimitRiskEvaluator('BC')
		self.assertEquals(rm.positions, {})

	def testCanAppendPositions(self):
		rm = CcyExposureLimitRiskEvaluator('BC')
		rm.append_position('EUR_CHF', 123)

	def testHasAppendedPositions(self):
		rm = CcyExposureLimitRiskEvaluator('BC')
		rm.append_position('EUR_CHF', 123)
		self.assertEquals(rm.positions['EUR_CHF'], 123)

	def testCanAppendedSameIntrumentTwice(self):
		rm = CcyExposureLimitRiskEvaluator('BC')
		rm.append_position('EUR_CHF', 123)
		rm.append_position('EUR_CHF', 27)
		self.assertEquals(rm.positions['EUR_CHF'], 150)

	def testHas2AppendedPositions(self):
		rm = CcyExposureLimitRiskEvaluator('BC')
		rm.append_position('EUR_CHF', 123)
		rm.append_position('EUR_USD', 1000)
		self.assertEquals(rm.positions['EUR_CHF'], 123)
		self.assertEquals(rm.positions['EUR_USD'], 1000)

	def testHasAppendedPos_FilterOrderCcyExpLimitBreach(self):
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimit=100)
		rm.append_position('CHF', 10)
		order = OrderEvent('CHF_USD', 10000, 'market', 'buy')
		filtered = rm.filter_order(order)
		self.assertNotEquals(filtered.units, 10000)
		self.assertEquals(filtered.units, 90)

	def testHasAppendedPos_FilteredOrderSpecificLimitNoBreach(self):
		ccyLimits = {'CHF': 1234}
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimit=100, ccyLimits=ccyLimits)
		rm.append_position('CHF', 10)
		filtered = rm.filter_order(OrderEvent('CHF_USD', 1000, 'market', 'buy'))
		self.assertEquals(filtered.units, 1000)

	def testHasAppendedPos_FilteredOrderSpecificLimitBreach(self):
		ccyLimits = {'CHF': 1234}
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimit=100, ccyLimits=ccyLimits)
		rm.append_position('CHF', 100)
		filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'market', 'buy'))
		self.assertEquals(filtered.units, 1134)

	def testHasAppendedPos_FilteredOrderSpecificLimitLessThanDefault_Breach(self):
		ccyLimits = {'CHF': 100}
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimit=1000, ccyLimits=ccyLimits)
		rm.append_position('CHF', 10)
		filtered = rm.filter_order(OrderEvent('CHF_USD', 1000, 'market', 'buy'))
		self.assertEquals(filtered.units, 90)

	def testHasAppendedPos_FilterOrderCcyExpLimitBreach_2Instruments(self):
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimit=100)
		rm.append_position('CHF', 10)
		order = OrderEvent('CHF_USD', 10000, 'market', 'buy')
		filtered = rm.filter_order(order)
		self.assertNotEquals(filtered.units, 10000)
		self.assertEquals(filtered.units, 90)

		order = OrderEvent('EUR_SGD', 10000, 'market', 'buy')
		filtered = rm.filter_order(order)
		self.assertNotEquals(filtered.units, 10000)
		self.assertEquals(filtered.units, 100)

	def testHasAppendedPos_FilteredOrderSpecificLimitBreach_2Instruments(self):
		ccyLimits = {'CHF': 1234}
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimit=100, ccyLimits=ccyLimits)
		rm.append_position('CHF', 100)
		order = OrderEvent('CHF_USD', 10000, 'market', 'buy')
		filtered = rm.filter_order(order)
		self.assertEquals(filtered.units, 1134)
		rm.append_position(filtered.instrument, filtered.units)

		order = OrderEvent('EUR_SGD', 1000, 'market', 'buy')
		filtered = rm.filter_order(order)
		self.assertNotEquals(filtered.units, 1000)
		self.assertEquals(filtered.units, 100)

	def testHasAppendedPos_FilteredOrderSpecificLimit_2InstrumentsBreahces(self):
		ccyLimits = {'CHF': 1234, 'EUR':10000}
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimit=100, ccyLimits=ccyLimits)
		rm.append_position('EUR', 100)
		filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'market', 'buy'))
		self.assertEquals(filtered.units, 1234)
		rm.append_position(filtered.instrument, filtered.units)

		filtered = rm.filter_order(OrderEvent('EUR_SGD', 5000, 'market', 'buy'))
		self.assertEquals(filtered.units, 5000)
		rm.append_position(filtered.instrument, filtered.units)

		filtered = rm.filter_order(OrderEvent('EUR_SGD', 50000, 'market', 'buy'))
		self.assertEquals(filtered.units, 4900)

	def testHas2AppendedPos_FilteredOrderSpecificLimit_2InstrumentsBreahces(self):
		ccyLimits = {'CHF': 1234, 'EUR':10000}
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimit=100, ccyLimits=ccyLimits)
		rm.append_position('CHF', 50)
		rm.append_position('EUR', 100)
		filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'market', 'buy'))
		self.assertEquals(filtered.units, 1184)
		rm.append_position(filtered.instrument, filtered.units)

		filtered = rm.filter_order(OrderEvent('EUR_SGD', 5000, 'market', 'buy'))
		self.assertEquals(filtered.units, 5000)
		rm.append_position(filtered.instrument, filtered.units)

		filtered = rm.filter_order(OrderEvent('EUR_SGD', 50000, 'market', 'buy'))
		self.assertEquals(filtered.units, 4900)

	#Short current positions
	def testHasAppendedShortPos_FilterOrderCcyExpLimitBreach(self):
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimit=100)
		rm.append_position('CHF', -10)
		order = OrderEvent('CHF_USD', 10000, 'market', 'buy')
		filtered = rm.filter_order(order)
		self.assertNotEquals(filtered.units, 10000)
		self.assertEquals(filtered.units, 110)

	def testHasAppendedShortPos_FilteredOrderSpecificLimitNoBreach(self):
		ccyLimits = {'CHF': 1234}
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimit=100, ccyLimits=ccyLimits)
		rm.append_position('CHF', -10)
		filtered = rm.filter_order(OrderEvent('CHF_USD', 1000, 'market', 'buy'))
		self.assertEquals(filtered.units, 1000)

	def testHasAppendedShortPos_FilteredOrderSpecificLimitBreach(self):
		ccyLimits = {'CHF': 1234}
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimit=100, ccyLimits=ccyLimits)
		rm.append_position('CHF', -100)
		filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'market', 'buy'))
		self.assertEquals(filtered.units, 1334)

	def testHasAppendedShortPos_FilteredOrderSpecificLimitLessThanDefault_Breach(self):
		ccyLimits = {'CHF': 100}
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimit=1000, ccyLimits=ccyLimits)
		rm.append_position('CHF', -10)
		filtered = rm.filter_order(OrderEvent('CHF_USD', 1000, 'market', 'buy'))
		self.assertEquals(filtered.units, 110)

	def testHasAppendedShortPos_FilterOrderCcyExpLimitBreach_2Instruments(self):
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimit=100)
		rm.append_position('CHF', -10)
		order = OrderEvent('CHF_USD', 10000, 'market', 'buy')
		filtered = rm.filter_order(order)
		self.assertNotEquals(filtered.units, 10000)
		self.assertEquals(filtered.units, 110)

		order = OrderEvent('EUR_SGD', 10000, 'market', 'buy')
		filtered = rm.filter_order(order)
		self.assertNotEquals(filtered.units, 10000)
		self.assertEquals(filtered.units, 100)

	def testHasAppendedShortPos_FilteredOrderSpecificLimitBreach_2Instruments(self):
		ccyLimits = {'CHF': 1234}
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimit=100, ccyLimits=ccyLimits)
		rm.append_position('CHF', -100)
		order = OrderEvent('CHF_USD', 10000, 'market', 'buy')
		filtered = rm.filter_order(order)
		self.assertEquals(filtered.units, 1334)

		order = OrderEvent('EUR_SGD', 1000, 'market', 'buy')
		filtered = rm.filter_order(order)
		self.assertNotEquals(filtered.units, 1000)
		self.assertEquals(filtered.units, 100)

	def testHasAppendedShortPos_FilteredOrderSpecificLimit_2InstrumentsBreahces(self):
		ccyLimits = {'CHF': 1234, 'EUR':10000}
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimit=100, ccyLimits=ccyLimits)
		rm.append_position('EUR', -100)
		filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'market', 'buy'))
		self.assertEquals(filtered.units, 1234)

		filtered = rm.filter_order(OrderEvent('EUR_SGD', 5000, 'market', 'buy'))
		self.assertEquals(filtered.units, 5000)
		rm.append_position(filtered.instrument, filtered.units)

		filtered = rm.filter_order(OrderEvent('EUR_SGD', 50000, 'market', 'buy'))
		self.assertEquals(filtered.units, 5100)

	def testHasAppended2ShortPos_FilteredOrderSpecificLimit_2InstrumentsBreahces(self):
		ccyLimits = {'CHF': 1234, 'EUR':10000}
		rm = CcyExposureLimitRiskEvaluator('ABC', ccyLimit=100, ccyLimits=ccyLimits)
		rm.append_position('CHF', -50)
		rm.append_position('EUR', -100)
		filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'market', 'buy'))
		self.assertEquals(filtered.units, 1284)
		rm.append_position(filtered.instrument, filtered.units)

		filtered = rm.filter_order(OrderEvent('EUR_SGD', 5000, 'market', 'buy'))
		self.assertEquals(filtered.units, 5000)
		rm.append_position(filtered.instrument, filtered.units)

		filtered = rm.filter_order(OrderEvent('EUR_SGD', 50000, 'market', 'buy'))
		self.assertEquals(filtered.units, 5100)

	def testCanSetPerCcyExpLimit(self):
		rm = CcyExposureLimitRiskEvaluator('BC')
		rm.set_limit('SHF_USD', ccyLimit=10000)
		self.assertEquals(rm.ccyLimits['SHF_USD'], 10000)

	def testCanSetPerPositionShortLimit(self):
		rm = CcyExposureLimitRiskEvaluator('BC')
		rm.set_limit('SHF_USD', ccyLimitShort=-22)
		self.assertEquals(rm.ccyLimitsShort['SHF_USD'], -22)

	def testCanSetPerPositionLongShortLimit(self):
		rm = CcyExposureLimitRiskEvaluator('BC')
		rm.set_limit('SHF_USD', ccyLimit=10000, ccyLimitShort=-22)
		self.assertEquals(rm.ccyLimits['SHF_USD'], 10000)
		self.assertEquals(rm.ccyLimitsShort['SHF_USD'], -22)

	def testCanSetPerCcyExpLimitAndUnsetShort(self):
		rm = CcyExposureLimitRiskEvaluator('BC')
		rm.set_limit('SHF_USD', ccyLimitShort=-22)
		self.assertEquals(rm.ccyLimitsShort['SHF_USD'], -22)
		rm.set_limit('SHF_USD', ccyLimit=10000)
		self.assertEquals(rm.ccyLimits['SHF_USD'], 10000)
		self.assertFalse('SHF_USD' in rm.ccyLimitsShort)

	def testCanSetPerPositionShortLimitAndUnsetLong(self):
		rm = CcyExposureLimitRiskEvaluator('BC')
		rm.set_limit('SHF_USD', ccyLimit=10000)
		self.assertEquals(rm.ccyLimits['SHF_USD'], 10000)
		rm.set_limit('SHF_USD', ccyLimitShort=-22)
		self.assertEquals(rm.ccyLimitsShort['SHF_USD'], -22)
		self.assertFalse('SHF_USD' in rm.ccyLimits)

	def testCanUnSetPerPositionShortLimit(self):
		rm = CcyExposureLimitRiskEvaluator('BC')
		rm.set_limit('SHF_USD', ccyLimit=10000 , ccyLimitShort=-22)
		self.assertEquals(rm.ccyLimits['SHF_USD'], 10000)
		self.assertEquals(rm.ccyLimitsShort['SHF_USD'], -22)
		rm.set_limit('SHF_USD')
		self.assertFalse('SHF_USD' in rm.ccyLimits)
		self.assertFalse('SHF_USD' in rm.ccyLimitsShort)
	def testCannotFilterOrderWithStaleRates(self):
		rm = CcyExposureLimitRiskEvaluator('ABC')
		try:
			filtered = rm.filter_order(OrderEvent('CHF_USD', 1000, 'market', 'buy'))
			self.fail('Filtered order without current fx rates')
		except AssertionError:
			pass
	"""

