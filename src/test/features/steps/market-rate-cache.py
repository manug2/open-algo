
from com.open.algo.trading.fxPricesCache import FxPricesCache
from com.open.algo.utils import EventLoop
from com.open.algo.model import gettime
from com.open.algo.trading.fxEvents import TickEvent

from queue import Queue
import threading
import time
from behave import *


@given('rates queue is initialized')
def step_impl(context):
    context.rates_events = Queue()


@given('market rate cache is listening to ticks')
def step_impl(context):
        context.looper = EventLoop(context.rates_events, context.rates_cache)
        context.price_thread = threading.Thread(target=context.looper.start, args=[])
        context.price_thread.start()


@when('market rate cache stops')
def step_impl(context):
        time.sleep(2*context.looper.heartbeat)
        context.looper.stop()
        context.price_thread.join(timeout=2*context.looper.heartbeat)


@when('a price tick arrives for {instrument} {bid}/{ask}')
def step_impl(context, instrument, bid, ask):
    context.rates_events.put(TickEvent(instrument, gettime(), float(bid), float(ask)))


@given('market rate cache is initialized')
def step_impl(context):
    context.rates_cache = FxPricesCache()


@given('market rate for {ccy} is {bid}/{ask} wrt {base_ccy}')
def step_impl(context, ccy, bid, ask, base_ccy):
    context.rates_cache.set_rate(TickEvent(ccy + '_' + base_ccy, gettime(), float(bid), float(ask)))
