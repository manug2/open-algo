import unittest

from testUtils import *
from com.open.algo.wiring.wiring import *
from com.open.algo.journal import Journaler


class TestWirePricesStream(unittest.TestCase):
    def setUp(self):
        self.rates_q = Queue()
        self.prices_wiring = WireOandaPrices()
        self.prices_wiring.set_rates_q(self.rates_q).set_journaler(Journaler())
        self.prices_wiring.set_target_env('practice').set_config_path(CONFIG_PATH_FOR_UNIT_TESTS)

    def test_forwarded_rate_should_be_in_fx_cache(self):
        rates_streamer = self.prices_wiring.wire()
        rates_stream_thread = Thread(target=rates_streamer.stream)
        rates_stream_thread.start()

        await_event_receipt(self, self.rates_q
                                   , 'did not get any rates forwarded by fx cache')
        rates_streamer.stop()
        rates_stream_thread.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        # end of wire test, but what to measure


class TestWirePricesStreamWithCommandListener(unittest.TestCase):
    def setUp(self):
        self.rates_q = Queue()
        self.prices_wiring = WireOandaPrices()
        self.prices_wiring.set_rates_q(self.rates_q).set_journaler(Journaler())
        self.prices_wiring.set_target_env('practice').set_config_path(CONFIG_PATH_FOR_UNIT_TESTS)

        self.command_q = Queue()
        self.prices_wiring.set_command_q(self.command_q)

    def test_forwarded_rate_should_be_in_fx_cache(self):
        rates_streamer, listener = self.prices_wiring.wire()
        rates_stream_thread = Thread(target=rates_streamer.stream)
        rates_stream_thread.start()
        listener_thread = listener.start_thread()

        await_event_receipt(self, self.rates_q
                                   , 'did not get any rates forwarded by fx cache')
        self.command_q.put_nowait(COMMAND_STOP)
        rates_stream_thread.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        listener_thread.join(timeout=1)
        # end of wire test, but what to measure


class TestWirePricesStreamToCache(unittest.TestCase):
    def setUp(self):
        self.prices_wiring = WireOandaPrices()
        self.prices_wiring.set_rates_q(Queue()).set_journaler(Journaler())
        self.prices_wiring.set_target_env('practice').set_config_path(CONFIG_PATH_FOR_UNIT_TESTS)

        self.rates_cache_wiring = WireRateCache()
        self.rates_cache_wiring.set_rates_q(self.prices_wiring.rates_q).set_forward_q(Queue())
        self.rates_cache_wiring.set_max_tick_age(2*24*60*60)

    def test_forwarded_rate_should_be_in_fx_cache(self):
        rates_streamer = self.prices_wiring.wire()
        rates_cache_loop = self.rates_cache_wiring.wire()

        rates_stream_thread = Thread(target=rates_streamer.stream)
        rates_cache_thread = Thread(target=rates_cache_loop.start)

        rates_stream_thread.start()
        rates_cache_thread.start()

        tick = await_event_receipt(self, self.rates_cache_wiring.forward_q
                                   , 'did not get any rates forwarded by fx cache')
        rates_streamer.stop()
        rates_cache_loop.stop()
        rates_stream_thread.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        rates_cache_thread.join(timeout=1)

        try:
            rates = rates_cache_loop.handler.get_rate(tick.instrument)
            print(rates)
            self.assertEqual(tick.bid, rates['bid'])
            self.assertEqual(tick.ask, rates['ask'])
        except KeyError:
            self.fail('expecting rates cache to provide rate corresponding to tick - [%s]' % tick)
        # end of wire test, but what to measure


class TestWirePricesStreamToCacheWithCommandListener(unittest.TestCase):
    def setUp(self):
        self.command_q_streamer = Queue()
        self.command_q_cache = Queue()
        self.spmc_command_q = QueueSPMC(Journaler())
        self.spmc_command_q.add_consumer(self.command_q_streamer)
        self.spmc_command_q.add_consumer(self.command_q_cache)

        self.prices_wiring = WireOandaPrices()
        self.prices_wiring.set_rates_q(Queue()).set_journaler(Journaler())
        self.prices_wiring.set_target_env('practice').set_config_path(CONFIG_PATH_FOR_UNIT_TESTS)

        self.rates_cache_wiring = WireRateCache()
        self.rates_cache_wiring.set_rates_q(self.prices_wiring.rates_q).set_forward_q(Queue())
        self.rates_cache_wiring.set_max_tick_age(2*24*60*60)

    def test_forwarded_rate_should_be_in_fx_cache(self):
        self.prices_wiring.set_command_q(self.command_q_streamer)
        rates_streamer, rates_command_listener = self.prices_wiring.wire()
        self.rates_cache_wiring.set_command_q(self.command_q_cache)
        rates_cache_loop = self.rates_cache_wiring.wire()

        rates_stream_thread = Thread(target=rates_streamer.stream)
        rates_cache_thread = Thread(target=rates_cache_loop.start)

        rates_stream_thread.start()
        rates_command_listener_thread = rates_command_listener.start_thread()
        rates_cache_thread.start()
        rates_cache_listener_thread = rates_cache_loop.listener.start_thread()

        tick = await_event_receipt(self, self.rates_cache_wiring.forward_q
                                   , 'did not get any rates forwarded by fx cache')

        self.spmc_command_q.put_nowait(COMMAND_STOP)
        rates_stream_thread.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        rates_command_listener_thread.join(timeout=1)
        rates_cache_thread.join(timeout=1)
        rates_cache_listener_thread.join(timeout=1)

        try:
            rates = rates_cache_loop.handler.get_rate(tick.instrument)
            print(rates)
            self.assertEqual(tick.bid, rates['bid'])
            self.assertEqual(tick.ask, rates['ask'])
        except KeyError:
            self.fail('expecting rates cache to provide rate corresponding to tick - [%s]' % tick)
        # end of wire test, but what to measure

    def test_when_using_starter_forwarded_rate_should_be_in_fx_cache(self):
        starter = ThreadStarter()
        starter.add_target(self.prices_wiring, self.command_q_streamer)\
            .add_target(self.rates_cache_wiring, self.command_q_cache)

        starter.start()

        tick = await_event_receipt(self, self.rates_cache_wiring.forward_q
                                   , 'did not get any rates forwarded by fx cache')

        self.spmc_command_q.put_nowait(COMMAND_STOP)
        starter.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)

        try:
            rates = self.rates_cache_wiring.component.get_rate(tick.instrument)
            print(rates)
            self.assertEqual(tick.bid, rates['bid'])
            self.assertEqual(tick.ask, rates['ask'])
        except KeyError:
            self.fail('expecting rates cache to provide rate corresponding to tick - [%s]' % tick)
        # end of wire test, but what to measure


from com.open.algo.trading.fxEvents import *
from com.open.algo.utils import get_day_of_week
from com.open.algo.model import ExceptionEvent


class TestWireExecutor(unittest.TestCase):
    def setUp(self):
        self.portfolio_q = Queue()
        self.execution_q = Queue()
        self.wiring = WireExecutor().set_journaler(Journaler())
        self.wiring.set_execution_result_q(self.portfolio_q).set_execution_q(self.execution_q)
        self.wiring.set_target_env('practice').set_config_path(CONFIG_PATH_FOR_UNIT_TESTS)

    def test_executed_order_should_reach_portfolio_q(self):
        buy_order = OrderEvent('EUR_USD', 1000, 'buy')

        execution_loop = self.wiring.wire()
        execution_thread = Thread(target=execution_loop.start)
        execution_thread.start()
        self.execution_q.put_nowait(buy_order)
        executed_order = await_event_receipt(self, self.portfolio_q, 'did not find one order in portfolio queue')
        execution_loop.stop()
        execution_thread.join(timeout=2*execution_loop.heartbeat)

        if get_day_of_week() >= 5:
            self.assertIsInstance(executed_order, ExceptionEvent)
        else:
            self.assertIsInstance(executed_order, ExecutedOrder
                      , 'expecting an executed order of type [%s] but got of type [%s] - %s'
                          % (type(ExecutedOrder), type(executed_order), executed_order))
            self.assertEqual(buy_order, executed_order.order)


from com.open.algo.utils import COMMAND_STOP
from com.open.algo.wiring.starter import ThreadStarter


class TestWireExecutorWithCommandListener(unittest.TestCase):
    def setUp(self):
        self.portfolio_q = Queue()
        self.execution_q = Queue()
        self.wiring = WireExecutor().set_journaler(Journaler())
        self.wiring.set_execution_result_q(self.portfolio_q).set_execution_q(self.execution_q)
        self.wiring.set_target_env('practice').set_config_path(CONFIG_PATH_FOR_UNIT_TESTS)

        self.command_q = Queue()

    def test_using_threads_executed_order_should_reach_portfolio_q(self):
        buy_order = OrderEvent('EUR_USD', 1000, 'buy')

        self.wiring.set_command_q(self.command_q)
        execution_loop = self.wiring.wire()
        t1 = Thread(target=execution_loop.start)
        t2 = Thread(target=execution_loop.listener.start)

        t1.start()
        t2.start()

        self.execution_q.put_nowait(buy_order)
        executed_order = await_event_receipt(self, self.portfolio_q, 'did not find one order in portfolio queue')

        self.command_q.put_nowait(COMMAND_STOP)
        t1.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        t2.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)

        if get_day_of_week() >= 5:
            self.assertIsInstance(executed_order, ExceptionEvent)
        else:
            self.assertIsInstance(executed_order, ExecutedOrder
                      , 'expecting an executed order of type [%s] but got of type [%s] - %s'
                          % (type(ExecutedOrder), type(executed_order), executed_order))
            self.assertEqual(buy_order, executed_order.order)

    def test_using_starter_executed_order_should_reach_portfolio_q(self):
        buy_order = OrderEvent('EUR_USD', 1000, 'buy')

        starter = ThreadStarter()
        starter.add_target(self.wiring, self.command_q)
        starter.start()

        self.execution_q.put_nowait(buy_order)
        executed_order = await_event_receipt(self, self.portfolio_q, 'did not find one order in portfolio queue')

        self.command_q.put_nowait(COMMAND_STOP)
        starter.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)

        if get_day_of_week() >= 5:
            self.assertIsInstance(executed_order, ExceptionEvent)
        else:
            self.assertIsInstance(executed_order, ExecutedOrder
                      , 'expecting an executed order of type [%s] but got of type [%s] - %s'
                          % (type(ExecutedOrder), type(executed_order), executed_order))
            self.assertEqual(buy_order, executed_order.order)

