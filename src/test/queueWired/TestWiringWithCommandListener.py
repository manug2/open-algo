import unittest

from testUtils import *
from com.open.algo.wiring.wiring import *
from com.open.algo.dummy import DummyBuyStrategy
from com.open.algo.journal import Journaler
from com.open.algo.oanda.parser import parse_event_str
from com.open.algo.utils import COMMAND_STOP
from com.open.algo.wiring.starter import ThreadStarter

TICK_MAX_AGE = 365*24*60*60
TICK_STRING = \
    '{"tick": {"instrument": "EUR_USD", "time": "2015-07-21T20:59:45.031348Z", "bid": 1.11975, "ask": 1.12089}}'


class TestWirePricesCache(unittest.TestCase):
    def setUp(self):
        self.starter = ThreadStarter()
        self.rates_q = Queue()
        self.tick = parse_event_str(None, TICK_STRING)
        self.forward_q = Queue()

        self.rates_cache_wiring = WireRateCache()
        self.rates_cache_wiring.set_max_tick_age(TICK_MAX_AGE)

        self.command_q = Queue()

    def test_forwarded_rate_should_be_in_fx_cache(self):
        self.starter.add_target(self.rates_cache_wiring, self.command_q, in_q=self.rates_q, out_q=self.forward_q)
        self.starter.start()

        self.rates_q.put_nowait(self.tick)
        await_event_receipt(self, self.forward_q, 'did not find one order in cache forward queue')

        self.command_q.put_nowait(COMMAND_STOP)
        self.starter.join()

        try:
            rates = self.rates_cache_wiring.component.get_rate(self.tick.instrument)
            print(rates)
            self.assertEqual(self.tick.bid, rates['bid'])
            self.assertEqual(self.tick.ask, rates['ask'])
        except KeyError:
            self.fail('expecting rates cache to provide rate corresponding to tick - [%s]' % self.tick)
        # end of wire test, but what to measure


from com.open.algo.trading.fxEvents import *
from com.open.algo.utils import get_time, get_day_of_week
from com.open.algo.model import ExceptionEvent


class TestWirePortfolio(unittest.TestCase):
    def setUp(self):
        self.starter = ThreadStarter()
        self.portfolio_q = Queue()
        self.execution_q = Queue()
        self.wiring = WirePortfolio()
        self.wiring.set_portfolio_ccy('USD').set_portfolio_balance(10000)
        self.wiring.set_portfolio_limit(500).set_portfolio_limit_short(-500)
        self.cache = FxPricesCache()
        self.wiring.set_prices_cache(self.cache)

        self.command_q = Queue()

    def test_signal_should_reach_execution_q(self):
        buy_order = OrderEvent('EUR_USD', 1000, 'buy')
        self.cache.set_rate(TickEvent('EUR_USD', get_time(), 1.0, 1.0))

        self.starter.add_target(self.wiring, command_q=self.command_q, in_q=self.portfolio_q, out_q=self.execution_q)
        self.starter.start()

        self.portfolio_q.put_nowait(buy_order)
        out_event = await_event_receipt(self, self.execution_q, 'did not find one order in execution queue')

        self.command_q.put_nowait(COMMAND_STOP)
        self.starter.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        self.assertEqual(buy_order, out_event)


class TestWireDummyBuyStrategy(unittest.TestCase):
    def setUp(self):
        self.starter = ThreadStarter()
        self.tick = parse_event_str(None, TICK_STRING)

        self.rates_q = Queue()
        self.tick_for_strategy_q = Queue()
        self.signal_output_q = Queue()

        self.strategy_wiring = WireStrategy().set_strategy(DummyBuyStrategy(), 100)
        command_q_strategy = Queue()
        self.starter.add_target(self.strategy_wiring,
                                command_q_strategy, self.tick_for_strategy_q, self.signal_output_q)

        self.rates_cache_wiring = WireRateCache().set_max_tick_age(TICK_MAX_AGE)
        command_q_rates = Queue()
        self.starter.add_target(self.rates_cache_wiring, command_q_rates, self.rates_q, self.tick_for_strategy_q)

        self.command_q = QueueSPMC(Journaler())
        self.command_q.add_consumer(command_q_rates).add_consumer(command_q_strategy)

    def test_should_produce_order_when_started(self):
        self.starter.start()

        self.rates_q.put_nowait(self.tick)
        signal = await_event_receipt(self, self.signal_output_q, 'should have received a signal from strategy')
        self.command_q.put_nowait(COMMAND_STOP)
        self.starter.join(timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)

        self.assertIsNotNone(signal)
        self.assertIsInstance(signal, OrderEvent)
