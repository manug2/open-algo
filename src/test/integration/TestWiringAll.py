import unittest
from queue import Queue
from threading import Thread
from testUtils import *
from com.open.algo.wiring.wiring import *
from time import sleep
from com.open.algo.dummy import DummyBuyStrategy
from com.open.algo.journal import Journaler


class TestWireRatesStrategyPortfolioExecutor(unittest.TestCase):

    def setUp(self):
        self.rates_q = Queue()
        self.tick_and_ack_q = Queue()
        self.portfolio_q = Queue()
        self.execution_q = Queue()
        self.journaler = Journaler()

        self.everything = WireAll()
        self.everything.set_rates_q(self.rates_q).set_ticks_and_ack_q(self.tick_and_ack_q)
        self.everything.set_max_tick_age(24*60*60).set_journaler(self.journaler)
        self.everything.set_target_env('practice').set_config_path(CONFIG_PATH_FOR_UNIT_TESTS)

        self.everything.set_portfolio_q(self.portfolio_q).set_execution_q(self.execution_q)
        self.everything.port_wiring.set_portfolio_ccy('USD').set_portfolio_balance(10000)
        self.everything.port_wiring.set_portfolio_limit(50).set_portfolio_limit_short(-50)

        self.everything.set_strategy(DummyBuyStrategy(100))

        self.rates_streamer, self.rates_cache_loop, self.portfolio_loop, self.execution_loop, self.strategy_loop = \
            self.everything.wire()

        self.rates_stream_thread = Thread(target=self.rates_streamer.stream)
        self.rates_cache_thread = Thread(target=self.rates_cache_loop.start)
        self.portfolio_thread = Thread(target=self.portfolio_loop.start)
        self.execution_thread = Thread(target=self.execution_loop.start)
        self.strategy_thread = Thread(target=self.strategy_loop.start)

    def tearDown(self):
        self.execution_loop.stop()
        self.portfolio_loop.stop()
        self.strategy_loop.stop()
        self.rates_streamer.stop()
        self.rates_cache_loop.stop()

        self.execution_thread.join(timeout=2*self.execution_loop.heartbeat)
        self.portfolio_thread.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        self.strategy_thread.join(timeout=2*self.execution_loop.heartbeat)
        self.rates_stream_thread.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        self.rates_cache_thread.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)

    def test_wire_all(self):
        self.rates_stream_thread.start()
        self.rates_cache_thread.start()
        self.portfolio_thread.start()
        self.execution_thread.start()
        self.strategy_thread.start()

        sleep(MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
