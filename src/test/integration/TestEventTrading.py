import unittest

from com.open.algo.trading.eventTrading import AlgoTrader
from com.open.algo.trading.fxEvents import *
from com.open.algo.eventLoop import EventLoop, Journaler
from com.open.algo.dummy import *
from queue import Queue
from com.open.algo.utils import get_time, EVENT_TYPES_ORDER

from com.open.algo.trading.fxPricesCache import FxPricesCache
from threading import Thread
from com.open.algo.oanda.environments import ENVIRONMENTS, CONFIG_PATH_FOR_UNIT_TESTS
from com.open.algo.utils import read_settings
from com.open.algo.oanda.streaming import StreamingForexPrices
from time import sleep
TARGET_ENV = "practice"
OUTPUT_DIR = '../output/'
TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM = 4


class TestStreamTrading(unittest.TestCase):
    def setUp(self):
        self.events = Queue()
        self.execution_q = Queue()
        self.strategy = DummyBuyStrategy(100)
        self.executor = DummyExecutor()
        self.algo_trader = AlgoTrader(None, self.strategy, self.executor)
        self.trader = EventLoop(self.events, self.algo_trader)
        self.trader.started = True

    def test_wire_fx_cache(self):
        rates_q = Queue()

        journaler = Journaler()
        domain = ENVIRONMENTS['streaming'][TARGET_ENV]
        settings = read_settings(CONFIG_PATH_FOR_UNIT_TESTS, TARGET_ENV)

        rates_streamer = StreamingForexPrices(
            domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID'],
            'EUR_USD', rates_q, None, journaler)
        rates_stream_thread = Thread(target=rates_streamer.stream)

        rates_cache = FxPricesCache()
        rates_cache_loop = EventLoop(rates_q, rates_cache)
        rates_cache_thread = Thread(target=rates_cache_loop.start)

        rates_stream_thread.start()
        rates_cache_thread.start()

        sleep(TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        rates_streamer.stop()
        rates_stream_thread.join(timeout=TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM)
        rates_cache_loop.stop()
        rates_cache_thread.join(timeout=2*rates_cache_loop.heartbeat)
        # end of wire test, but what to measure
