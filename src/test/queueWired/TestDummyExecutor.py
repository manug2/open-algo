import sys

sys.path.append('../../main')
import unittest

from com.open.algo.dummy import DummyExecutor
from com.open.algo.trading.fxEvents import *
from com.open.algo.wiring.eventLoop import *
from queue import Queue, Empty
from threading import Thread


class TestDummyExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = DummyExecutor()
        self.buy_order = OrderEvent('EUR_USD', 1000, ORDER_SIDE_BUY)
        self.executed_order = ExecutedOrder(self.buy_order, 1.0, self.buy_order.units)

    def test_should_have_executed_order_in_portfolio_q(self):
        execution_q = Queue()
        portfolio_q = Queue()
        execution_loop = EventLoop(execution_q, self.executor, processed_event_q=portfolio_q)
        execution_thread = Thread(target=execution_loop.start)
        execution_thread.start()
        execution_q.put_nowait(self.buy_order)
        sleep(2*execution_loop.heartbeat)
        execution_loop.stop()
        execution_thread.join(timeout=2*execution_loop.heartbeat)

        try:
            executed_order = portfolio_q.get_nowait()
            self.assertEquals(self.buy_order, executed_order.order)
            self.assertEquals(self.executed_order, executed_order)
        except Empty:
            self.fail('should have one event in portfolio queue as response from executor')