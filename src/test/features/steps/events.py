import sys

sys.path.append('../main/')

from com.open.algo.trading.fxEvents import *
from com.open.algo.utils import Journaler
from behave import *

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
    context.event = Event()


@then('there is a journaler')
def step_impl(context):
    assert context.journaler != None
    assert context.journaler.__class__.__name__ == 'Journaler'


@then('journaler can log event')
def step_impl(context):
    context.journaler.logEvent(context.event)


@when('we receive a tick')
def step_impl(context):
    context.event = TickEvent('SGD_GBP', '', 1.0, 1.0)
    context.journaler.logEvent(context.event)


@then('journaler logs show it as last event')
def step_impl(context):
    assert context.event == context.journaler.getLastEvent()
    context.journaler.logEvent(context.event)

