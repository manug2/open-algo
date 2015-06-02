__author__ = 'ManuGarg'

import sys
from queue import Queue

sys.path.append('../../main')
import unittest
from com.open.algo.trading.fxCostPredictor import FxSpreadCostEvaluator
from com.open.algo.trading.fxEvents import *
from com.open.algo.utils import get_time
from com.open.algo.wiring.eventLoop import EventLoop


class TestCostPrediction(unittest.TestCase):

    def setUp(self):
        self.events = Queue()
        self.cost_predictor = FxSpreadCostEvaluator(self.events)
        self.looper = EventLoop(self.events, self.cost_predictor)
        self.looper.started = True

    def test_should_be_able_to_pull_one_tick_from_event_queue(self):
        tick = TickEvent('CHF_USD', get_time(), 1.0, 1.0)
        self.events.put_nowait(tick)
        self.looper.pull_process()
        self.assertEqual(self.cost_predictor.get_last_tick(), tick)

    def test_should_not_eval_cost_if_no_tick(self):
        order = OrderEvent('CHF_USD', 100, 'buy')
        try:
            self.cost_predictor.eval_cost(order)
            self.fail('should have given error as np tick is present')
        except KeyError:
            pass

    def test_should_not_eval_cost_if_no_tick_for_specific_instrument(self):
        tick = TickEvent('CHF_USD', get_time(), 1.0, 1.0)
        self.events.put_nowait(tick)
        self.looper.pull_process()
        order = OrderEvent('EUR_USD', 100, 'buy')
        try:
            self.cost_predictor.eval_cost(order)
            self.fail('should have given error as no tick for [%s] is present' % order.instrument)
        except KeyError:
            pass

    def test_should_eval_cost_if_tick_available(self):
        tick = TickEvent('CHF_USD', get_time(), 1.01, 1.02)
        self.events.put_nowait(tick)
        self.looper.pull_process()
        order = OrderEvent(tick.instrument, 100, 'buy')
        cost = self.cost_predictor.eval_cost(order)
        self.assertEqual(0.01, cost)
