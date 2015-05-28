import sys

sys.path.append('../../main')
import unittest

from com.open.algo.utils import get_time
from com.open.algo.dummy import *
from com.open.algo.trading.fxEvents import *
from com.open.algo.utils import EVENT_TYPES_ORDER


class TestDummyBuyStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = DummyBuyStrategy(100)

        # ticks and events for testing
        self.tick = TickEvent('EUR_GBP', get_time(), 0.87, 0.88)
        self.buy_order = OrderEvent(self.tick.instrument, self.strategy.units, ORDER_SIDE_BUY)
        self.executed_order = ExecutedOrder(self.buy_order, 1.1, self.strategy.units)

    def testSetup(self):
        pass

    def test_should_calculate_signals(self):
        order = self.strategy.calculate_signals(self.tick)
        self.assertEquals(self.tick.instrument, order.instrument)
        self.assertEquals(EVENT_TYPES_ORDER, order.TYPE)
        self.assertEquals(self.strategy.units, order.units)

    def test_should_have_signaled_positions(self):
        self.assertIsNotNone(self.strategy.get_signaled_positions())

    def test_should_raise_error_when_instrument_not_in_signaled_positions(self):
        try:
            self.strategy.get_signaled_position('EUR_USD')
            self.fail('should have failed while getting non-present signaled positions')
        except KeyError:
            pass

    def test_should_give_signaled_position_for_instrument(self):
        self.strategy.calculate_signals(self.tick)
        self.assertIsInstance(self.strategy.get_signaled_position('EUR_GBP'), int, 'should have been "int" type')

    def test_should_keep_record_of_signaled_position_when_only_one_instrument(self):
        self.strategy.calculate_signals(self.tick)
        self.assertDictEqual({'EUR_GBP': self.strategy.units}, self.strategy.get_signaled_positions())

    def test_should_keep_record_of_signaled_positions_when_two_instruments(self):
        self.strategy.calculate_signals(self.tick)
        tick = TickEvent('EUR_USD', get_time(), 0.97, 0.98)
        self.strategy.calculate_signals(tick)
        self.assertDictEqual(
            {'EUR_GBP': self.strategy.units, 'EUR_USD': self.strategy.units}, self.strategy.get_signaled_positions())

    def test_should_raise_error_when_ack_with_wrong_event_type(self):
        self.strategy.calculate_signals(self.tick)
        self.assertEqual(self.strategy.units, self.strategy.get_signaled_position('EUR_GBP'))
        reject_order = OrderEvent('EUR_GBP', self.strategy.units, ORDER_SIDE_BUY)
        try:
            self.strategy.acknowledge(reject_order)
            self.fail('should have failed as event\'s "%s" field should be "%s, found "%s"'
                      % ('TYPE', EVENT_TYPES_REJECTED, reject_order.TYPE))
        except ValueError:
            pass
        self.assertEqual(self.strategy.units, self.strategy.get_signaled_position('EUR_GBP'))

    def test_should_maintain_signaled_position_when_ack_with_wrong_event_type(self):
        self.strategy.calculate_signals(self.tick)
        self.assertEqual(self.strategy.units, self.strategy.get_signaled_position('EUR_GBP'))
        reject_order = OrderEvent('EUR_GBP', self.strategy.units, ORDER_SIDE_BUY)
        try:
            self.strategy.acknowledge(reject_order)
            self.fail('should have failed as event\'s "%s" field should be "%s, found "%s"'
                      % ('TYPE', EVENT_TYPES_REJECTED, reject_order.TYPE))
        except ValueError:
            pass
        self.assertEqual(self.strategy.units, self.strategy.get_signaled_position('EUR_GBP'))

    def test_should_have_no_signaled_positions_when_rejected(self):
        self.strategy.calculate_signals(self.tick)
        self.assertEqual(self.strategy.units, self.strategy.get_signaled_position('EUR_GBP'))
        reject_order = OrderEvent('EUR_GBP', self.strategy.units, ORDER_SIDE_BUY)
        reject_order.TYPE = EVENT_TYPES_REJECTED
        self.strategy.acknowledge_rejection(reject_order)
        self.assertEqual(0, self.strategy.get_signaled_position('EUR_GBP'))

    # open interests after execution is successful
    def test_should_give_open_interests(self):
        open_interests = self.strategy.get_open_interests()
        self.assertIsNotNone(open_interests)

    def test_should_raise_error_when_instrument_not_in_open_interests(self):
        try:
            self.strategy.get_open_interest('EUR_USD')
            self.fail('should have failed while getting non-present open interest')
        except KeyError:
            pass

    def test_should_give_open_interest_for_instrument_when_executed(self):
        self.strategy.calculate_signals(self.tick)
        self.strategy.acknowledge_execution(self.executed_order)
        self.assertIsInstance(self.strategy.get_open_interest('EUR_GBP'), int, 'should have been "int" type')

    def test_should_keep_record_of_open_interest_when_only_one_instrument(self):
        self.strategy.calculate_signals(self.tick)
        self.strategy.acknowledge_execution(self.executed_order)
        self.assertDictEqual({'EUR_GBP': self.strategy.units}, self.strategy.get_open_interests())

    def test_should_keep_record_of_open_interest_when_two_instruments(self):
        self.strategy.calculate_signals(self.tick)
        self.strategy.acknowledge_execution(self.executed_order)
        tick = TickEvent('EUR_USD', get_time(), 0.97, 0.98)
        self.strategy.calculate_signals(tick)
        second_order = OrderEvent(tick.instrument, self.strategy.units, ORDER_SIDE_BUY)
        second_execution = ExecutedOrder(second_order, 1.2, self.strategy.units)
        self.strategy.acknowledge_execution(second_execution)
        self.assertDictEqual(
            {'EUR_GBP': self.strategy.units, 'EUR_USD': self.strategy.units}, self.strategy.get_open_interests())

    def test_should_keep_record_of_open_interest_when_two_instruments_when_acknowledged_out_of_order(self):
        self.strategy.calculate_signals(self.tick)
        tick = TickEvent('EUR_USD', get_time(), 0.97, 0.98)
        self.strategy.calculate_signals(tick)
        second_order = OrderEvent(tick.instrument, self.strategy.units, ORDER_SIDE_BUY)
        second_execution = ExecutedOrder(second_order, 1.2, self.strategy.units)
        self.strategy.acknowledge_execution(second_execution)
        self.strategy.acknowledge_execution(self.executed_order)
        self.assertDictEqual(
            {'EUR_GBP': self.strategy.units, 'EUR_USD': self.strategy.units}, self.strategy.get_open_interests())

    def test_should_give_open_interest_for_instrument_when_acknowledge_with_executed_order(self):
        self.strategy.calculate_signals(self.tick)
        self.strategy.acknowledge(self.executed_order)
        self.assertIsInstance(self.strategy.get_open_interest('EUR_GBP'), int, 'should have been "int" type')

    def test_should_have_no_signaled_positions_when_acknowledged_with_rejection(self):
        self.strategy.calculate_signals(self.tick)
        self.assertEqual(self.strategy.units, self.strategy.get_signaled_position('EUR_GBP'))
        reject_order = OrderEvent('EUR_GBP', self.strategy.units, ORDER_SIDE_BUY)
        reject_order.TYPE = EVENT_TYPES_REJECTED
        self.strategy.acknowledge(reject_order)
        self.assertEqual(0, self.strategy.get_signaled_position('EUR_GBP'))


class TestRandomStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = BuyOrSellAt5thTickStrategy(100)
        self.tick = TickEvent('EUR_GBP', get_time(), 0.87, 0.88)

    def testSetup(self):
        pass

    def test_should_not_give_order_on_first_tick(self):
        tick = TickEvent("EUR_GBP", get_time(), 0.87, 0.88)
        order = self.strategy.calculate_signals(tick)
        self.assertIsNone(order)

    def test_should_give_order_when_calculating_5_ticks(self):
        for i in range(1, 5):
            tick = TickEvent('EUR_GBP', get_time(), 0.87 + i, 0.88 + i)
            order = self.strategy.calculate_signals(tick)
            self.assertEquals(None, order)

        tick = TickEvent('EUR_GBP', get_time(), 0.874, 0.885)
        order = self.strategy.calculate_signals(tick)

        self.assertIsNotNone(order)
        self.assertEquals(tick.instrument, order.instrument)
        self.assertEquals(order.TYPE, EVENT_TYPES_ORDER)
        self.assertEquals(self.strategy.units, order.units)

    def test_should_give_open_interest_for_instrument_when_acknowledge_with_executed_order(self):
        for i in range(1, 5):
            tick = TickEvent('EUR_GBP', get_time(), 0.87 + i, 0.88 + i)
            order = self.strategy.calculate_signals(tick)
            self.assertEquals(None, order)

        order = self.strategy.calculate_signals(self.tick)
        executed_order = ExecutedOrder(order, 1.1, self.strategy.units)
        self.strategy.acknowledge(executed_order)
        self.assertIsInstance(self.strategy.get_open_interest('EUR_GBP'), int, 'should have been "int" type')

    def test_should_have_no_signaled_positions_when_acknowledged_with_rejection(self):
        for i in range(1, 5):
            tick = TickEvent('EUR_GBP', get_time(), 0.87 + i, 0.88 + i)
            order = self.strategy.calculate_signals(tick)
            self.assertEquals(None, order)

        self.strategy.calculate_signals(self.tick)
        units = self.strategy.get_signaled_position('EUR_GBP')
        if units > 0:
            side = ORDER_SIDE_BUY
        else:
            side = ORDER_SIDE_SELL
        self.assertEqual(self.strategy.units, abs(units))
        reject_order = OrderEvent('EUR_GBP', self.strategy.units, side)
        reject_order.TYPE = EVENT_TYPES_REJECTED
        self.strategy.acknowledge(reject_order)
        self.assertEqual(0, self.strategy.get_signaled_position('EUR_GBP'))

