import sys

sys.path.append('../../main')
import unittest

from com.open.algo.risk.fxPositionLimitRisk import FxPositionLimitRiskEvaluator
from com.open.algo.trading.fxEvents import OrderEvent


class TestRiskManager(unittest.TestCase):
    def setUp(self):
        pass

    def testClassExists(self):
        self.assertNotEquals(FxPositionLimitRiskEvaluator(), None)

    def testHasPositions(self):
        self.assertNotEquals(FxPositionLimitRiskEvaluator().positions, None)

    def testHasPositionLimit(self):
        self.assertNotEquals(FxPositionLimitRiskEvaluator().posLimit, None)

    def testHasDefaultPositionLimit(self):
        rm = FxPositionLimitRiskEvaluator()
        self.assertTrue(rm.posLimit > 0)

    def testHasPresetPositionLimit(self):
        rm = FxPositionLimitRiskEvaluator(posLimit=123)
        self.assertEquals(rm.posLimit, 123)

    def testHasPerPositionLimit(self):
        self.assertNotEquals(FxPositionLimitRiskEvaluator().posLimits, None)

    def testCanInitWithPerPositionLimit(self):
        self.assertEquals(FxPositionLimitRiskEvaluator(posLimits={}).posLimits, {})

    def testCanInitWithPerPositionLimitCHF_USD(self):
        posLimits = {'CHF_USD': 100.1}
        rm = FxPositionLimitRiskEvaluator(posLimits=posLimits)
        self.assertEquals(rm.posLimits['CHF_USD'], 100.1)

    def testFilterOrder(self):
        rm = FxPositionLimitRiskEvaluator()
        filtered = rm.filter_order(OrderEvent('CHF_USD', 1000, 'buy'))

    def testFilterOrderHasCorrectInstrument(self):
        rm = FxPositionLimitRiskEvaluator(posLimit=100)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 100, 'buy'))
        self.assertEquals(filtered.instrument, 'CHF_USD')

    def testFilteredOrderHasCorrectSide(self):
        rm = FxPositionLimitRiskEvaluator(posLimit=100)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 100, 'buy'))
        self.assertEquals(filtered.side, 'buy')

    def testFilteredOrderHasCorrectSide2(self):
        rm = FxPositionLimitRiskEvaluator(posLimit=100)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 100, 'sell'))
        self.assertEquals(filtered.side, 'sell')

    def testFilteredOrderHasCorrectType(self):
        rm = FxPositionLimitRiskEvaluator(posLimit=100)
        order = OrderEvent('CHF_USD', 100, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(order.order_type, filtered.order_type)

    def testFilterOrderPositionLimitBreach(self):
        rm = FxPositionLimitRiskEvaluator(posLimit=100)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        print(order)
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 100)

    def testFilteredOrderSpecificLimitNoBreach(self):
        posLimits = {'CHF_USD': 1234}
        rm = FxPositionLimitRiskEvaluator(posLimit=100, posLimits=posLimits)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 1000, 'buy'))
        self.assertEquals(filtered.units, 1000)

    def testFilteredOrderSpecificLimitBreach(self):
        posLimits = {'CHF_USD': 1234}
        rm = FxPositionLimitRiskEvaluator(posLimit=100, posLimits=posLimits)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'buy'))
        self.assertEquals(filtered.units, 1234)

    def testFilteredOrderSpecificLimitLessThanDefault_Breach(self):
        posLimits = {'CHF_USD': 100}
        rm = FxPositionLimitRiskEvaluator(posLimit=1000, posLimits=posLimits)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 1000, 'buy'))
        self.assertEquals(filtered.units, 100)

    def testFilterOrderPositionLimitBreach_2Instruments(self):
        rm = FxPositionLimitRiskEvaluator(posLimit=100)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 100)

        order = OrderEvent('EUR_SGD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 100)

    def testFilteredOrderSpecificLimitBreach_2Instruments(self):
        posLimits = {'CHF_USD': 1234}
        rm = FxPositionLimitRiskEvaluator(posLimit=100, posLimits=posLimits)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 1234)

        order = OrderEvent('EUR_SGD', 1000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 1000)
        self.assertEquals(filtered.units, 100)

    def testFilteredOrderSpecificLimit_2InstrumentsBreahces(self):
        posLimits = {'CHF_USD': 1234, 'EUR_SGD': 10000}
        rm = FxPositionLimitRiskEvaluator(posLimit=100, posLimits=posLimits)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'buy'))
        self.assertEquals(filtered.units, 1234)

        filtered = rm.filter_order(OrderEvent('EUR_SGD', 5000, 'buy'))
        self.assertEquals(filtered.units, 5000)

        filtered = rm.filter_order(OrderEvent('EUR_SGD', 50000, 'buy'))
        self.assertEquals(filtered.units, 10000)

        # Short limits

    def testHasDefaultShortPositionLimit(self):
        rm = FxPositionLimitRiskEvaluator()
        self.assertTrue(rm.posLimitShort <= 0)

    def testHasPresetShortPositionLimit(self):
        rm = FxPositionLimitRiskEvaluator(posLimit=123, posLimitShort=-100)
        self.assertEquals(rm.posLimitShort, -100)

    def testWrongPresetShortPositionLimitRaisesError(self):
        try:
            rm = FxPositionLimitRiskEvaluator(posLimitShort=100)
            self.fail('Should have failed using +ve short position limit')
        except AssertionError:
            pass

    def testWrongPresetPositionLimitRaisesError(self):
        try:
            rm = FxPositionLimitRiskEvaluator(posLimit=-12)
            self.fail('Should have failed using -ve short position limit')
        except AssertionError:
            pass

    def testHasPerPositionShortLimit(self):
        self.assertNotEquals(FxPositionLimitRiskEvaluator().posLimitsShort, None)

    def testCanInitWithPerPositionShortLimit(self):
        self.assertEquals(FxPositionLimitRiskEvaluator(posLimitsShort={}).posLimitsShort, {})

    def testCanInitWithPerPositionShortLimitCHF_USD(self):
        posLimitsShort = {'CHF_USD': -12.1}
        rm = FxPositionLimitRiskEvaluator(posLimitsShort=posLimitsShort)
        self.assertEquals(rm.posLimitsShort['CHF_USD'], -12.1)

    def testFilterOrderDefaultShortPositionLimitBreach(self):
        rm = FxPositionLimitRiskEvaluator()
        order = OrderEvent('CHF_USD', 10000, 'sell')
        print(order)
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 0)

    def testFilterOrderShortPositionLimitBreach(self):
        rm = FxPositionLimitRiskEvaluator(posLimitShort=-100)
        order = OrderEvent('CHF_USD', 10000, 'sell')
        print(order)
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 100)

    def testFilteredOrderSpecificLimitNoBreachShort(self):
        posLimitsShort = {'CHF_USD': -234}
        rm = FxPositionLimitRiskEvaluator(posLimitShort=-100, posLimitsShort=posLimitsShort)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 200, 'sell'))
        self.assertEquals(filtered.units, 200)

    def testFilteredOrderSpecificLimitBreachShort(self):
        posLimitsShort = {'CHF_USD': -234}
        rm = FxPositionLimitRiskEvaluator(posLimitShort=-100, posLimitsShort=posLimitsShort)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'sell'))
        self.assertEquals(filtered.units, 234)


    #Current positions
    def testHasEmptyPositions(self):
        rm = FxPositionLimitRiskEvaluator()
        self.assertEquals(rm.positions, {})

    def testCanAppendPositions(self):
        rm = FxPositionLimitRiskEvaluator()
        rm.append_position('EUR_CHF', 123)

    def testHasAppendedPositions(self):
        rm = FxPositionLimitRiskEvaluator()
        rm.append_position('EUR_CHF', 123)
        self.assertEquals(rm.positions['EUR_CHF'], 123)

    def testCanAppendedSameIntrumentTwice(self):
        rm = FxPositionLimitRiskEvaluator()
        rm.append_position('EUR_CHF', 123)
        rm.append_position('EUR_CHF', 27)
        self.assertEquals(rm.positions['EUR_CHF'], 150)

    def testHas2AppendedPositions(self):
        rm = FxPositionLimitRiskEvaluator()
        rm.append_position('EUR_CHF', 123)
        rm.append_position('EUR_USD', 1000)
        self.assertEquals(rm.positions['EUR_CHF'], 123)
        self.assertEquals(rm.positions['EUR_USD'], 1000)

    def testHasAppendedPos_FilterOrderPositionLimitBreach(self):
        rm = FxPositionLimitRiskEvaluator(posLimit=100)
        rm.append_position('CHF_USD', 10)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 90)

    def testHasAppendedPos_FilteredOrderSpecificLimitNoBreach(self):
        posLimits = {'CHF_USD': 1234}
        rm = FxPositionLimitRiskEvaluator(posLimit=100, posLimits=posLimits)
        rm.append_position('CHF_USD', 10)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 1000, 'buy'))
        self.assertEquals(filtered.units, 1000)

    def testHasAppendedPos_FilteredOrderSpecificLimitBreach(self):
        posLimits = {'CHF_USD': 1234}
        rm = FxPositionLimitRiskEvaluator(posLimit=100, posLimits=posLimits)
        rm.append_position('CHF_USD', 100)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'buy'))
        self.assertEquals(filtered.units, 1134)

    def testHasAppendedPos_FilteredOrderSpecificLimitLessThanDefault_Breach(self):
        posLimits = {'CHF_USD': 100}
        rm = FxPositionLimitRiskEvaluator(posLimit=1000, posLimits=posLimits)
        rm.append_position('CHF_USD', 10)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 1000, 'buy'))
        self.assertEquals(filtered.units, 90)

    def testHasAppendedPos_FilterOrderPositionLimitBreach_2Instruments(self):
        rm = FxPositionLimitRiskEvaluator(posLimit=100)
        rm.append_position('CHF_USD', 10)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 90)

        order = OrderEvent('EUR_SGD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 100)

    def testHasAppendedPos_FilteredOrderSpecificLimitBreach_2Instruments(self):
        posLimits = {'CHF_USD': 1234}
        rm = FxPositionLimitRiskEvaluator(posLimit=100, posLimits=posLimits)
        rm.append_position('CHF_USD', 100)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 1134)
        rm.append_position(filtered.instrument, filtered.units)

        order = OrderEvent('EUR_SGD', 1000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 1000)
        self.assertEquals(filtered.units, 100)

    def testHasAppendedPos_FilteredOrderSpecificLimit_2InstrumentsBreahces(self):
        posLimits = {'CHF_USD': 1234, 'EUR_SGD': 10000}
        rm = FxPositionLimitRiskEvaluator(posLimit=100, posLimits=posLimits)
        rm.append_position('EUR_SGD', 100)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'buy'))
        self.assertEquals(filtered.units, 1234)
        rm.append_position(filtered.instrument, filtered.units)

        filtered = rm.filter_order(OrderEvent('EUR_SGD', 5000, 'buy'))
        self.assertEquals(filtered.units, 5000)
        rm.append_position(filtered.instrument, filtered.units)

        filtered = rm.filter_order(OrderEvent('EUR_SGD', 50000, 'buy'))
        self.assertEquals(filtered.units, 4900)

    def testHas2AppendedPos_FilteredOrderSpecificLimit_2InstrumentsBreahces(self):
        posLimits = {'CHF_USD': 1234, 'EUR_SGD': 10000}
        rm = FxPositionLimitRiskEvaluator(posLimit=100, posLimits=posLimits)
        rm.append_position('CHF_USD', 50)
        rm.append_position('EUR_SGD', 100)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'buy'))
        self.assertEquals(filtered.units, 1184)
        rm.append_position(filtered.instrument, filtered.units)

        filtered = rm.filter_order(OrderEvent('EUR_SGD', 5000, 'buy'))
        self.assertEquals(filtered.units, 5000)
        rm.append_position(filtered.instrument, filtered.units)

        filtered = rm.filter_order(OrderEvent('EUR_SGD', 50000, 'buy'))
        self.assertEquals(filtered.units, 4900)

    #Short current positions
    def testHasAppendedShortPos_FilterOrderPositionLimitBreach(self):
        rm = FxPositionLimitRiskEvaluator(posLimit=100)
        rm.append_position('CHF_USD', -10)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 110)

    def testHasAppendedShortPos_FilteredOrderSpecificLimitNoBreach(self):
        posLimits = {'CHF_USD': 1234}
        rm = FxPositionLimitRiskEvaluator(posLimit=100, posLimits=posLimits)
        rm.append_position('CHF_USD', -10)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 1000, 'buy'))
        self.assertEquals(filtered.units, 1000)

    def testHasAppendedShortPos_FilteredOrderSpecificLimitBreach(self):
        posLimits = {'CHF_USD': 1234}
        rm = FxPositionLimitRiskEvaluator(posLimit=100, posLimits=posLimits)
        rm.append_position('CHF_USD', -100)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'buy'))
        self.assertEquals(filtered.units, 1334)

    def testHasAppendedShortPos_FilteredOrderSpecificLimitLessThanDefault_Breach(self):
        posLimits = {'CHF_USD': 100}
        rm = FxPositionLimitRiskEvaluator(posLimit=1000, posLimits=posLimits)
        rm.append_position('CHF_USD', -10)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 1000, 'buy'))
        self.assertEquals(filtered.units, 110)

    def testHasAppendedShortPos_FilterOrderPositionLimitBreach_2Instruments(self):
        rm = FxPositionLimitRiskEvaluator(posLimit=100)
        rm.append_position('CHF_USD', -10)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 110)

        order = OrderEvent('EUR_SGD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 100)

    def testHasAppendedShortPos_FilteredOrderSpecificLimitBreach_2Instruments(self):
        posLimits = {'CHF_USD': 1234}
        rm = FxPositionLimitRiskEvaluator(posLimit=100, posLimits=posLimits)
        rm.append_position('CHF_USD', -100)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 1334)

        order = OrderEvent('EUR_SGD', 1000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 1000)
        self.assertEquals(filtered.units, 100)

    def testHasAppendedShortPos_FilteredOrderSpecificLimit_2InstrumentsBreahces(self):
        posLimits = {'CHF_USD': 1234, 'EUR_SGD': 10000}
        rm = FxPositionLimitRiskEvaluator(posLimit=100, posLimits=posLimits)
        rm.append_position('EUR_SGD', -100)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'buy'))
        self.assertEquals(filtered.units, 1234)

        filtered = rm.filter_order(OrderEvent('EUR_SGD', 5000, 'buy'))
        self.assertEquals(filtered.units, 5000)
        rm.append_position(filtered.instrument, filtered.units)

        filtered = rm.filter_order(OrderEvent('EUR_SGD', 50000, 'buy'))
        self.assertEquals(filtered.units, 5100)

    def testHasAppended2ShortPos_FilteredOrderSpecificLimit_2InstrumentsBreahces(self):
        posLimits = {'CHF_USD': 1234, 'EUR_SGD': 10000}
        rm = FxPositionLimitRiskEvaluator(posLimit=100, posLimits=posLimits)
        rm.append_position('CHF_USD', -50)
        rm.append_position('EUR_SGD', -100)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'buy'))
        self.assertEquals(filtered.units, 1284)
        rm.append_position(filtered.instrument, filtered.units)

        filtered = rm.filter_order(OrderEvent('EUR_SGD', 5000, 'buy'))
        self.assertEquals(filtered.units, 5000)
        rm.append_position(filtered.instrument, filtered.units)

        filtered = rm.filter_order(OrderEvent('EUR_SGD', 50000, 'buy'))
        self.assertEquals(filtered.units, 5100)

    def testCanSetPerPositionLimit(self):
        rm = FxPositionLimitRiskEvaluator()
        rm.set_limit('SHF_USD', posLimit=10000)
        self.assertEquals(rm.posLimits['SHF_USD'], 10000)

    def testCanSetPerPositionShortLimit(self):
        rm = FxPositionLimitRiskEvaluator()
        rm.set_limit('SHF_USD', posLimitShort=-22)
        self.assertEquals(rm.posLimitsShort['SHF_USD'], -22)

    def testCanSetPerPositionLongShortLimit(self):
        rm = FxPositionLimitRiskEvaluator()
        rm.set_limit('SHF_USD', posLimit=10000, posLimitShort=-22)
        self.assertEquals(rm.posLimits['SHF_USD'], 10000)
        self.assertEquals(rm.posLimitsShort['SHF_USD'], -22)

    def testCanSetPerPositionLimitAndUnsetShort(self):
        rm = FxPositionLimitRiskEvaluator()
        rm.set_limit('SHF_USD', posLimitShort=-22)
        self.assertEquals(rm.posLimitsShort['SHF_USD'], -22)
        rm.set_limit('SHF_USD', posLimit=10000)
        self.assertEquals(rm.posLimits['SHF_USD'], 10000)
        self.assertFalse('SHF_USD' in rm.posLimitsShort)

    def testCanSetPerPositionShortLimitAndUnsetLong(self):
        rm = FxPositionLimitRiskEvaluator()
        rm.set_limit('SHF_USD', posLimit=10000)
        self.assertEquals(rm.posLimits['SHF_USD'], 10000)
        rm.set_limit('SHF_USD', posLimitShort=-22)
        self.assertEquals(rm.posLimitsShort['SHF_USD'], -22)
        self.assertFalse('SHF_USD' in rm.posLimits)

    def testCanUnSetPerPositionShortLimit(self):
        rm = FxPositionLimitRiskEvaluator()
        rm.set_limit('SHF_USD', posLimit=10000, posLimitShort=-22)
        self.assertEquals(rm.posLimits['SHF_USD'], 10000)
        self.assertEquals(rm.posLimitsShort['SHF_USD'], -22)
        rm.set_limit('SHF_USD')
        self.assertFalse('SHF_USD' in rm.posLimits)
        self.assertFalse('SHF_USD' in rm.posLimitsShort)

