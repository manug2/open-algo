from behave import *
import queue, time, threading
from datetime import datetime
from com.open.algo.trading.eventTrading import AlgoTrader
from com.open.algo.dummy import DummyBuyStrategy, DummyExecutor
from com.open.algo.utils import Journaler, EventLoop
from com.open.algo.trading.fxEvents import *


@given('we have an event stream')
def step_impl(context):
    context.events = queue.Queue()
    context.journaler = Journaler()


@given('we are using a dummy strategy and executor')
def step_impl(context):
    context.strategy = DummyBuyStrategy(context.events, 100, context.journaler)
    context.executor = DummyExecutor()


@given('we are using a dummy strategy')
def step_impl(context):
    context.strategy = DummyBuyStrategy(context.events, 100, context.journaler)


@given('we are using a dummy executor')
def step_impl(context):
    context.executor = DummyExecutor()


@given('we have a trading bot')
def step_impl(context):
    context.trader = AlgoTrader(None, context.strategy, context.executor)
    context.trader_bot = EventLoop(context.events, context.trader, 0.5)


@given('bot is trading in a thread')
def step_impl(context):
    context.trade_thread = threading.Thread(target=context.trader_bot.start, args=[])
    context.trade_thread.start()


@when('bot trading thread is stopped')
def step_impl(context):
    context.trader_bot.stop()
    time.sleep(0.5)


@when('bot trading is stopped')
def step_impl(context):
    context.trader_bot.pull_process()
    context.trader_bot.started = False


@given('bot is trading')
def step_impl(context):
    context.trader_bot.started = True


@when('no event occured')
def step_impl(context):
    pass


@then('trader generates no output')
def step_impl(context):
    le = context.journaler.getLastEvent()
    assert le is None, 'journaler wrongly logged event when none was expected [%s]' % le


@when('we input a price tick event')
def step_impl(context):
    context.events.put(TickEvent('EUR_GBP', str(datetime.now()), 0.87, 0.88))


@then('bot generates an order')
def step_impl(context):
    assert context.journaler.getLastEvent() is not None, 'journaler did not log any event'


@when('we input an invalid event')
def step_impl(context):
    context.event = 'this is an invalid event'
    context.events.put(context.event)

