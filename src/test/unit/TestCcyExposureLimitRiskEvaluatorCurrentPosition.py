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

    def test_should_have_positions(self):
        self.assertIsNotNone(CcyExposureLimitRiskEvaluator('BC', self.cache).positions)

    def test_should_allow_to_append_positions(self):
        rm = CcyExposureLimitRiskEvaluator('BC', self.cache)
        rm.append_position('EUR_CHF', 123)

    def test_should_have_appended_positions(self):
        rm = CcyExposureLimitRiskEvaluator('BC', self.cache)
        rm.append_position('EUR_CHF', 123)
        self.assertEquals(rm.positions['EUR_CHF'], 123)

    def test_should_allow_to_append_positions_twice(self):
        rm = CcyExposureLimitRiskEvaluator('BC', self.cache)
        rm.append_position('EUR_CHF', 123)
        rm.append_position('EUR_CHF', 27)
        self.assertEquals(rm.positions['EUR_CHF'], 150)

    def test_should_allow_to_append_different_positions(self):
        rm = CcyExposureLimitRiskEvaluator('BC', self.cache)
        rm.append_position('EUR_CHF', 123)
        rm.append_position('EUR_USD', 1000)
        self.assertEquals(rm.positions['EUR_CHF'], 123)
        self.assertEquals(rm.positions['EUR_USD'], 1000)

    def test_filtered_order_should_have_same_units_when_order_size_plus_current_position_does_not_breach_default_limit(self):
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache)
        self.assign_unity_rates(rm)
        rm.append_position('CHF', 10)
        order = OrderEvent('CHF_USD', 100, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 100)

    def test_filtered_order_should_have_same_units_when_order_size_plus_current_position_does_not_breach_specific_limit(self):
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limits={'CHF': 1234})
        self.assign_unity_rates(rm)
        rm.append_position('CHF', 10)
        order = OrderEvent('CHF_USD', 100, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 100)

    def test_filtered_order_should_have_less_units_when_order_size_plus_current_position_breaches_default_limit(self):
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache)
        self.assign_unity_rates(rm)
        rm.append_position('CHF', 10)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, rm.ccy_limit-10)

    def test_filtered_order_should_have_less_units_when_order_size_plus_current_position_breaches_specific_limit(self):
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limits={'CHF': 1234})
        self.assign_unity_rates(rm)
        rm.append_position('CHF', 10)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, rm.ccy_limits['CHF']-10)

    def test_should_allow_second_instrument_without_breach_if_another_instrument_already_breached(self):
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache)
        self.assign_unity_rates(rm)
        rm.append_position('CHF', 10)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, rm.ccy_limit-10)

        order = OrderEvent('EUR_SGD', 100, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 100)

    def test_should_allow_second_instrument_without_breach_if_first_instrument_breaches_specific_limit(self):
        ccy_limits = {'CHF': 1234}
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit=100, ccy_limits=ccy_limits)
        self.assign_unity_rates(rm)
        rm.append_position('CHF', 10)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, rm.ccy_limits['CHF']-10)
        rm.append_position(filtered.instrument, filtered.units)

        order = OrderEvent('EUR_SGD', 100, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 100)

    def test_should_allow_specific_limit_on_second_instrument_with_current_position_on_first(self):
        ccy_limits = {'CHF': 1234, 'EUR': 10000}
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit=100, ccy_limits=ccy_limits)
        self.assign_unity_rates(rm)
        rm.append_position('EUR', 100)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'buy'))
        self.assertEquals(filtered.units, 1234)
        rm.append_position(filtered.instrument, filtered.units)

    def test_should_allow_specific_limit_on_second_instrument_with_current_position_on_first_complex(self):
        ccy_limits = {'CHF': 1234, 'EUR': 10000}
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit=100, ccy_limits=ccy_limits, ccy_limit_short=-100000)
        self.assign_unity_rates(rm)
        rm.append_position('EUR', 100)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'buy'))
        self.assertEquals(filtered.units, 1234)
        rm.append_position('CHF', filtered.units)

        filtered = rm.filter_order(OrderEvent('EUR_USD', 5000, 'buy'))
        self.assertEquals(filtered.units, 5000)
        rm.append_position('EUR', filtered.units)

        filtered = rm.filter_order(OrderEvent('EUR_USD', 50000, 'buy'))
        self.assertEquals(filtered.units, 4900)

    """
        *************************************************
        #Short current positions
        *************************************************
    """

    def test_should_allow_short_current_position(self):
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit=100)
        rm.append_position('CHF', -10)

    def test_should_have_same_units_than_buy_order_size_when_have_short_current_position_and_order_does_not_breach(self):
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit=100)
        self.assign_unity_rates(rm)
        rm.append_position('CHF', -10)
        order = OrderEvent('CHF_USD', 50, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 50)

    def test_should_have_more_units_than_buy_order_size_when_have_short_current_position_and_order_breaches_default_limit(self):
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit_short=-100000)
        self.assign_unity_rates(rm)
        rm.append_position('CHF', -10)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, rm.ccy_limit+10)

    def test_should_have_more_units_than_buy_order_size_when_have_short_current_position_and_order_breaches_specific_limit(self):
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limits={'CHF':1235})
        self.assign_unity_rates(rm)
        rm.append_position('CHF', -10)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, rm.ccy_limits['CHF']+10)



    def test_should_filters_two_orders_in_different_instruments_correctly(self):
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit=100)
        self.assign_unity_rates(rm)
        rm.append_position('CHF', -10)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 110)

        order = OrderEvent('EUR_SGD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 10000)
        self.assertEquals(filtered.units, 100)

    def test_should_filters_two_orders_in_different_instruments_correctly2(self):
        ccy_limits = {'CHF': 1234}
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit=100, ccy_limits=ccy_limits)
        self.assign_unity_rates(rm)
        rm.append_position('CHF', -100)
        order = OrderEvent('CHF_USD', 10000, 'buy')
        filtered = rm.filter_order(order)
        self.assertEquals(filtered.units, 1334)

        order = OrderEvent('EUR_SGD', 1000, 'buy')
        filtered = rm.filter_order(order)
        self.assertNotEquals(filtered.units, 1000)
        self.assertEquals(filtered.units, 100)

    def test_should_filters_two_orders_in_different_instruments_correctly3(self):
        ccy_limits = {'CHF': 1234, 'EUR': 10000}
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit=100, ccy_limits=ccy_limits, ccy_limit_short=-100000)
        self.assign_unity_rates(rm)
        rm.append_position('EUR', -100)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'buy'))
        self.assertEquals(filtered.units, 1234)

        filtered = rm.filter_order(OrderEvent('EUR_USD', 5000, 'buy'))
        self.assertEquals(filtered.units, 5000)
        rm.append_position('EUR', filtered.units)

        filtered = rm.filter_order(OrderEvent('EUR_USD', 50000, 'buy'))
        self.assertEquals(filtered.units, 5100)

    def test_should_filters_two_orders_in_different_instruments_correctly4(self):
        ccy_limits = {'CHF': 1234, 'EUR': 10000}
        rm = CcyExposureLimitRiskEvaluator('USD', self.cache, ccy_limit=100, ccy_limits=ccy_limits, ccy_limit_short=-100000)
        self.assign_unity_rates(rm)
        rm.append_position('CHF', -50)
        rm.append_position('EUR', -100)
        filtered = rm.filter_order(OrderEvent('CHF_USD', 10000, 'buy'))
        self.assertEquals(filtered.units, 1284)
        rm.append_position(filtered.instrument, filtered.units)

        filtered = rm.filter_order(OrderEvent('EUR_USD', 5000, 'buy'))
        self.assertEquals(filtered.units, 5000)
        rm.append_position('EUR', filtered.units)

        filtered = rm.filter_order(OrderEvent('EUR_USD', 50000, 'buy'))
        self.assertEquals(filtered.units, 5100)
