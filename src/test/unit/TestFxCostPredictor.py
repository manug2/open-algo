__author__ = 'ManuGarg'

import sys
import queue

sys.path.append('../../main')
import unittest
from com.open.algo.trading.fxCostPredictor import FxSpreadCostEvaluator
from com.open.algo.trading.fxEvents import *
from com.open.algo.utils import get_time


class TestCostPrediction(unittest.TestCase):

    def setUp(self):
        self.events = queue.Queue()
        self.cost_predictor = FxSpreadCostEvaluator(self.events)

    def test_should_be_able_to_pull_one_tick_from_event_queue(self):
        tick = TickEvent('CHF_USD', get_time(), 1.0, 1.0)
        events = queue.Queue()
        cost_predictor = FxSpreadCostEvaluator(events)
        events.put_nowait(tick)
        cost_predictor.pull_process()
        self.assertEqual(cost_predictor.get_last_tick(), tick)

    def test_should_not_eval_cost_if_no_tick(self):
        events = queue.Queue()
        cost_predictor = FxSpreadCostEvaluator(events)
        cost_predictor.pull_process()
        order = OrderEvent('CHF_USD', 100, 'buy')
        try:
            cost_predictor.eval_cost(order)
            self.fail('should have given error as np tick is present')
        except KeyError:
            pass

    def test_should_not_eval_cost_if_no_tick_for_specific_instrument(self):
        tick = TickEvent('CHF_USD', get_time(), 1.0, 1.0)
        events = queue.Queue()
        events.put_nowait(tick)
        cost_predictor = FxSpreadCostEvaluator(events)
        cost_predictor.pull_process()
        order = OrderEvent('EUR_USD', 100, 'buy')
        try:
            cost_predictor.eval_cost(order)
            self.fail('should have given error as no tick for [%s] is present' % order.instrument)
        except KeyError:
            pass

    def test_should_be_able_to_pull_two_ticks_from_event_queue(self):
        tick1 = TickEvent('CHF_USD', get_time(), 1.0, 1.0)
        tick2 = TickEvent('EUR_USD', get_time(), 1.0, 1.0)
        events = queue.Queue()
        cost_predictor = FxSpreadCostEvaluator(events)
        events.put_nowait(tick1)
        events.put_nowait(tick2)
        cost_predictor.pull_process()
        self.assertEqual(cost_predictor.get_last_tick(), tick2)

    def test_should_be_able_to_pull_two_ticks_of_same_instrument_from_event_queue(self):
        tick1 = TickEvent('CHF_USD', get_time(), 1.0, 1.0)
        tick2 = TickEvent('CHF_USD', get_time(), 1.01, 1.02)
        events = queue.Queue()
        cost_predictor = FxSpreadCostEvaluator(events)
        events.put_nowait(tick1)
        events.put_nowait(tick2)
        cost_predictor.pull_process()
        self.assertEqual(cost_predictor.get_last_tick().instrument, tick2.instrument)
        self.assertEqual(cost_predictor.get_last_tick().bid, tick2.bid)
        self.assertEqual(cost_predictor.get_last_tick().ask, tick2.ask)

    def test_should_eval_cost_if_one_tick_available(self):
        tick = TickEvent('CHF_USD', get_time(), 1.01, 1.02)
        events = queue.Queue()
        events.put_nowait(tick)
        cost_predictor = FxSpreadCostEvaluator(events)
        cost_predictor.pull_process()
        order = OrderEvent(tick.instrument, 100, 'buy')
        cost = cost_predictor.eval_cost(order)
        self.assertEqual(0.01, cost)

    def test_should_eval_cost_if_two_ticks_available(self):
        tick1 = TickEvent('CHF_USD', get_time(), 1.01, 1.03)
        tick2 = TickEvent('CHF_USD', get_time(), 1.02, 1.03)
        events = queue.Queue()
        events.put_nowait(tick1)
        events.put_nowait(tick2)
        cost_predictor = FxSpreadCostEvaluator(events)
        cost_predictor.pull_process()
        order = OrderEvent(tick2.instrument, 100, 'buy')
        cost = cost_predictor.eval_cost(order)
        self.assertEqual(0.015, cost)

