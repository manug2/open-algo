import unittest
from queue import Queue
from threading import Thread
from testUtils import *
from com.open.algo.wiring.wiring import *
from time import sleep
from com.open.algo.dummy import DummyBuyStrategy
from com.open.algo.journal import Journaler
from com.open.algo.wiring.commandListener import COMMAND_STOP


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
        from com.open.algo.starter import ThreadStarter

        starter = ThreadStarter(self.__class__.__name__)
        command_q_for_cloning = Queue()
        command_q = QueueSPMC(Journaler())
        self.everything.set_command_q(command_q, command_q_for_cloning)

        rates_streamer, rates_command_listener, rates_cache_loop, portfolio_loop, execution_loop, strategy_loop = \
            self.everything.wire()

        starter.add_target(rates_streamer.stream).add_target(rates_command_listener.listen)
        starter.add_target(rates_cache_loop.start).add_target(rates_cache_loop.listener.listen)
        starter.add_target(portfolio_loop.start).add_target(portfolio_loop.listener.listen)
        starter.add_target(execution_loop.start).add_target(execution_loop.listener.listen)
        starter.add_target(strategy_loop.start).add_target(strategy_loop.listener.listen)

        try:
            starter.start()

            sleep(MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        except RuntimeError as e:
            print('error starting all components')
            print(e)
        except:
            print('error starting all components')
        finally:

            command_q.put_nowait(COMMAND_STOP)

            starter.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)


class TestCommandQueueWiring(unittest.TestCase):

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
        wire_logger()
        self.command_q_for_cloning = Queue()
        self.command_q = QueueSPMC(Journaler())
        self.everything.set_command_q(self.command_q, self.command_q_for_cloning)

    def test_should_wire_components_with_cloned_command_q_for_listening(self):
        rates_streamer, rates_command_listener, rates_cache_loop, portfolio_loop, execution_loop, strategy_loop = \
            self.everything.wire()

        self.assertIsNotNone(rates_cache_loop.command_q)
        self.assertIsNotNone(portfolio_loop.command_q)
        self.assertIsNotNone(execution_loop.command_q)
        self.assertIsNotNone(strategy_loop.command_q)

    def test_should_have_cloned_command_queues_not_equal_to_original_q(self):
        rates_streamer, rates_command_listener, rates_cache_loop, portfolio_loop, execution_loop, strategy_loop = \
            self.everything.wire()

        self.assertNotEqual(self.command_q_for_cloning, rates_cache_loop.command_q)
        self.assertNotEqual(self.command_q_for_cloning, portfolio_loop.command_q)
        self.assertNotEqual(self.command_q_for_cloning, execution_loop.command_q)
        self.assertNotEqual(self.command_q_for_cloning, strategy_loop.command_q)

    def test_spmc_command_q_should_have_cloned_queues_as_consumers(self):
        rates_streamer, rates_command_listener, rates_cache_loop, portfolio_loop, execution_loop, strategy_loop = \
            self.everything.wire()

        self.assertTrue(rates_command_listener.command_q in self.command_q.consumer_queues)
        self.assertTrue(rates_cache_loop.command_q in self.command_q.consumer_queues)
        self.assertTrue(portfolio_loop.command_q in self.command_q.consumer_queues)
        self.assertTrue(execution_loop.command_q in self.command_q.consumer_queues)
        self.assertTrue(strategy_loop.command_q in self.command_q.consumer_queues)
