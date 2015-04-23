import sys

sys.path.append('../../main')
import unittest

from com.open.algo.risk.ccyExposureLimitRisk import CcyExposureLimitRiskEvaluator
from com.open.algo.trading.fxEvents import OrderEvent


class TestRiskManager(unittest.TestCase):
    def assign_dummy_rates(self, rm):
        rm.rates['CHF'] = {}
        rm.rates['CHF']['bid'] = 1.04
        rm.rates['CHF']['ask'] = 1.05
        rm.rates['EUR'] = {}
        rm.rates['EUR']['bid'] = 1.08
        rm.rates['EUR']['ask'] = 1.09
        rm.rates['SGD'] = {}
        rm.rates['SGD']['bid'] = 0.74
        rm.rates['SGD']['ask'] = 0.75

    def assign_unity_rates(self, rm):
        rm.rates['CHF'] = {}
        rm.rates['CHF']['bid'] = 1.0
        rm.rates['CHF']['ask'] = 1.0
        rm.rates['EUR'] = {}
        rm.rates['EUR']['bid'] = 1.0
        rm.rates['EUR']['ask'] = 1.0
        rm.rates['SGD'] = {}
        rm.rates['SGD']['bid'] = 1.0
        rm.rates['SGD']['ask'] = 1.0

    def setUp(self):
        self.rm = CcyExposureLimitRiskEvaluator('USD', ccy_limit_short=-100000)
        self.assign_dummy_rates(self.rm)

    def test_currency_exposure_manager_exists(self):
        self.assertIsNotNone(CcyExposureLimitRiskEvaluator('BC'))

    def test_should_have_base_currency(self):
        self.assertIsNotNone(CcyExposureLimitRiskEvaluator('BC').base_ccy)
        self.assertEquals(CcyExposureLimitRiskEvaluator('BC').base_ccy, 'BC')

    def test_should_have_positions(self):
        self.assertIsNotNone(CcyExposureLimitRiskEvaluator('BC').positions)

    def test_should_have_currency_exposure_limit(self):
        self.assertIsNotNone(CcyExposureLimitRiskEvaluator('BC').ccy_limit)

    def test_should_have_portfolio_limit(self):
        self.assertIsNotNone(CcyExposureLimitRiskEvaluator('BC').port_limit)

    def test_should_have_default_ccy_exposure_limit(self):
        rm = CcyExposureLimitRiskEvaluator('BC')
        self.assertTrue(rm.ccy_limit > 0)

    def test_should_have_preset_ccy_exposure_limit(self):
        rm = CcyExposureLimitRiskEvaluator('BC', ccy_limit=123)
        self.assertEquals(rm.ccy_limit, 123)

    def test_should_have_default_portfolio_limit(self):
        rm = CcyExposureLimitRiskEvaluator('BC')
        self.assertTrue(rm.port_limit > 0)

    def test_should_have_preset_portfolio_limit(self):
        rm = CcyExposureLimitRiskEvaluator('BC', port_limit=1230)
        self.assertEquals(rm.port_limit, 1230)

    def test_should_have_specific_ccy_exposure_limits(self):
        self.assertIsNotNone(CcyExposureLimitRiskEvaluator('BC').ccy_limits)

    def test_should_init_with_specific_ccy_exposure_limits(self):
        self.assertEquals(CcyExposureLimitRiskEvaluator('BC', ccy_limits={}).ccy_limits, {})

    def test_should_init_with_specific_ccy_exposure_limit_for_CHF(self):
        ccy_limits = {'CHF': 100.1}
        rm = CcyExposureLimitRiskEvaluator('BC', ccy_limits=ccy_limits)
        self.assertEquals(rm.ccy_limits['CHF'], 100.1)

    def test_should_not_filter_order_without_rates(self):
        rmo = CcyExposureLimitRiskEvaluator('ABC')
        try:
            rmo.filter_order(OrderEvent('CHF_USD', 1000, 'buy'))
            self.fail('Filtered order without fx rates')
        except AssertionError:
            pass

    def test_should_filter_order(self):
        filtered = self.rm.filter_order(OrderEvent('CHF_USD', 1000, 'buy'))
        self.assertNotEqual(None, filtered, 'Could not filter trade')

    def test_filtered_order_should_have_expected_instrument(self):
        filtered = self.rm.filter_order(OrderEvent('CHF_USD', 100, 'buy'))
        self.assertEquals(filtered.instrument, 'CHF_USD')

    def test_filtered_buy_order_should_have_expected_side(self):
        filtered = self.rm.filter_order(OrderEvent('CHF_USD', 100, 'buy'))
        self.assertEquals(filtered.side, 'buy')

    def test_filtered_sell_order_should_have_expected_side(self):
        filtered = self.rm.filter_order(OrderEvent('CHF_USD', 100, 'sell'))
        self.assertEquals(filtered.side, 'sell')

    def test_filtered_order_should_have_expected_type(self):
        order = OrderEvent('CHF_USD', 100, 'buy')
        filtered = self.rm.filter_order(order)
        self.assertEquals(order.order_type, filtered.order_type)

    def test_filtered_order_should_have_same_units_when_order_size_does_not_breach_default_limit_on_1st_ccy(self):
        order = OrderEvent('CHF_USD', 100, 'buy')
        filtered = self.rm.filter_order(order)
        self.assertEquals(filtered.units, 100)

    def test_filtered_order_should_have_same_units_when_order_size_does_not_breach_non_default_limit_on_1st_ccy(self):
        rm = CcyExposureLimitRiskEvaluator('USD', ccy_limit=150)
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 140, 'buy')
        filtered = self.rm.filter_order(order)
        self.assertEquals(filtered.units, 140)

    def test_filtered_order_should_have_less_units_when_order_size_breaches_default_limit_on_1st_ccy(self):
        order = OrderEvent('EUR_SGD', 10000, 'buy')
        filtered = self.rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        amount_in_base_ccy = round(self.rm.ccy_limit / self.rm.rates['EUR']['ask'], 0)
        self.assertEquals(amount_in_base_ccy, filtered.units)

    def test_filtered_order_should_have_less_units_when_order_size_breaches_non_default_limit_on_1st_ccy(self):
        ccy_limits = {'CHF': 1234}
        rm = CcyExposureLimitRiskEvaluator('USD', ccy_limit=100, ccy_limits=ccy_limits)
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 1000, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 1000)

    def test_filtered_order_should_have_less_units_when_order_size_breaches_specific_limit_on_1st_ccy(self):
        ccy_limits = {'CHF': 1234}
        rm = CcyExposureLimitRiskEvaluator('USD', ccy_limit=100, ccy_limits=ccy_limits)
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        amount_in_base_ccy = round(rm.ccy_limits['CHF'] / self.rm.rates['CHF']['ask'], 0)
        filtered = rm.filter_order(order)
        self.assertEquals(amount_in_base_ccy, filtered.units)

    def test_filtered_sell_order_should_have_same_units_when_order_size_does_not_breach_default_short_limit_on_1st_ccy(self):
        order = OrderEvent('CHF_USD', 100, 'sell')
        filtered = self.rm.filter_order(order)
        self.assertEqual(100, filtered.units)

    def test_filtered_order_should_have_less_units_when_order_size_breaches_specific_limit_on_1st_ccy(self):
        ccy_limits_short = {'CHF': -234}
        rm = CcyExposureLimitRiskEvaluator('USD', ccy_limit=100, ccy_limits_short=ccy_limits_short)
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 100, 'sell')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 100)

    def test_filtered_sell_order_should_have_same_units_when_order_size_does_not_breach_non_default_short_limit_on_1st_ccy(self):
        rm = CcyExposureLimitRiskEvaluator('USD', ccy_limit_short=-10)
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 10, 'sell')
        filtered = self.rm.filter_order(order)
        self.assertEquals(filtered.units, 10)

    def test_filtered_sell_order_should_have_less_units_when_order_size_breaches_default_short_limit_on_1st_ccy(self):
        order = OrderEvent('EUR_SGD', 10000, 'sell')
        filtered = self.rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        amount_in_base_ccy = round(self.rm.ccy_limit / self.rm.rates['SGD']['ask'], 0)
        self.assertEquals(amount_in_base_ccy, filtered.units)

    def test_filtered_order_should_have_less_units_when_order_size_breaches_specific_limit_less_than_default_on_1st_ccy(self):
        ccy_limits = {'CHF': 100}
        rm = CcyExposureLimitRiskEvaluator('USD', ccy_limit=1000, ccy_limits=ccy_limits)
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 1000, 'buy')
        amount_in_base_ccy = round(rm.ccy_limits['CHF'] / self.rm.rates['CHF']['ask'], 0)
        filtered = rm.filter_order(order)
        self.assertEquals(amount_in_base_ccy, filtered.units)

    def test_filtered_order_should_have_less_units_when_order_size_does_not_breach_specific_limit_more_than_default_on_1st_ccy_with_fx_rate_gt_1(self):
        ccy_limits = {'CHF': 10000}
        rm = CcyExposureLimitRiskEvaluator('USD', ccy_limit=1000, ccy_limits=ccy_limits, ccy_limit_short=-10000)
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        amount_in_base_ccy = round(rm.ccy_limits['CHF'] / rm.rates['CHF']['ask'], 0)
        self.assertEquals(amount_in_base_ccy, filtered.units)

    def test_filtered_sell_order_should_have_less_units_when_order_size_breaches_short_specific_limit_less_than_default_short_limit_on_1st_ccy(self):
        ccy_limits_short = {'CHF': -100}
        rm = CcyExposureLimitRiskEvaluator('USD', ccy_limit_short=-1000, ccy_limits_short=ccy_limits_short)
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 1000, 'sell')
        amount_in_base_ccy = round(-1 * rm.ccy_limits_short['CHF'] / self.rm.rates['CHF']['bid'], 0)
        filtered = rm.filter_order(order)
        self.assertEquals(amount_in_base_ccy, filtered.units)
        self.assertEquals(filtered.instrument, 'CHF_USD')
        self.assertEquals(filtered.side, 'sell')

    def test_filtered_sell_order_should_have_same_units_when_order_size_breaches_short_specific_limit_more_than_default_short_limit_on_1st_ccy(self):
        ccy_limits_short = {'CHF': -10000}
        rm = CcyExposureLimitRiskEvaluator('USD', ccy_limit_short=-1000, ccy_limits_short=ccy_limits_short, ccy_limit=100000)
        self.assign_unity_rates(rm)
        order = OrderEvent('CHF_USD', 10000, 'sell')
        filtered = rm.filter_order(order)
        self.assertEquals(10000, filtered.units)
        self.assertEquals(filtered.instrument, 'CHF_USD')
        self.assertEquals(filtered.side, 'sell')

    def test_should_allow_to_set_ccy_limit_and_have_expected_value(self):
        rm = CcyExposureLimitRiskEvaluator('BC', ccy_limits={})
        rm.set_limit('CHF', 1234.5)
        self.assertEquals(rm.ccy_limits['CHF'], 1234.5)

    def test_filtered_order_should_have_less_units_when_order_size_breaches_both_specific_and_default_limit_on_1st_ccy(self):
        ccy_limits = {'CHF': 12000}
        rm = CcyExposureLimitRiskEvaluator('SGD', ccy_limit=10000, ccy_limits=ccy_limits, ccy_limit_short=-100000)
        self.assign_unity_rates(rm)
        order = OrderEvent('CHF_SGD', 15000, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 12000)

    def test_should_allow_to_set_unity_fx_rate_and_have_same_units(self):
        ccy_limits = {'CHF': 110}
        rm = CcyExposureLimitRiskEvaluator('SGD', ccy_limit=10000, ccy_limits=ccy_limits)
        rm.fix_rate('CHF', 1.0, 1.0)
        order = OrderEvent('CHF_SGD', 105, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 105)

    def test_should_allow_to_set_unity_fx_rate_and_have_less_units_when_order_size_breaches_specific_limit_on_1st_ccy(self):
        ccy_limits = {'CHF': 110}
        rm = CcyExposureLimitRiskEvaluator('SGD', ccy_limit=10000, ccy_limits=ccy_limits)
        rm.fix_rate('CHF', 1.0, 1.0)
        order = OrderEvent('CHF_SGD', 150, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 110)

    """
    ***********************************************************************************************
    Tests for 2nd currency limit breaches
    ***********************************************************************************************
    """

    def test_filtered_order_should_have_same_units_when_order_size_does_not_breach_default_short_ccy_limit_on_2nd_ccy(self):
        rm = CcyExposureLimitRiskEvaluator('USD', ccy_limit_short=-150, ccy_limits={'CHF': 10000})
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 100, 'buy')
        filtered = self.rm.filter_order(order)
        self.assertEquals(filtered.units, 100)

    def test_filtered_order_should_have_same_units_when_order_size_does_not_breach_non_default_short_ccy_limit_on_2nd_ccy(self):
        rm = CcyExposureLimitRiskEvaluator('USD', ccy_limit_short=-150, ccy_limits={'CHF': 10000})
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 140, 'buy')
        filtered = self.rm.filter_order(order)
        self.assertEquals(filtered.units, 140)

    def test_filtered_order_should_have_less_units_when_order_size_breaches_non_default_short_ccy_limit_on_2nd_ccy(self):
        rm = CcyExposureLimitRiskEvaluator('USD', ccy_limit_short=-150, ccy_limits={'EUR': 10000})
        self.assign_unity_rates(rm)
        order = OrderEvent('EUR_SGD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(abs(rm.ccy_limit_short), filtered.units)

    def test_filtered_order_should_have_same_units_when_order_size_equals_non_default_short_ccy_limit_on_2nd_ccy(self):
        rm = CcyExposureLimitRiskEvaluator('USD', ccy_limits_short={'USD': -1000}, ccy_limits={'CHF': 1500})
        self.assign_unity_rates(rm)
        order = OrderEvent('CHF_USD', 1000, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 1000)

    def test_filtered_order_should_have_less_units_when_order_size_breaches_specific_short_ccy_limit_on_2nd_ccy(self):
        rm = CcyExposureLimitRiskEvaluator('USD', ccy_limits_short={'USD': -1000}, ccy_limits={'CHF': 15000})
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(1000, filtered.units)

    def test_filtered_sell_order_should_have_same_units_when_order_size_does_not_breach_default_limits_on_1st_and_2nd_currencies(self):
        order = OrderEvent('CHF_USD', 100, 'sell')
        filtered = self.rm.filter_order(order)
        self.assertEqual(100, filtered.units)

    def test_filtered_sell_order_should_have_same_units_when_order_size_does_not_breach_specific_short_limit_on_2nd_ccy_and_size_equals_default_limit_on_1sr_ccy(self):
        rm = CcyExposureLimitRiskEvaluator('USD', ccy_limit=100, ccy_limits_short={'CHF': -234})
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 100, 'sell')
        filtered = rm.filter_order(order)
        self.assertEquals(100, filtered.units)

    def test_filtered_order_should_have_less_units_when_order_size_breaches_specific_short_limit_on_2nd_ccy_with_fx_rate_greater_than_1(self):
        rm = CcyExposureLimitRiskEvaluator('USD', ccy_limits_short={'EUR': -100})
        self.assign_dummy_rates(rm)
        order = OrderEvent('SGD_EUR', 2000, 'buy')
        filtered = rm.filter_order(order)
        amount_in_base_ccy = round(-1 * rm.ccy_limits_short['EUR'] / self.rm.rates['EUR']['bid'], 0)
        self.assertEquals(amount_in_base_ccy, filtered.units)

    def test_filtered_sell_order_should_have_less_units_when_order_size_breaches_specific_short_limit_on_2nd_ccy_with_fx_rate_greater_than_1(self):
        rm = CcyExposureLimitRiskEvaluator('USD', ccy_limits_short={'EUR': -100})
        self.assign_dummy_rates(rm)
        order = OrderEvent('SGD_EUR', 5000, 'sell')
        filtered = rm.filter_order(order)
        amount_in_base_ccy = round(rm.ccy_limit / self.rm.rates['EUR']['ask'], 0)
        self.assertEquals(amount_in_base_ccy, filtered.units)

    """
    def testFilterOrderCcyExpLimitBreach_2Instruments(self):
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit=100)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 100)

        order = OrderEvent('EUR_SGD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 100)

    def testFilteredOrderSpecificLimitBreach_2Instruments(self):
        ccy_limits = {'CHF': 1234}
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit=100, ccy_limits=ccy_limits)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 1234)

        order = OrderEvent('EUR_SGD', 1000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 1000)
        self.assertEquals(filtered.units, 100)

    def testFilteredOrderSpecificLimit_2InstrumentsBreahces(self):
        ccy_limits = {'CHF': 1234, 'EUR':10000}
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit=100, ccy_limits=ccy_limits)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'buy'))
        self.assertEquals(filtered.units, 1234)

        filtered = rm.filter_order(OrderEvent('EUR_SGD', 5000, 'buy'))
        self.assertEquals(filtered.units, 5000)

        filtered = rm.filter_order(OrderEvent('EUR_SGD', 50000, 'buy'))
        self.assertEquals(filtered.units, 10000)

    def testFilterBasedOnCcyExposure(self):
        rm = CcyExposureLimitRiskEvaluator('ABC')
        self.assertNotEquals(rm.ccy_limit, None)

    def testHasDefaultCurrencyLimit(self):
        rm = CcyExposureLimitRiskEvaluator('BC')
        self.assertTrue(rm.ccy_limit > 0)

    def testFilterBasedOnCcyExposure(self):
        rm = CcyExposureLimitRiskEvaluator('ABC')
        rm.rates['CHF'] = {}
        rm.rates['CHF']['bid'] = 0.8123
        rm.rates['CHF']['ask'] = 0.8120
        self.assertEquals(rm.rates['CHF']['bid'], 0.8123)
        self.assertEquals(rm.rates['CHF']['ask'], 0.8120)

    #Short limits
    def testHasDefaultShortCcyExpLimit(self):
        rm = CcyExposureLimitRiskEvaluator('BC')
        self.assertTrue(rm.ccy_limit_short <= 0)

    def testHasPresetShortCcyExpLimit(self):
        rm = CcyExposureLimitRiskEvaluator('BC', ccy_limit=123, ccy_limit_short=-100)
        self.assertEquals(rm.ccy_limit_short, -100)

    def testWrongPresetShortCcyExpLimitRaisesError(self):
        try:
            rm = CcyExposureLimitRiskEvaluator('BC', ccy_limit_short=100)
            self.fail('Should have failed using +ve short position limit')
        except AssertionError:
            pass

    def testWrongPresetCcyExpLimitRaisesError(self):
        try:
            rm = CcyExposureLimitRiskEvaluator('BC', ccy_limit=-12)
            self.fail('Should have failed using -ve short position limit')
        except AssertionError:
            pass

    def testHasPerPositionShortLimit(self):
        self.assertNotEquals(CcyExposureLimitRiskEvaluator('BC').ccy_limits_short, None)

    def testCanInitWithPerPositionShortLimit(self):
        self.assertEquals(CcyExposureLimitRiskEvaluator('BC', ccy_limits_short={}).ccy_limits_short, {})

    def testCanInitWithPerPositionShortLimitCHF(self):
        ccy_limits_short = { 'CHF': -12.1}
        rm = CcyExposureLimitRiskEvaluator('BC', ccy_limits_short=ccy_limits_short)
        self.assertEquals(rm.ccy_limits_short['CHF_USD'], -12.1)

    def testFilterOrderDefaultShortCcyExpLimitBreach(self):
        rm = CcyExposureLimitRiskEvaluator('ABC')
        order = OrderEvent('CHF_USD', 10000, 'sell')
        print (order)
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 0)

    def testFilterOrderShortCcyExpLimitBreach(self):
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit_short=-100)
        order = OrderEvent('CHF_USD', 10000, 'sell')
        print (order)
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 100)

    def testFilteredOrderSpecificLimitNoBreachShort(self):
        ccy_limits_short = {'CHF': -234}
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit_short=-100, ccy_limits_short=ccy_limits_short)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 200, 'sell'))
        self.assertEquals(filtered.units, 200)

    def testFilteredOrderSpecificLimitBreachShort(self):
        ccy_limits_short = {'CHF': -234}
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit_short=-100, ccy_limits_short=ccy_limits_short)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'sell'))
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
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit=100)
        rm.append_position('CHF', 10)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 90)

    def testHasAppendedPos_FilteredOrderSpecificLimitNoBreach(self):
        ccy_limits = {'CHF': 1234}
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit=100, ccy_limits=ccy_limits)
        rm.append_position('CHF', 10)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 1000, 'buy'))
        self.assertEquals(filtered.units, 1000)

    def testHasAppendedPos_FilteredOrderSpecificLimitBreach(self):
        ccy_limits = {'CHF': 1234}
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit=100, ccy_limits=ccy_limits)
        rm.append_position('CHF', 100)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'buy'))
        self.assertEquals(filtered.units, 1134)

    def testHasAppendedPos_FilteredOrderSpecificLimitLessThanDefault_Breach(self):
        ccy_limits = {'CHF': 100}
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit=1000, ccy_limits=ccy_limits)
        rm.append_position('CHF', 10)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 1000, 'buy'))
        self.assertEquals(filtered.units, 90)

    def testHasAppendedPos_FilterOrderCcyExpLimitBreach_2Instruments(self):
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit=100)
        rm.append_position('CHF', 10)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 90)

        order = OrderEvent('EUR_SGD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 100)

    def testHasAppendedPos_FilteredOrderSpecificLimitBreach_2Instruments(self):
        ccy_limits = {'CHF': 1234}
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit=100, ccy_limits=ccy_limits)
        rm.append_position('CHF', 100)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 1134)
        rm.append_position(filtered.instrument, filtered.units)

        order = OrderEvent('EUR_SGD', 1000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 1000)
        self.assertEquals(filtered.units, 100)

    def testHasAppendedPos_FilteredOrderSpecificLimit_2InstrumentsBreahces(self):
        ccy_limits = {'CHF': 1234, 'EUR':10000}
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit=100, ccy_limits=ccy_limits)
        rm.append_position('EUR', 100)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'buy'))
        self.assertEquals(filtered.units, 1234)
        rm.append_position(filtered.instrument, filtered.units)

        filtered = rm.filter_order(OrderEvent('EUR_SGD', 5000, 'buy'))
        self.assertEquals(filtered.units, 5000)
        rm.append_position(filtered.instrument, filtered.units)

        filtered = rm.filter_order(OrderEvent('EUR_SGD', 50000, 'buy'))
        self.assertEquals(filtered.units, 4900)

    def testHas2AppendedPos_FilteredOrderSpecificLimit_2InstrumentsBreahces(self):
        ccy_limits = {'CHF': 1234, 'EUR':10000}
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit=100, ccy_limits=ccy_limits)
        rm.append_position('CHF', 50)
        rm.append_position('EUR', 100)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'buy'))
        self.assertEquals(filtered.units, 1184)
        rm.append_position(filtered.instrument, filtered.units)

        filtered = rm.filter_order(OrderEvent('EUR_SGD', 5000, 'buy'))
        self.assertEquals(filtered.units, 5000)
        rm.append_position(filtered.instrument, filtered.units)

        filtered = rm.filter_order(OrderEvent('EUR_SGD', 50000, 'buy'))
        self.assertEquals(filtered.units, 4900)

    #Short current positions
    def testHasAppendedShortPos_FilterOrderCcyExpLimitBreach(self):
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit=100)
        rm.append_position('CHF', -10)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 110)

    def testHasAppendedShortPos_FilteredOrderSpecificLimitNoBreach(self):
        ccy_limits = {'CHF': 1234}
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit=100, ccy_limits=ccy_limits)
        rm.append_position('CHF', -10)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 1000, 'buy'))
        self.assertEquals(filtered.units, 1000)

    def testHasAppendedShortPos_FilteredOrderSpecificLimitBreach(self):
        ccy_limits = {'CHF': 1234}
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit=100, ccy_limits=ccy_limits)
        rm.append_position('CHF', -100)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'buy'))
        self.assertEquals(filtered.units, 1334)

    def testHasAppendedShortPos_FilteredOrderSpecificLimitLessThanDefault_Breach(self):
        ccy_limits = {'CHF': 100}
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit=1000, ccy_limits=ccy_limits)
        rm.append_position('CHF', -10)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 1000, 'buy'))
        self.assertEquals(filtered.units, 110)

    def testHasAppendedShortPos_FilterOrderCcyExpLimitBreach_2Instruments(self):
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit=100)
        rm.append_position('CHF', -10)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 110)

        order = OrderEvent('EUR_SGD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 100)

    def testHasAppendedShortPos_FilteredOrderSpecificLimitBreach_2Instruments(self):
        ccy_limits = {'CHF': 1234}
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit=100, ccy_limits=ccy_limits)
        rm.append_position('CHF', -100)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 1334)

        order = OrderEvent('EUR_SGD', 1000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 1000)
        self.assertEquals(filtered.units, 100)

    def testHasAppendedShortPos_FilteredOrderSpecificLimit_2InstrumentsBreahces(self):
        ccy_limits = {'CHF': 1234, 'EUR':10000}
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit=100, ccy_limits=ccy_limits)
        rm.append_position('EUR', -100)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'buy'))
        self.assertEquals(filtered.units, 1234)

        filtered = rm.filter_order(OrderEvent('EUR_SGD', 5000, 'buy'))
        self.assertEquals(filtered.units, 5000)
        rm.append_position(filtered.instrument, filtered.units)

        filtered = rm.filter_order(OrderEvent('EUR_SGD', 50000, 'buy'))
        self.assertEquals(filtered.units, 5100)

    def testHasAppended2ShortPos_FilteredOrderSpecificLimit_2InstrumentsBreahces(self):
        ccy_limits = {'CHF': 1234, 'EUR':10000}
        rm = CcyExposureLimitRiskEvaluator('ABC', ccy_limit=100, ccy_limits=ccy_limits)
        rm.append_position('CHF', -50)
        rm.append_position('EUR', -100)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'buy'))
        self.assertEquals(filtered.units, 1284)
        rm.append_position(filtered.instrument, filtered.units)

        filtered = rm.filter_order(OrderEvent('EUR_SGD', 5000, 'buy'))
        self.assertEquals(filtered.units, 5000)
        rm.append_position(filtered.instrument, filtered.units)

        filtered = rm.filter_order(OrderEvent('EUR_SGD', 50000, 'buy'))
        self.assertEquals(filtered.units, 5100)

    def testCanSetPerCcyExpLimit(self):
        rm = CcyExposureLimitRiskEvaluator('BC')
        rm.set_limit('SHF_USD', ccy_limit=10000)
        self.assertEquals(rm.ccy_limits['SHF_USD'], 10000)

    def testCanSetPerPositionShortLimit(self):
        rm = CcyExposureLimitRiskEvaluator('BC')
        rm.set_limit('SHF_USD', ccy_limit_short=-22)
        self.assertEquals(rm.ccy_limits_short['SHF_USD'], -22)

    def testCanSetPerPositionLongShortLimit(self):
        rm = CcyExposureLimitRiskEvaluator('BC')
        rm.set_limit('SHF_USD', ccy_limit=10000, ccy_limit_short=-22)
        self.assertEquals(rm.ccy_limits['SHF_USD'], 10000)
        self.assertEquals(rm.ccy_limits_short['SHF_USD'], -22)

    def testCanSetPerCcyExpLimitAndUnsetShort(self):
        rm = CcyExposureLimitRiskEvaluator('BC')
        rm.set_limit('SHF_USD', ccy_limit_short=-22)
        self.assertEquals(rm.ccy_limits_short['SHF_USD'], -22)
        rm.set_limit('SHF_USD', ccy_limit=10000)
        self.assertEquals(rm.ccy_limits['SHF_USD'], 10000)
        self.assertFalse('SHF_USD' in rm.ccy_limits_short)

    def testCanSetPerPositionShortLimitAndUnsetLong(self):
        rm = CcyExposureLimitRiskEvaluator('BC')
        rm.set_limit('SHF_USD', ccy_limit=10000)
        self.assertEquals(rm.ccy_limits['SHF_USD'], 10000)
        rm.set_limit('SHF_USD', ccy_limit_short=-22)
        self.assertEquals(rm.ccy_limits_short['SHF_USD'], -22)
        self.assertFalse('SHF_USD' in rm.ccy_limits)

    def testCanUnSetPerPositionShortLimit(self):
        rm = CcyExposureLimitRiskEvaluator('BC')
        rm.set_limit('SHF_USD', ccy_limit=10000 , ccy_limit_short=-22)
        self.assertEquals(rm.ccy_limits['SHF_USD'], 10000)
        self.assertEquals(rm.ccy_limits_short['SHF_USD'], -22)
        rm.set_limit('SHF_USD')
        self.assertFalse('SHF_USD' in rm.ccy_limits)
        self.assertFalse('SHF_USD' in rm.ccy_limits_short)
    def testCannotFilterOrderWithStaleRates(self):
        rm = CcyExposureLimitRiskEvaluator('ABC')
        try:
            filtered = rm.filter_order(OrderEvent('CHF_USD', 1000, 'buy'))
            self.fail('Filtered order without current fx rates')
        except AssertionError:
            pass
    """