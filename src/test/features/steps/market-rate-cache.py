
from com.open.algo.trading.fxPricesCache import FxPricesCache
from com.open.algo.utils import get_time
from com.open.algo.eventLoop import EventLoop
from com.open.algo.trading.fxEvents import TickEvent
from com.open.algo.model import ExceptionEvent

from queue import Queue, Empty
import threading
import time
from behave import *


@given('rates queue is initialized')
def step_impl(context):
    context.rates_events = Queue()
    context.exception_q = Queue()


@given('market rate cache is listening to ticks')
def step_impl(context):
        context.looper = EventLoop(context.rates_events, context.rates_cache, exceptions_q=context.exception_q)
        context.price_thread = threading.Thread(target=context.looper.start, args=[])
        context.price_thread.start()


@when('market rate cache stops')
def step_impl(context):
        time.sleep(2*context.looper.heartbeat)
        context.looper.stop()
        context.price_thread.join(timeout=2*context.looper.heartbeat)


@when('a price tick arrives for {instrument} {bid}/{ask}')
def step_impl(context, instrument, bid, ask):
    context.rates_events.put(TickEvent(instrument, get_time(), float(bid), float(ask)))


@given('market rate cache is initialized')
def step_impl(context):
    context.rates_cache = FxPricesCache()


@given('market rate for {ccy} is {bid}/{ask} wrt {base_ccy}')
def step_impl(context, ccy, bid, ask, base_ccy):
    context.rates_cache.set_rate(TickEvent(ccy + '_' + base_ccy, get_time(), float(bid), float(ask)))


@when('an old tick arrives for {instrument} {bid}/{ask}')
def step_impl(context, instrument, bid, ask):
    context.old_tick = TickEvent(instrument, get_time(-2*context.rates_cache.max_tick_age), float(bid), float(ask))
    context.rates_events.put(context.old_tick)


@then('the old tick goes into exception queue')
def step_impl(context):
    exception = None
    try:
        while True:
            exception = context.exception_q.get_nowait()
    except Empty:
        pass
    assert isinstance(exception, ExceptionEvent), 'expecting ExceptionEvent, but got [%s]' % exception
    assert exception.orig_event is not None, 'expecting stale tick information in ExceptionEvent, but got None'
    assert context.old_tick == exception.orig_event, 'expecting stale tick [%s] in ExceptionEvent, but got [%s]' \
                                                     % (context.old_tick, exception.orig_event)

