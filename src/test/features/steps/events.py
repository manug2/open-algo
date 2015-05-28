import sys

sys.path.append('../main/')

from com.open.algo.trading.fxEvents import *
from com.open.algo.eventLoop import Journaler
from behave import *
from queue import Queue


@given('we have an event stream')
def step_impl(context):
    context.events = Queue()
# events
@given('we want to trade')
def step_impl(context):
    context.listen = True


@when('we want to listen to tick')
def step_impl(context):
    context.event = TickEvent(None, None, None, None)


@when('we want to create order')
def step_impl(context):
    context.event = OrderEvent('ABC', 1, 'buy')


@then('we use TickEvent')
def step_impl(context):
    et = context.event.__class__.__name__
    assert et == 'TickEvent'


@then('we use OrderEvent')
def step_impl(context):
    et = context.event.__class__.__name__
    assert et == 'OrderEvent'


#journaler
@given('we want to trade in event driven fashion utilizing a journaler')
def step_impl(context):
    context.journaler = Journaler()


@when('we want to log event')
def step_impl(context):
    context.event = Event('dummy')


@then('there is a journaler')
def step_impl(context):
    assert context.journaler != None
    assert context.journaler.__class__.__name__ == 'Journaler'


@then('journaler can log event')
def step_impl(context):
    context.journaler.log_event(context.event)


@when('we receive a tick')
def step_impl(context):
    context.event = TickEvent('SGD_GBP', '', 1.0, 1.0)
    context.journaler.log_event(context.event)


@then('journaler logs show it as last event')
def step_impl(context):
    assert context.event == context.journaler.get_last_event()
    context.journaler.log_event(context.event)

