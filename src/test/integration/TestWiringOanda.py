import unittest
from testUtils import *
from com.open.algo.wiring.wiring import *
from com.open.algo.dummy import DummyBuyStrategy
from com.open.algo.journal import Journaler


class TestWirePricesStreamToCache(unittest.TestCase):
    def setUp(self):
        self.wiring = WireRateCache()
        self.wiring.set_rates_q(Queue()).set_forward_q(Queue()).set_journaler(Journaler())
        self.wiring.set_target_env('practice').set_config_path(CONFIG_PATH_FOR_UNIT_TESTS)
        self.wiring.set_max_tick_age(2*24*60*60)

    def test_forwarded_rate_should_be_in_fx_cache(self):
        rates_streamer, rates_cache_loop = self.wiring.wire()

        rates_stream_thread = Thread(target=rates_streamer.stream)
        rates_cache_thread = Thread(target=rates_cache_loop.start)

        rates_stream_thread.start()
        rates_cache_thread.start()

        tick = await_event_receipt(self, self.wiring.forward_q, 'did not get any rates forwarded by fx cache')
        rates_streamer.stop()
        rates_cache_loop.stop()
        rates_stream_thread.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        rates_cache_thread.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)

        try:
            rates = rates_cache_loop.handler.get_rate(tick.instrument)
            print(rates)
            self.assertEqual(tick.bid, rates['bid'])
            self.assertEqual(tick.ask, rates['ask'])
        except KeyError:
            self.fail('expecting rates cache to provide rate corresponding to tick - [%s]' % tick)
        # end of wire test, but what to measure


from com.open.algo.trading.fxEvents import *
from com.open.algo.utils import get_time, get_day_of_week
from com.open.algo.model import ExceptionEvent


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
        out_event = await_event_receipt(self, self.execution_q, 'did not find one order in execution queue')
        portfolio_loop.stop()
        portfolio_thread.join(2*portfolio_loop.heartbeat)
        self.assertEqual(buy_order, out_event)


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

        if get_day_of_week() == 6:
            self.assertIsInstance(executed_order, ExceptionEvent)
        else:
            self.assertIsInstance(executed_order, ExecutedOrder
                      , 'expecting an executed order of type [%s] but got of type [%s] - %s'
                          % (type(ExecutedOrder), type(executed_order), executed_order))
            self.assertEqual(buy_order, executed_order.order)


class TestWireDummyBuyStrategy(unittest.TestCase):
    def setUp(self):
        self.tick_for_strategy_q = Queue()
        self.signal_output_q = Queue()

        self.strategy_wiring = WireStrategy().set_strategy(DummyBuyStrategy(100))
        self.strategy_wiring.set_signal_output_q(self.signal_output_q).set_ticks_and_ack_q(self.tick_for_strategy_q)
        self.strategy_loop = self.strategy_wiring.wire()
        self.strategy_thread = Thread(target=self.strategy_loop.start)

        self.rates_wiring = WireRateCache()
        self.rates_wiring.set_rates_q(Queue()).set_forward_q(self.tick_for_strategy_q).set_journaler(Journaler())
        self.rates_wiring.set_target_env('practice').set_config_path(CONFIG_PATH_FOR_UNIT_TESTS)
        self.rates_wiring.set_max_tick_age(24*60*60)

        self.streamer, self.rates_cache_loop = self.rates_wiring.wire()
        self.streaming_thread = Thread(target=self.streamer.stream, args=[])
        self.rates_cache_thread = Thread(target=self.rates_cache_loop.start)

    def tearDown(self):
        self.streamer.stop()
        self.rates_cache_loop.stop()
        self.strategy_loop.stop()

        self.streaming_thread.join(MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        self.rates_cache_thread.join(MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        self.strategy_thread.join(MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)

    def test_should_produce_order_when_started(self):
        self.streaming_thread.start()
        self.rates_cache_thread.start()
        self.strategy_thread.start()

        signal = await_event_receipt(self, self.signal_output_q, 'should have received a signal from strategy')
        self.assertIsNotNone(signal)
        self.assertIsInstance(signal, OrderEvent)

