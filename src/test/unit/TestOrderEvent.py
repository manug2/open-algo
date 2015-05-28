import sys

sys.path.append('../../main')
import unittest

from com.open.algo.trading.fxEvents import OrderEvent, ORDER_SIDE_BUY, ORDER_SIDE_SELL
from com.open.algo.model import EVENT_TYPES_ORDER


class TestOrderEvents(unittest.TestCase):
    def setUp(self):
        pass

    def test_should_have_expected_type(self):
        self.assertEquals(OrderEvent('ABC', 1, ORDER_SIDE_SELL).TYPE, EVENT_TYPES_ORDER)

    def test_should_have_expected_instrument(self):
        self.assertEquals(OrderEvent('ABC', 1, ORDER_SIDE_BUY).instrument, 'ABC')

    def test_should_have_expected_units(self):
        self.assertEquals(OrderEvent('ABC', 125, ORDER_SIDE_SELL).units, 125)

    def test_should_have_expected_order_type(self):
        self.assertEquals(OrderEvent('ABC', 1, ORDER_SIDE_BUY, order_type='market').order_type, 'market')

    def test_should_have_expected_side(self):
        self.assertEquals(OrderEvent('ABC', 1, ORDER_SIDE_SELL).side, ORDER_SIDE_SELL)

    def test_should_have_expected_order_type_limit(self):
        self.assertEquals(OrderEvent('ABC', 1, ORDER_SIDE_SELL, order_type='limit').order_type, 'limit')

    def test_should_not_allow_to_create_with_wrong_order_type(self):
        try:
            OrderEvent('ABC', 1, ORDER_SIDE_BUY, order_type='random type')
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_wrong_side_BUY(self):
        try:
            OrderEvent('ABC', 1, ORDER_SIDE_BUY)
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_wrong_side_SELL(self):
        try:
            OrderEvent('ABC', 1, ORDER_SIDE_BUY)
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_wrong_side(self):
        try:
            OrderEvent('ABC', 1, 'random side')
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_0_units(self):
        try:
            OrderEvent('ABC', 0, ORDER_SIDE_BUY)
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_bad_units(self):
        try:
            OrderEvent('ABC', 'hello', ORDER_SIDE_BUY)
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_negative_units(self):
        try:
            OrderEvent('ABC', -100, ORDER_SIDE_BUY)
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_none_instrument(self):
        try:
            OrderEvent(None, -100, ORDER_SIDE_BUY)
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_empty_instrument(self):
        try:
            OrderEvent('', -100, ORDER_SIDE_BUY)
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_none_units(self):
        try:
            OrderEvent('ABC', None, ORDER_SIDE_BUY)
        except AssertionError:
            pass
        except TypeError:
            pass

    def test_should_not_allow_to_create_with_none_side(self):
        try:
            OrderEvent('ABC', 100, None)
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_none_type(self):
        try:
            OrderEvent('ABC', 100, ORDER_SIDE_BUY, order_type=None)
        except AssertionError:
            pass

    def test_should_have_orig_units(self):
        self.assertEquals(OrderEvent('ABC', 1, ORDER_SIDE_SELL, order_type='limit').orig_units, 1)
