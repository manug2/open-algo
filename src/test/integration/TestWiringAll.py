import unittest
from time import sleep

from testUtils import *
from com.open.algo.wiring.wiring import *
from com.open.algo.dummy import DummyBuyStrategy
from com.open.algo.journal import Journaler
from com.open.algo.utils import COMMAND_STOP


class TestWireRatesStrategyPortfolioExecutor(unittest.TestCase):

    def setUp(self):
        self.rates_q = Queue()
        self.tick_and_ack_q = Queue()
        self.portfolio_q = Queue()
        self.execution_q = Queue()
        self.journaler = Journaler()

        self.everything = WireAll()
        self.everything.set_max_tick_age(24*60*60).set_journaler(self.journaler)
        self.everything.set_target_env('practice').set_config_path(CONFIG_PATH_FOR_UNIT_TESTS)

        self.everything.port_wiring.set_portfolio_ccy('USD').set_portfolio_balance(10000)
        self.everything.port_wiring.set_portfolio_limit(50).set_portfolio_limit_short(-50)

        self.everything.set_strategy(DummyBuyStrategy(100))
        self.logger = wire_logger()

    def test_wire_all(self):
        rates_streamer, rates_cache_loop, portfolio_loop, execution_loop, strategy_loop = \
            self.everything.wire()

        rates_stream_thread = Thread(target=rates_streamer.stream)
        rates_cache_thread = Thread(target=rates_cache_loop.start)
        portfolio_thread = Thread(target=portfolio_loop.start)
        execution_thread = Thread(target=execution_loop.start)
        strategy_thread = Thread(target=strategy_loop.start)
        try:
            rates_stream_thread.start()
            rates_cache_thread.start()
            portfolio_thread.start()
            execution_thread.start()
            strategy_thread.start()

            sleep(MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        except RuntimeError as e:
            self.logger.error('error starting all components', e)
        except:
            self.logger.error('error starting all components')
        try:
            execution_loop.stop()
            portfolio_loop.stop()
            strategy_loop.stop()
            rates_streamer.stop()
            rates_cache_loop.stop()
        except:
            self.logger.info('error stopping all components')
        finally:
            execution_thread.join(timeout=2*execution_loop.heartbeat)
            portfolio_thread.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
            strategy_thread.join(timeout=2*execution_loop.heartbeat)
            rates_stream_thread.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
            rates_cache_thread.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)

    def test_wire_all_with_command_listener(self):
        command_q_for_cloning = Queue()
        command_q = QueueSPMC(Journaler())

        rates_streamer, rates_command_listener, rates_cache_loop, portfolio_loop, execution_loop, strategy_loop = \
            self.everything.wire(command_q=command_q, in_q=command_q_for_cloning)

        rates_stream_thread = Thread(target=rates_streamer.stream)
        rates_cache_thread = Thread(target=rates_cache_loop.start)
        portfolio_thread = Thread(target=portfolio_loop.start)
        execution_thread = Thread(target=execution_loop.start)
        strategy_thread = Thread(target=strategy_loop.start)

        rates_command_listener_thread = None
        t1 = None
        t2 = None
        t3 = None
        t4 = None

        try:
            rates_stream_thread.start()
            rates_cache_thread.start()
            portfolio_thread.start()
            execution_thread.start()
            strategy_thread.start()
            rates_command_listener_thread = rates_command_listener.start_thread()
            t1 = rates_cache_loop.listener.start_thread()
            t2 = portfolio_loop.listener.start_thread()
            t3 = execution_loop.listener.start_thread()
            t4 = strategy_loop.listener.start_thread()

            sleep(MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        except RuntimeError as e:
            self.logger.error('error starting all components', e)
        except:
            self.logger.error('error starting all components')

        command_q.put_nowait(COMMAND_STOP)

        execution_thread.join(timeout=2*execution_loop.heartbeat)
        portfolio_thread.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        strategy_thread.join(timeout=2*execution_loop.heartbeat)
        rates_stream_thread.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        rates_cache_thread.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)

        rates_command_listener_thread.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        t1.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        t2.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        t3.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        t4.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)


class TestCommandQueueWiring(unittest.TestCase):

    def setUp(self):
        self.journaler = Journaler()

        self.everything = WireAll()
        self.everything.set_max_tick_age(24*60*60).set_journaler(self.journaler)
        self.everything.set_target_env('practice').set_config_path(CONFIG_PATH_FOR_UNIT_TESTS)

        self.everything.port_wiring.set_portfolio_ccy('USD').set_portfolio_balance(10000)
        self.everything.port_wiring.set_portfolio_limit(50).set_portfolio_limit_short(-50)

        self.everything.set_strategy(DummyBuyStrategy(100))
        wire_logger()
        self.command_q_for_cloning = Queue()
        self.command_q = QueueSPMC(Journaler())

    def test_should_wire_components_with_cloned_command_q_for_listening(self):
        rates_streamer, rates_command_listener, rates_cache_loop, portfolio_loop, execution_loop, strategy_loop = \
            self.everything.wire(command_q=self.command_q, in_q=self.command_q_for_cloning)

        self.assertIsNotNone(rates_cache_loop.command_q)
        self.assertIsNotNone(portfolio_loop.command_q)
        self.assertIsNotNone(execution_loop.command_q)
        self.assertIsNotNone(strategy_loop.command_q)

    def test_should_have_cloned_command_queues_not_equal_to_original_q(self):
        rates_streamer, rates_command_listener, rates_cache_loop, portfolio_loop, execution_loop, strategy_loop = \
            self.everything.wire(command_q=self.command_q, in_q=self.command_q_for_cloning)

        self.assertNotEqual(self.command_q_for_cloning, rates_cache_loop.command_q)
        self.assertNotEqual(self.command_q_for_cloning, portfolio_loop.command_q)
        self.assertNotEqual(self.command_q_for_cloning, execution_loop.command_q)
        self.assertNotEqual(self.command_q_for_cloning, strategy_loop.command_q)

    def test_spmc_command_q_should_have_cloned_queues_as_consumers(self):
        rates_streamer, rates_command_listener, rates_cache_loop, portfolio_loop, execution_loop, strategy_loop = \
            self.everything.wire(command_q=self.command_q, in_q=self.command_q_for_cloning)

        self.assertTrue(rates_command_listener.command_q in self.command_q.consumer_queues)
        self.assertTrue(rates_cache_loop.command_q in self.command_q.consumer_queues)
        self.assertTrue(portfolio_loop.command_q in self.command_q.consumer_queues)
        self.assertTrue(execution_loop.command_q in self.command_q.consumer_queues)
        self.assertTrue(strategy_loop.command_q in self.command_q.consumer_queues)
