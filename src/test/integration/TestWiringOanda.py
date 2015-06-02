import unittest
from queue import Queue, Empty
from threading import Thread
from time import sleep

from com.open.algo.journal import Journaler
from com.open.algo.wiring.wiring import *
from com.open.algo.oanda.environments import CONFIG_PATH_FOR_UNIT_TESTS


TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM = 4


class TestWirePricesStreamToCache(unittest.TestCase):
    def setUp(self):
        self.wiring = WireRateCache()
        self.wiring.set_rates_q(Queue()).set_forward_q(Queue()).set_journaler(Journaler())
        self.wiring.set_target_env('practice').set_config_path(CONFIG_PATH_FOR_UNIT_TESTS)

    def test_forwarded_rate_should_be_in_fx_cache(self):
        rates_streamer, rates_cache_loop = self.wiring.wire()

        rates_stream_thread = Thread(target=rates_streamer.stream)
        rates_cache_thread = Thread(target=rates_cache_loop.start)

        rates_stream_thread.start()
        rates_cache_thread.start()

        sleep(TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        rates_streamer.stop()
        rates_stream_thread.join(timeout=TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        rates_cache_loop.stop()
        rates_cache_thread.join(timeout=2*rates_cache_loop.heartbeat)

        tick = None
        try:
            while True:
                tick = self.wiring.forward_q.get_nowait()
        except Empty:
            pass
        self.assertIsNotNone(tick, 'rates q should have had at least one tick received by rates streamer, found None')
        try:
            rates = rates_cache_loop.handler.get_rate(tick.instrument)
            self.assertEqual(tick.bid, rates['bid'])
            self.assertEqual(tick.ask, rates['ask'])
        except KeyError:
            self.fail('expecting rates cache to provide rate corresponding to tick - [%s]' % tick)
        # end of wire test, but what to measure


from com.open.algo.trading.fxEvents import *
from com.open.algo.utils import get_time


class TestWirePortfolio(unittest.TestCase):
    def setUp(self):
        self.portfolio_q = Queue()
        self.execution_q = Queue()
        self.wiring = WirePortfolio()
        self.wiring.set_portfolio_q(self.portfolio_q).set_execution_q(self.execution_q)
        self.wiring.set_portfolio_ccy('USD').set_portfolio_balance(10000)
        self.wiring.set_portfolio_limit(500).set_portfolio_limit_short(-500)
        self.cache = FxPricesCache()
        self.wiring.set_prices_cache(self.cache)

    def test_signal_should_reach_execution_q(self):
        buy_order = OrderEvent('EUR_USD', 1000, 'buy')
        self.cache.set_rate(TickEvent('EUR_USD', get_time(), 1.0, 1.0))

        portfolio_loop = self.wiring.wire()
        portfolio_thread = Thread(target=portfolio_loop.start)

        portfolio_thread.start()
        self.portfolio_q.put_nowait(buy_order)
        sleep(2*portfolio_loop.heartbeat)
        portfolio_loop.stop()
        portfolio_thread.join(2*portfolio_loop.heartbeat)

        try:
            out_event = self.execution_q.get_nowait()
            self.assertEqual(buy_order, out_event)
        except Empty:
            self.fail('should have found one order in execution queue')


class TestWireExecutor(unittest.TestCase):
    def setUp(self):
        self.portfolio_q = Queue()
        self.execution_q = Queue()
        self.wiring = WireExecutor()
        self.wiring.set_portfolio_q(self.portfolio_q).set_execution_q(self.execution_q)
        self.wiring.set_target_env('practice').set_config_path(CONFIG_PATH_FOR_UNIT_TESTS)

    def test_executed_order_should_reach_portfolio_q(self):
        buy_order = OrderEvent('EUR_USD', 1000, 'buy')

        execution_loop = self.wiring.wire()
        execution_thread = Thread(target=execution_loop.start)
        execution_thread.start()
        self.execution_q.put_nowait(buy_order)
        sleep(TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        execution_loop.stop()
        execution_thread.join(timeout=2*execution_loop.heartbeat)

        try:
            executed_order = self.portfolio_q.get_nowait()
            self.assertEqual(buy_order, executed_order.order)
        except Empty:
            self.fail('should have sent executed order to portfolio q')
