import sys

from behave import *

from com.open.algo.utils import get_time
from com.open.algo.trading.eventTrading import AlgoTrader
from com.open.algo.dummy import DummyBuyStrategy, DummyExecutor
from com.open.algo.wiring.eventLoop import EventLoop
from com.open.algo.trading.fxEvents import *
from com.open.algo.strategy import StrategyOrderManager


@given('we are using a dummy strategy and executor')
def step_impl(context):
    context.strategy = StrategyOrderManager(DummyBuyStrategy(), 100)
    context.executor = DummyExecutor()


@given('we are using a dummy strategy')
def step_impl(context):
    context.strategy = StrategyOrderManager(DummyBuyStrategy(), 100)


@given('we are using a dummy executor')
def step_impl(context):
    context.executor = DummyExecutor()


@given('we have a trading bot')
def step_impl(context):
    context.trader = AlgoTrader(None, context.strategy, context.executor)
    context.trader_bot = EventLoop(context.events, context.trader, processed_event_q=context.events)


@when('trading bot is stopped')
def step_impl(context):
    context.trader_bot.started = False


@given('bot is trading')
def step_impl(context):
    context.trader_bot.started = True


@when('no event occured')
def step_impl(context):
    pass


@then('executor receives no order')
def step_impl(context):
    le = context.executor.get_last_event()
    assert le is None, 'executor wrongly logged event when none was expected [%s]' % le


@when('we input a price tick event')
def step_impl(context):
    context.events.put(TickEvent('EUR_GBP', get_time(), 0.87, 0.88))


@then('executor receives an order')
def step_impl(context):
    le = context.executor.get_last_event()
    assert le is not None, 'executor did not get any event'


@when('we input an invalid event')
def step_impl(context):
    context.event = 'this is an invalid event'
    context.events.put(context.event)


@when('trading bot tries to process')
def step_impl(context):
    try:
        context.trader_bot.pull_process()
    except:
        print('Unexpected error-%s' % sys.exc_info()[0])
