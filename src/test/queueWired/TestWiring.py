
import unittest
from testUtils import *
from com.open.algo.wiring.wiring import *
from com.open.algo.dummy import DummyBuyStrategy
from com.open.algo.oanda.parser import parse_event_str

TICK_MAX_AGE = 365*24*60*60
TICK_STRING = \
    '{"tick": {"instrument": "EUR_USD", "time": "2015-07-21T20:59:45.031348Z", "bid": 1.11975, "ask": 1.12089}}'


class TestWirePricesCache(unittest.TestCase):
    def setUp(self):
        self.rates_q = Queue()
        self.tick = parse_event_str(None, TICK_STRING)
        self.forward_q = Queue()

        self.rates_cache_wiring = WireRateCache()
        self.rates_cache_wiring.set_max_tick_age(TICK_MAX_AGE)

    def test_forwarded_rate_should_be_in_fx_cache(self):
        rates_cache_loop = self.rates_cache_wiring.wire(in_q=self.rates_q, out_q=self.forward_q)
        rates_cache_thread = Thread(target=rates_cache_loop.start)
        rates_cache_thread.start()

        self.rates_q.put_nowait(self.tick)
        await_event_receipt(self, self.forward_q, 'did not find one order in cache forward queue')

        rates_cache_loop.stop()
        rates_cache_thread.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)

        try:
            rates = rates_cache_loop.handler.get_rate(self.tick.instrument)
            print(rates)
            self.assertEqual(self.tick.bid, rates['bid'])
            self.assertEqual(self.tick.ask, rates['ask'])
        except KeyError:
            self.fail('expecting rates cache to provide rate corresponding to tick - [%s]' % self.tick)
        # end of wire test, but what to measure


from com.open.algo.trading.fxEvents import *
from com.open.algo.utils import get_time, get_day_of_week


class TestWirePortfolio(unittest.TestCase):
    def setUp(self):
        self.portfolio_q = Queue()
        self.execution_q = Queue()
        self.wiring = WirePortfolio()
        self.wiring.set_portfolio_ccy('USD').set_portfolio_balance(10000)
        self.wiring.set_portfolio_limit(500).set_portfolio_limit_short(-500)
        self.cache = FxPricesCache()
        self.wiring.set_prices_cache(self.cache)

    def test_signal_should_reach_execution_q(self):
        buy_order = OrderEvent('EUR_USD', 1000, 'buy')
        self.cache.set_rate(TickEvent('EUR_USD', get_time(), 1.0, 1.0))

        portfolio_loop = self.wiring.wire(in_q=self.portfolio_q, out_q=self.execution_q)
        portfolio_thread = Thread(target=portfolio_loop.start)

        portfolio_thread.start()
        self.portfolio_q.put_nowait(buy_order)
        out_event = await_event_receipt(self, self.execution_q, 'did not find one order in execution queue')
        portfolio_loop.stop()
        portfolio_thread.join(2*portfolio_loop.heartbeat)
        self.assertEqual(buy_order, out_event)


class TestWireDummyBuyStrategy(unittest.TestCase):
    def setUp(self):
        self.rates_q = Queue()
        self.tick = parse_event_str(None, TICK_STRING)

        self.tick_for_strategy_q = Queue()
        self.signal_output_q = Queue()

        self.strategy_wiring = WireStrategy().set_strategy(DummyBuyStrategy(), 100)
        self.strategy_loop = self.strategy_wiring.wire(in_q=self.tick_for_strategy_q, out_q=self.signal_output_q)
        self.strategy_thread = Thread(target=self.strategy_loop.start)

        self.rates_cache_wiring = WireRateCache()
        self.rates_cache_wiring.set_max_tick_age(TICK_MAX_AGE)
        self.rates_cache_loop = self.rates_cache_wiring.wire(in_q=self.rates_q, out_q=self.tick_for_strategy_q)

        self.rates_cache_thread = Thread(target=self.rates_cache_loop.start)

    def tearDown(self):
        self.rates_cache_loop.stop()
        self.strategy_loop.stop()

        self.rates_cache_thread.join(MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        self.strategy_thread.join(MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)

    def test_should_produce_order_when_started(self):
        self.rates_cache_thread.start()
        self.strategy_thread.start()

        self.rates_q.put_nowait(self.tick)
        signal = await_event_receipt(self, self.signal_output_q, 'should have received a signal from strategy')
        self.assertIsNotNone(signal)
        self.assertIsInstance(signal, OrderEvent)

