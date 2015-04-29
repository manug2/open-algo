import sys

sys.path.append('../../main')
import unittest

from com.open.algo.trading.fxEvents import OrderEvent


class TestOrderEvents(unittest.TestCase):
    def setUp(self):
        pass

    def testOrderEventHasExpectedType(self):
        self.assertEquals(OrderEvent('ABC', 1, 'sell').TYPE, 'ORDER')

    def testOrderEventHasExpectedInstrument(self):
        self.assertEquals(OrderEvent('ABC', 1, 'buy').instrument, 'ABC')

    def testOrderEventHasExpectedUnits(self):
        self.assertEquals(OrderEvent('ABC', 125, 'sell').units, 125)

    def testOrderEventHasExpectedOrderType(self):
        self.assertEquals(OrderEvent('ABC', 1, 'buy', order_type='market').order_type, 'market')

    def testOrderEventHasExpectedSide(self):
        self.assertEquals(OrderEvent('ABC', 1, 'sell').side, 'sell')

    def testOrderEventHasExpectedOrderType2(self):
        self.assertEquals(OrderEvent('ABC', 1, 'sell', order_type='limit').order_type, 'limit')

    def test_should_not_allow_to_create_with_wrong_order_type(self):
        try:
            OrderEvent('ABC', 1, 'buy', order_type='random type')
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_wrong_side_BUY(self):
        try:
            OrderEvent('ABC', 1, 'BUY')
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_wrong_side_SELL(self):
        try:
            OrderEvent('ABC', 1, 'BUY')
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_wrong_side(self):
        try:
            OrderEvent('ABC', 1, 'random side')
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_0_units(self):
        try:
            OrderEvent('ABC', 0, 'buy')
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_negative_units(self):
        try:
            OrderEvent('ABC', -100, 'buy')
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_none_instrument(self):
        try:
            OrderEvent(None, -100, 'buy')
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_empty_instrument(self):
        try:
            OrderEvent('', -100, 'buy')
        except AssertionError:
            pass

    def test_should_not_allow_to_create_with_none_units(self):
        try:
            OrderEvent('ABC', None, 'buy')
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
            OrderEvent('ABC', 100, 'buy', order_type=None)
        except AssertionError:
            pass
