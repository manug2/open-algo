import sys

sys.path.append('../../main')
import unittest
import queue

from com.open.algo.utils import get_time
from com.open.algo.dummy import *
from com.open.algo.trading.fxEvents import *
from com.open.algo.eventLoop import Journaler
from com.open.algo.model import EVENT_TYPES_ORDER


class TestDummyBuyStrategy(unittest.TestCase):
    def setUp(self):
        self.events = queue.Queue()
        self.journaler = Journaler()
        self.strategy = DummyBuyStrategy(self.events, 100, self.journaler)

        # ticks and events for testing
        self.tick = TickEvent('EUR_GBP', get_time(), 0.87, 0.88)
        self.buy_order = OrderEvent(self.tick.instrument, self.strategy.units, ORDER_SIDE_BUY)
        self.executed_order = ExecutedOrder(self.buy_order, 1.1, self.strategy.units)

    def testSetup(self):
        pass

    def test_should_calculate_signals(self):
        self.strategy.calculate_signals(self.tick)
        outEvent = self.journaler.get_last_event()
        self.assertEquals(self.tick.instrument, outEvent.instrument)
        self.assertEquals(outEvent.TYPE, EVENT_TYPES_ORDER)
        self.assertEquals(self.strategy.units, outEvent.units)

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

    def test_should_raise_error_when_rejected_with_wrong_event_type(self):
        self.strategy.calculate_signals(self.tick)
        self.assertEqual(self.strategy.units, self.strategy.get_signaled_position('EUR_GBP'))
        reject_order = OrderEvent('EUR_GBP', self.strategy.units, ORDER_SIDE_BUY)
        try:
            self.strategy.acknowledge_rejection(reject_order)
            self.fail('should have failed as event\'s "%s" field should be "%s, found "%s"'
                      % ('TYPE', EVENT_TYPES_REJECTED, reject_order.TYPE))
        except ValueError:
            pass
        self.assertEqual(self.strategy.units, self.strategy.get_signaled_position('EUR_GBP'))

    def test_should_maintain_signaled_position_when_rejected_with_wrong_event_type(self):
        self.strategy.calculate_signals(self.tick)
        self.assertEqual(self.strategy.units, self.strategy.get_signaled_position('EUR_GBP'))
        reject_order = OrderEvent('EUR_GBP', self.strategy.units, ORDER_SIDE_BUY)
        try:
            self.strategy.acknowledge_rejection(reject_order)
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


class TestRandomStrategy(unittest.TestCase):
    def setUp(self):
        self.events = queue.Queue()
        self.journaler = Journaler()
        self.strategy = BuyOrSellAt5thTickStrategy(self.events, 100, self.journaler)

    def testSetup(self):
        pass

    def testCalcSignalsWithOneEvent(self):
        tick = TickEvent("EUR_GBP", get_time(), 0.87, 0.88)
        self.strategy.calculate_signals(tick)
        outEvent = self.journaler.get_last_event()
        self.assertEquals(tick, outEvent)

    def testCalcSignalsWithOneEvent(self):
        for i in range(1, 5):
            tick = TickEvent("EUR_GBP", get_time(), 0.87 + i, 0.88 + i)
            self.strategy.calculate_signals(tick)
            outEvent = self.journaler.get_last_event()
            self.assertEquals(None, outEvent)

        tick = TickEvent("EUR_GBP", get_time(), 0.874, 0.885)
        self.strategy.calculate_signals(tick)
        outEvent = self.journaler.get_last_event()

        self.assertIsNotNone(outEvent)
        self.assertEquals(tick.instrument, outEvent.instrument)
        self.assertEquals(outEvent.TYPE, EVENT_TYPES_ORDER)
        self.assertEquals(self.strategy.units, outEvent.units)


