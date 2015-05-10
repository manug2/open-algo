import sys

sys.path.append('../../main')
import unittest
from com.open.algo.risk.ccyExposureLimitRisk import CcyExposureLimitRiskEvaluator
from com.open.algo.trading.fxEvents import TickEvent, OrderEvent
from com.open.algo.trading.fxPricesCache import FxPricesCache
from com.open.algo.utils import get_time


class TestRiskManager(unittest.TestCase):
    def assign_dummy_rates(self, rm):
        now = get_time()
        rm.rates_cache.set_rate(TickEvent('CHF_USD', now, 1.04, 1.05))
        rm.rates_cache.set_rate(TickEvent('EUR_USD', now, 1.08, 1.09))
        rm.rates_cache.set_rate(TickEvent('SGD_USD', now, 0.74, 0.75))
        rm.rates_cache.set_rate(TickEvent('CHF_SGD', now, 1.04, 1.05))

    def assign_unity_rates(self, rm):
        now = get_time()
        rm.rates_cache.set_rate(TickEvent('CHF_USD', now, 1.0, 1.0))
        rm.rates_cache.set_rate(TickEvent('EUR_USD', now, 1.0, 1.0))
        rm.rates_cache.set_rate(TickEvent('SGD_USD', now, 1.0, 1.0))
        rm.rates_cache.set_rate(TickEvent('CHF_SGD', now, 1.0, 1.0))

    def setUp(self):
        self.cache = FxPricesCache()
        self.rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit_short=-100000)
        self.assign_dummy_rates(self.rm)

    def test_currency_exposure_manager_exists(self):
        self.assertIsNotNone(CcyExposureLimitRiskEvaluator('BC', self.cache))

    def test_should_have_base_currency(self):
        self.assertIsNotNone(CcyExposureLimitRiskEvaluator('BC', self.cache).base_ccy)
        self.assertEquals(CcyExposureLimitRiskEvaluator('BC', self.cache).base_ccy, 'BC')

    def test_should_have_currency_exposure_limit(self):
        self.assertIsNotNone(CcyExposureLimitRiskEvaluator('BC', self.cache).ccy_limit)

    def test_should_have_default_ccy_exposure_limit(self):
        rm = CcyExposureLimitRiskEvaluator('BC', self.cache)
        self.assertTrue(rm.ccy_limit > 0)

    def test_should_have_preset_ccy_exposure_limit(self):
        rm = CcyExposureLimitRiskEvaluator('BC', FxPricesCache(), ccy_limit=123)
        self.assertEquals(rm.ccy_limit, 123)

    def test_should_not_allow_negative_preset_ccy_exposure_limit(self):
        try:
            CcyExposureLimitRiskEvaluator('BC', self.cache, ccy_limit=-123)
        except AssertionError:
            pass

    def test_should_have_specific_ccy_exposure_limits(self):
        self.assertIsNotNone(CcyExposureLimitRiskEvaluator('BC', self.cache).ccy_limits)

    def test_should_init_with_specific_ccy_exposure_limits(self):
        self.assertEquals(CcyExposureLimitRiskEvaluator('BC', self.cache, ccy_limits={}).ccy_limits, {})

    def test_should_init_with_specific_ccy_exposure_limit_for_CHF(self):
        ccy_limits = {'CHF': 100.1}
        rm = CcyExposureLimitRiskEvaluator('BC', self.cache, ccy_limits=ccy_limits)
        self.assertEquals(rm.ccy_limits['CHF'], 100.1)

    def test_should_not_filter_order_without_rates(self):
        rmo = CcyExposureLimitRiskEvaluator('ABC', FxPricesCache())
        try:
            rmo.filter_order(OrderEvent('CHF_USD', 1000, 'buy'))
            self.fail('Filtered order without fx rates')
        except AssertionError:
            pass

    def test_should_filter_order(self):
        filtered = self.rm.filter_order(OrderEvent('CHF_USD', 1000, 'buy'))
        self.assertIsNotNone(filtered, 'Could not filter trade')

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
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit=150)
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 140, 'buy')
        filtered = self.rm.filter_order(order)
        self.assertEquals(filtered.units, 140)

    def test_filtered_order_should_have_less_units_when_order_size_breaches_default_limit_on_1st_ccy(self):
        order = OrderEvent('EUR_SGD', 10000, 'buy')
        filtered = self.rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        amount_in_base_ccy = round(self.rm.ccy_limit / self.rm.rates_cache.get_rate('EUR_USD')['ask'], 0)
        self.assertEquals(amount_in_base_ccy, filtered.units)

    def test_filtered_order_should_have_less_units_when_order_size_breaches_non_default_limit_on_1st_ccy(self):
        ccy_limits = {'CHF': 1234}
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit=100, ccy_limits=ccy_limits)
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 1000, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 1000)

    def test_filtered_order_should_have_less_units_when_order_size_breaches_specific_limit_on_1st_ccy(self):
        ccy_limits = {'CHF': 1234}
        rm = CcyExposureLimitRiskEvaluator('USD', ccy_limit=100, ccy_limits=ccy_limits)
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        amount_in_base_ccy = round(rm.ccy_limits['CHF'] / self.rm.rates.get_rate('CHF_USD')['ask'], 0)
        filtered = rm.filter_order(order)
        self.assertEquals(amount_in_base_ccy, filtered.units)

    def test_filtered_sell_order_should_have_same_units_when_order_size_does_not_breach_default_short_limit_on_1st_ccy(self):
        order = OrderEvent('CHF_USD', 100, 'sell')
        filtered = self.rm.filter_order(order)
        self.assertEqual(100, filtered.units)

    def test_filtered_order_should_have_less_units_when_order_size_breaches_specific_limit_on_1st_ccy(self):
        ccy_limits_short = {'CHF': -234}
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit=100, ccy_limits_short=ccy_limits_short)
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 100, 'sell')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 100)

    def test_filtered_sell_order_should_have_same_units_when_order_size_does_not_breach_non_default_short_limit_on_1st_ccy(self):
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit_short=-10)
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 10, 'sell')
        filtered = self.rm.filter_order(order)
        self.assertEquals(filtered.units, 10)

    def test_filtered_sell_order_should_have_less_units_when_order_size_breaches_default_short_limit_on_1st_ccy(self):
        order = OrderEvent('EUR_SGD', 10000, 'sell')
        filtered = self.rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        amount_in_base_ccy = round(self.rm.ccy_limit / self.rm.rates_cache.get_rate('SGD_USD')['ask'], 0)
        self.assertEquals(amount_in_base_ccy, filtered.units)

    def test_filtered_order_should_have_less_units_when_order_size_breaches_specific_limit_less_than_default_on_1st_ccy(self):
        ccy_limits = {'CHF': 100}
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit=1000, ccy_limits=ccy_limits)
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 1000, 'buy')
        amount_in_base_ccy = round(rm.ccy_limits['CHF'] / self.rm.rates_cache.get_rate('CHF_USD')['ask'], 0)
        filtered = rm.filter_order(order)
        self.assertEquals(amount_in_base_ccy, filtered.units)

    def test_filtered_order_should_have_less_units_when_order_size_does_not_breach_specific_limit_more_than_default_on_1st_ccy_with_fx_rate_gt_1(self):
        ccy_limits = {'CHF': 10000}
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit=1000, ccy_limits=ccy_limits, ccy_limit_short=-10000)
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        amount_in_base_ccy = round(rm.ccy_limits['CHF'] / rm.rates_cache.get_rate('CHF_USD')['ask'], 0)
        self.assertEquals(amount_in_base_ccy, filtered.units)

    def test_filtered_sell_order_should_have_less_units_when_order_size_breaches_short_specific_limit_less_than_default_short_limit_on_1st_ccy(self):
        ccy_limits_short = {'CHF': -100}
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit_short=-1000, ccy_limits_short=ccy_limits_short)
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 1000, 'sell')
        amount_in_base_ccy = round(-1 * rm.ccy_limits_short['CHF'] / self.rm.rates_cache.get_rate('CHF_USD')['bid'], 0)
        filtered = rm.filter_order(order)
        self.assertEquals(amount_in_base_ccy, filtered.units)
        self.assertEquals(filtered.instrument, 'CHF_USD')
        self.assertEquals(filtered.side, 'sell')

    def test_filtered_sell_order_should_have_same_units_when_order_size_breaches_short_specific_limit_more_than_default_short_limit_on_1st_ccy(self):
        ccy_limits_short = {'CHF': -10000}
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit_short=-1000, ccy_limits_short=ccy_limits_short, ccy_limit=100000)
        self.assign_unity_rates(rm)
        order = OrderEvent('CHF_USD', 10000, 'sell')
        filtered = rm.filter_order(order)
        self.assertEquals(10000, filtered.units)
        self.assertEquals(filtered.instrument, 'CHF_USD')
        self.assertEquals(filtered.side, 'sell')

    def test_should_allow_to_set_ccy_limit_and_have_expected_value(self):
        rm = CcyExposureLimitRiskEvaluator('BC', self.cache, ccy_limits={})
        rm.set_limit('CHF', 1234.5)
        self.assertEquals(rm.ccy_limits['CHF'], 1234.5)

    def test_filtered_order_should_have_less_units_when_order_size_breaches_both_specific_and_default_limit_on_1st_ccy(self):
        ccy_limits = {'CHF': 12000}
        rm = CcyExposureLimitRiskEvaluator('SGD', self.cache, ccy_limit=10000, ccy_limits=ccy_limits, ccy_limit_short=-100000)
        self.assign_unity_rates(rm)
        order = OrderEvent('CHF_SGD', 15000, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 12000)

    def test_should_allow_to_set_unity_fx_rate_and_have_same_units(self):
        ccy_limits = {'CHF': 110}
        rm = CcyExposureLimitRiskEvaluator('SGD', self.cache, ccy_limit=10000, ccy_limits=ccy_limits)
        rm.rates_cache.set_rate(TickEvent('CHF_SGD', get_time(), 1.0, 1.0))
        order = OrderEvent('CHF_SGD', 105, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 105)

    def test_should_allow_to_set_unity_fx_rate_and_have_less_units_when_order_size_breaches_specific_limit_on_1st_ccy(self):
        ccy_limits = {'CHF': 110}
        rm = CcyExposureLimitRiskEvaluator('SGD', self.cache, ccy_limit=10000, ccy_limits=ccy_limits)
        rm.rates_cache.set_rate(TickEvent('CHF_SGD', get_time(), 1.0, 1.0))
        order = OrderEvent('CHF_SGD', 150, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 110)

    def test_should_allow_second_instrument_without_breach_if_another_instrument_already_breached(self):
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = self.rm.filter_order(order)
        amount_in_base_ccy = round(self.rm.ccy_limit / self.rm.rates_cache.get_rate('CHF_USD')['ask'])
        self.assertEquals(filtered.units, amount_in_base_ccy)

        order = OrderEvent('EUR_SGD', 100, 'buy')
        filtered = self.rm.filter_order(order)
        self.assertEquals(filtered.units, 100)

    def test_should_allow_second_instrument_without_breach_if_first_instrument_breaches_specific_limit(self):
        ccy_limits = {'CHF': 1234}
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit=100, ccy_limits=ccy_limits)
        self.assign_unity_rates(rm)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        amount_in_base_ccy = round(rm.ccy_limits['CHF'] / rm.rates_cache.get_rate('CHF_USD')['ask'])
        self.assertEquals(filtered.units, amount_in_base_ccy)
        rm.append_position(filtered.instrument, filtered.units)

        order = OrderEvent('EUR_SGD', 1000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 1000)
        self.assertEquals(filtered.units, 100)

    def test_should_allow_to_set_short_ccy_limit_and_have_expected_value(self):
        rm = CcyExposureLimitRiskEvaluator('BC', self.cache, ccy_limits={})
        rm.set_limit('CHF', ccy_limit_short=-1234.5)
        self.assertEquals(rm.ccy_limits_short['CHF'], -1234.5)

    def test_should_allow_to_set_long_short_ccy_limit_and_have_expected_value(self):
        rm = CcyExposureLimitRiskEvaluator('BC', self.cache)
        rm.set_limit('SHF_USD', ccy_limit=10000, ccy_limit_short=-22)
        self.assertEquals(rm.ccy_limits['SHF_USD'], 10000)
        self.assertEquals(rm.ccy_limits_short['SHF_USD'], -22)

    def test_should_allow_to_set_long_ccy_limit_and_unset_short_limit(self):
        rm = CcyExposureLimitRiskEvaluator('BC', self.cache)
        rm.set_limit('SHF_USD', ccy_limit_short=-22)
        self.assertEquals(rm.ccy_limits_short['SHF_USD'], -22)
        rm.set_limit('SHF_USD', ccy_limit=10000)
        self.assertEquals(rm.ccy_limits['SHF_USD'], 10000)
        self.assertFalse('SHF_USD' in rm.ccy_limits_short)

    def test_should_allow_to_set_short_ccy_limit_and_unset_long_limit(self):
        rm = CcyExposureLimitRiskEvaluator('BC', self.cache)
        rm.set_limit('SHF_USD', ccy_limit=10000)
        self.assertEquals(rm.ccy_limits['SHF_USD'], 10000)
        rm.set_limit('SHF_USD', ccy_limit_short=-22)
        self.assertEquals(rm.ccy_limits_short['SHF_USD'], -22)
        self.assertFalse('SHF_USD' in rm.ccy_limits)

    def test_should_allow_to_unset_ccy_limits(self):
        rm = CcyExposureLimitRiskEvaluator('BC', self.cache)
        rm.set_limit('SHF_USD', ccy_limit=10000 , ccy_limit_short=-22)
        self.assertEquals(rm.ccy_limits['SHF_USD'], 10000)
        self.assertEquals(rm.ccy_limits_short['SHF_USD'], -22)
        rm.set_limit('SHF_USD')
        self.assertFalse('SHF_USD' in rm.ccy_limits)
        self.assertFalse('SHF_USD' in rm.ccy_limits_short)

    def test_should_init_with_rates_cache(self):
        cache = FxPricesCache()
        self.assertEquals(CcyExposureLimitRiskEvaluator('BC', cache, ccy_limits={}).rates_cache, cache)

    """

    def testCannotFilterOrderWithStaleRates(self):
        rm = CcyExposureLimitRiskEvaluator('ABC')
        try:
            filtered = rm.filter_order(OrderEvent('CHF_USD', 1000, 'buy'))
            self.fail('Filtered order without current fx rates')
        except AssertionError:
            pass
    """