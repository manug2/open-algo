import sys

sys.path.append('../../main')
import unittest

from com.open.algo.trading.fxEvents import OrderEvent, ExecutedOrder, ORDER_SIDE_BUY, ORDER_SIDE_SELL
from com.open.algo.trading.fxEvents import ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET
from com.open.algo.utils import EVENT_TYPES_ORDER


class TestOrderEvents(unittest.TestCase):
    def setUp(self):
        self.buy_order = OrderEvent('ABC', 125, ORDER_SIDE_BUY)
        self.sell_order = OrderEvent('ABC', 100, ORDER_SIDE_SELL)
        self.market_order = OrderEvent('ABC', 101, ORDER_SIDE_BUY, order_type=ORDER_TYPE_MARKET)
        self.limit_order = OrderEvent('ABC', 102, ORDER_SIDE_SELL, order_type=ORDER_TYPE_LIMIT)

    def test_should_have_expected_type(self):
        self.assertEquals(self.buy_order.TYPE, EVENT_TYPES_ORDER)

    def test_should_have_expected_instrument(self):
        self.assertEquals(self.buy_order.instrument, 'ABC')

    def test_should_have_expected_units(self):
        self.assertEquals(self.buy_order.units, 125)

    def test_should_have_expected_order_type(self):
        self.assertEquals(self.market_order.order_type, ORDER_TYPE_MARKET)

    def test_should_have_expected_side_buy(self):
        self.assertEquals(self.buy_order.side, ORDER_SIDE_BUY)

    def test_should_have_expected_side_sell(self):
        self.assertEquals(self.sell_order.side, ORDER_SIDE_SELL)

    def test_should_have_expected_order_type_limit(self):
        self.assertEquals(self.limit_order.order_type, ORDER_TYPE_LIMIT)

    def test_should_not_allow_to_create_with_wrong_order_type(self):
        try:
            OrderEvent('ABC', 1, ORDER_SIDE_BUY, order_type='random type')
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_wrong_side(self):
        try:
            OrderEvent('ABC', 1, 'random side')
            self.fail('should have failed')
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_0_units(self):
        try:
            OrderEvent('ABC', 0, ORDER_SIDE_BUY)
            self.fail('should have failed')
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_bad_units(self):
        try:
            OrderEvent('ABC', 'hello', ORDER_SIDE_BUY)
            self.fail('should have failed')
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_negative_units(self):
        try:
            OrderEvent('ABC', -100, ORDER_SIDE_BUY)
            self.fail('should have failed')
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_none_instrument(self):
        try:
            OrderEvent(None, -100, ORDER_SIDE_BUY)
            self.fail('should have failed')
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_empty_instrument(self):
        try:
            OrderEvent('', -100, ORDER_SIDE_BUY)
            self.fail('should have failed')
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_none_units(self):
        try:
            OrderEvent('ABC', None, ORDER_SIDE_BUY)
            self.fail('should have failed')
        except AssertionError:
            pass
        except TypeError:
            pass

    def test_should_not_allow_to_create_with_none_side(self):
        try:
            OrderEvent('ABC', 100, None)
            self.fail('should have failed')
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_none_type(self):
        try:
            OrderEvent('ABC', 100, ORDER_SIDE_BUY, order_type=None)
            self.fail('should have failed')
        except AssertionError:
            pass

    def test_should_have_orig_units(self):
        self.assertEquals(self.limit_order.orig_units, 102)

    def test_should_have_orig_units_after_filter(self):
        self.limit_order.units = 0
        self.assertEquals(self.limit_order.orig_units, 102)

    def test_should_get_units_with_sign_buy(self):
        self.assertEquals(OrderEvent('ABC', 102, ORDER_SIDE_BUY).get_signed_units(), 102)

    def test_should_get_units_with_sign_sell(self):
        self.assertEquals(OrderEvent('ABC', 1, ORDER_SIDE_SELL).get_signed_units(), -1)

    def test_should_get_orig_units_with_sign_buy(self):
        self.assertEquals(OrderEvent('ABC', 1, ORDER_SIDE_BUY).get_signed_orig_units(), 1)

    def test_should_get_orig_units_with_sign_sell(self):
        self.assertEquals(OrderEvent('ABC', 1, ORDER_SIDE_SELL).get_signed_orig_units(), -1)

    def test_should_get_orig_units_with_sign_buy_after_filter(self):
        order = OrderEvent('ABC', 1, ORDER_SIDE_BUY)
        order.units = 0
        self.assertEquals(order.get_signed_orig_units(), 1)

    def test_should_get_orig_units_with_sign_sell_after_filter(self):
        order = OrderEvent('ABC', 1, ORDER_SIDE_SELL)
        order.units = 0
        self.assertEquals(order.get_signed_orig_units(), -1)


class TestExecutedOrder(unittest.TestCase):
    def setUp(self):
        self.buy_order = OrderEvent('ABC', 1, ORDER_SIDE_BUY)
        self.sell_order = OrderEvent('ABC', 1, ORDER_SIDE_SELL)
        self.limit_order = OrderEvent('ABC', 1, ORDER_SIDE_SELL, order_type=ORDER_TYPE_LIMIT)
        self.market_order = OrderEvent('ABC', 1, ORDER_SIDE_BUY, order_type=ORDER_TYPE_MARKET)

    def test_should_have_expected_order_buy(self):
        executed = ExecutedOrder(self.buy_order, 1.1, 100)
        self.assertEquals(self.buy_order, executed.order)

    def test_should_have_expected_order_sell(self):
        executed = ExecutedOrder(self.sell_order, 1.1, 100)
        self.assertEquals(self.sell_order, executed.order)

    def test_should_have_expected_order_market(self):
        executed = ExecutedOrder(self.market_order, 1.1, 100)
        self.assertEquals(self.market_order, executed.order)

    def test_should_have_expected_order_limit(self):
        executed = ExecutedOrder(self.limit_order, 1.1, 100)
        self.assertEquals(self.limit_order, executed.order)

    def test_should_have_expected_execution_price(self):
        executed = ExecutedOrder(self.limit_order, 1.5, 100)
        self.assertEquals(1.5, executed.price)

    def test_should_have_expected_execution_units(self):
        executed = ExecutedOrder(self.limit_order, 1.5, 1011)
        self.assertEquals(1011, executed.units)

    def test_should_have_expected_signed_execution_buy(self):
        executed = ExecutedOrder(self.buy_order, 1.5, 101)
        self.assertEquals(101, executed.get_signed_units())

    def test_should_have_expected_signed_execution_sell(self):
        executed = ExecutedOrder(self.sell_order, 1.5, 101)
        self.assertEquals(-101, executed.get_signed_units())
