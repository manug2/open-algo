import sys

sys.path.append('../main/')
import queue, threading, time

from com.open.algo.eventLoop import Journaler
from com.open.algo.oanda.streaming import *
from com.open.algo.oanda.environments import ENVIRONMENTS

from behave import *


@given('we want to establish connection to Oanda {domainAlias}')
def step_impl(context, domainAlias):
    context.env = domainAlias


@given('using access token "{token}"')
def step_impl(context, token):
    context.token = token


@given('using account id "{account_id}"')
def step_impl(context, account_id):
    context.account_id = account_id


@given('using instrument "{instrument}"')
def step_impl(context, instrument):
    context.instrument = instrument


@given('using {connection} connection')
def step_impl(context, connection):
    context.connection = connection


@when('i say connect')
def step_impl(context):
    context.response = None
    domain = ENVIRONMENTS[context.connection][context.env]
    context.prices = StreamingForexPrices(
        domain, context.token, context.account_id,
        context.instrument, None, None, None
    )
    print(str(context.prices))
    context.response = context.prices.connect()


@then('we are able to connect to Oanda')
def step_impl(context):
    assert context.response.status_code == 200


# Scenario streaming
@given('we want to stream ticks from Oanda {domainAlias}')
def step_impl(context, domainAlias):
    context.env = domainAlias


@when('i say stream')
def step_impl(context):
    context.response = None
    context.journaler = Journaler()
    domain = ENVIRONMENTS[context.connection][context.env]
    context.events = queue.Queue()
    context.exceptions = queue.Queue()
    context.prices = StreamingForexPrices(
        domain, context.token, context.account_id,
        context.instrument, context.events, context.journaler, context.exceptions
    )
    price_thread = threading.Thread(target=context.prices.stream, args=[])
    price_thread.start()
    time.sleep(1.5)
    context.prices.stop()


@then('we received a tick for this instrument')
def step_impl(context):
    event = context.events.get(True, 0.5)
    assert event.TYPE == 'TICK'
    assert event.instrument == context.instrument


@then('we received few ticks for this instrument')
def step_impl(context):
    while True:
        try:
            context.lastEvent = context.events.get(False)
        except queue.Empty:
            break

    assert context.lastEvent.TYPE == 'TICK'
    assert context.lastEvent.instrument == context.instrument


@then('last tick was logged by the journaler as last event')
def step_impl(context):
    assert context.lastEvent == context.journaler.getLastEvent()


@given('using {field}={value}, {field1}={value1} and {field2}={value2}')
def step_impl(context, field, value, field1, value1, field2, value2):
    setattr(context, field, value)
    setattr(context, field1, value1)
    setattr(context, field2, value2)

