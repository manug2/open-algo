import sys

sys.path.append('../../main')
import unittest
from com.open.algo.risk.ccyExposureLimitRisk import CcyExposureLimitRiskEvaluator
from com.open.algo.trading.fxEvents import TickEvent, OrderEvent
from com.open.algo.trading.fxPricesCache import FxPricesCache
from com.open.algo.model import gettime


class TestRiskManager(unittest.TestCase):
    def assign_dummy_rates(self, rm):
        now = gettime()
        rm.rates_cache.set_rate(TickEvent('CHF_USD', now, 1.04, 1.05))
        rm.rates_cache.set_rate(TickEvent('EUR_USD', now, 1.08, 1.09))
        rm.rates_cache.set_rate(TickEvent('SGD_USD', now, 0.74, 0.75))
        rm.rates_cache.set_rate(TickEvent('CHF_SGD', now, 1.04, 1.05))

    def assign_unity_rates(self, rm):
        now = gettime()
        rm.rates_cache.set_rate(TickEvent('CHF_USD', now, 1.0, 1.0))
        rm.rates_cache.set_rate(TickEvent('EUR_USD', now, 1.0, 1.0))
        rm.rates_cache.set_rate(TickEvent('SGD_USD', now, 1.0, 1.0))
        rm.rates_cache.set_rate(TickEvent('CHF_SGD', now, 1.0, 1.0))

    def setUp(self):
        self.cache = FxPricesCache()
        self.rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit_short=-100000)
        self.assign_dummy_rates(self.rm)

    def test_should_have_default_short_ccy_exposure_limit(self):
        rm = CcyExposureLimitRiskEvaluator('BC', self.cache)
        self.assertTrue(rm.ccy_limit_short <= 0)

    def test_should_have_preset_short_ccy_exposure_limit(self):
        rm = CcyExposureLimitRiskEvaluator('BC', self.cache, ccy_limit_short=-123)
        self.assertEquals(rm.ccy_limit_short, -123)

    def test_should_not_allow_negative_preset_short_ccy_exposure_limit(self):
        try:
            CcyExposureLimitRiskEvaluator('BC', self.cache, ccy_limit=123)
        except AssertionError:
            pass

    def test_filtered_order_should_have_same_units_when_order_size_does_not_breach_default_short_ccy_limit_on_2nd_ccy(self):
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit_short=-150, ccy_limits={'CHF': 10000})
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 100, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 100)

    def test_filtered_order_should_have_same_units_when_order_size_does_not_breach_non_default_short_ccy_limit_on_2nd_ccy(self):
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit_short=-150, ccy_limits={'CHF': 10000})
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 140, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 140)

    def test_filtered_order_should_have_less_units_when_order_size_breaches_non_default_short_ccy_limit_on_2nd_ccy(self):
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit_short=-150, ccy_limits={'EUR': 10000})
        self.assign_unity_rates(rm)
        order = OrderEvent('EUR_SGD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(abs(rm.ccy_limit_short), filtered.units)

    def test_filtered_order_should_have_same_units_when_order_size_equals_non_default_short_ccy_limit_on_2nd_ccy(self):
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limits_short={'USD': -1000}, ccy_limits={'CHF': 1500})
        self.assign_unity_rates(rm)
        order = OrderEvent('CHF_USD', 1000, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 1000)

    def test_filtered_order_should_have_less_units_when_order_size_breaches_specific_short_ccy_limit_on_2nd_ccy(self):
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limits_short={'USD': -1000}, ccy_limits={'CHF': 15000})
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(1000, filtered.units)

    def test_filtered_sell_order_should_have_same_units_when_order_size_does_not_breach_default_limits_on_1st_and_2nd_currencies(self):
        order = OrderEvent('CHF_USD', 100, 'sell')
        filtered = self.rm.filter_order(order)
        self.assertEqual(100, filtered.units)

    def test_filtered_sell_order_should_have_same_units_when_order_size_does_not_breach_specific_short_limit_on_2nd_ccy_and_size_equals_default_limit_on_1sr_ccy(self):
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit=100, ccy_limits_short={'CHF': -234})
        self.assign_dummy_rates(rm)
        order = OrderEvent('CHF_USD', 100, 'sell')
        filtered = rm.filter_order(order)
        self.assertEquals(100, filtered.units)

    def test_filtered_order_should_have_less_units_when_order_size_breaches_specific_short_limit_on_2nd_ccy_with_fx_rate_greater_than_1(self):
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limits_short={'EUR': -100})
        self.assign_dummy_rates(rm)
        order = OrderEvent('SGD_EUR', 2000, 'buy')
        filtered = rm.filter_order(order)
        amount_in_base_ccy = round(-1 * rm.ccy_limits_short['EUR'] / rm.rates_cache.get_rate('EUR_USD')['bid'], 0)
        self.assertEquals(amount_in_base_ccy, filtered.units)

    def test_filtered_sell_order_should_have_less_units_when_order_size_breaches_specific_short_limit_on_2nd_ccy_with_fx_rate_greater_than_1(self):
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limits_short={'EUR': -100})
        self.assign_dummy_rates(rm)
        order = OrderEvent('SGD_EUR', 5000, 'sell')
        filtered = rm.filter_order(order)
        amount_in_base_ccy = round(rm.ccy_limit / rm.rates_cache.get_rate('EUR_USD')['ask'], 0)
        self.assertEquals(amount_in_base_ccy, filtered.units)

    def test_should_have_per_position_short_limit(self):
        self.assertIsNotNone(CcyExposureLimitRiskEvaluator('BC', self.cache).ccy_limits_short)

    def test_should_init_with_per_position_short_limit(self):
        self.assertEquals(CcyExposureLimitRiskEvaluator('BC', self.cache, ccy_limits_short={}).ccy_limits_short, {})
