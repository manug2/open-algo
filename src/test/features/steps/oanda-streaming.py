import queue
import threading
import time

from behave import *

from com.open.algo.journal import Journaler
from com.open.algo.oanda.streaming import *
from com.open.algo.oanda.environments import ENVIRONMENTS, CONFIG_PATH_FOR_FEATURE_STEPS
from com.open.algo.utils import read_settings


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
    context.prices = \
        get_price_streamer(context, context.connection, context.env, context.token, context.account_id, 'EUR_USD')
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

    context.prices = \
        get_price_streamer(context, context.connection, context.env, context.token, context.account_id, 'EUR_USD')

    price_thread = threading.Thread(target=context.prices.stream, args=[])
    price_thread.start()
    time.sleep(2.5)
    context.prices.stop()


@then('we received a tick')
def step_impl(context):
    event = context.events.get(True, 0.5)
    assert event.TYPE == 'TICK'
    assert event.instrument is not None


@then('we received few ticks for this instrument')
def step_impl(context):
    try:
        while True:
            context.last_tick = context.events.get_nowait()
    except queue.Empty:
        pass

    assert context.last_tick.TYPE == 'TICK'
    assert context.last_tick.instrument == context.instrument


@then('journaler logs input events')
def step_impl(context):
    last_event_str = context.journaler.get_last_event()
    last_received = context.journaler.get_last_received()
    last_event = json.loads(last_event_str)
    print('last event = %s' % last_event)
    assert last_event is not None
    parsed = parse_event(last_received, last_event)
    assert isinstance(parsed, TickEvent) or isinstance(parsed, Heartbeat)


@given('using {field}={value}, {field1}={value1} and {field2}={value2}')
def step_impl(context, field, value, field1, value1, field2, value2):
    setattr(context, field, value)
    setattr(context, field1, value1)
    setattr(context, field2, value2)


@then('Oanda sends heartbeats')
def step_impl(context):
    try:
        while True:
            context.last_hb = context.heartbeat_events.get_nowait()
    except queue.Empty:
        pass

    assert context.last_hb.TYPE == 'HB'
    assert context.last_hb.alias == 'oanda-stream'


def get_price_streamer(context, connection, env, token, account_id, instruments):
    context.last_tick = None
    context.last_hb = None
    context.response = None
    context.journaler = Journaler()

    context.events = queue.Queue()
    context.heartbeat_events = queue.Queue()
    context.exceptions = queue.Queue()

    domain = ENVIRONMENTS[connection][env]
    pricer = StreamingForexPrices(
        domain, token, account_id,
        instruments, context.events, context.heartbeat_events, context.journaler, context.exceptions
    )
    return pricer

@given('System is connected to Oanda {env} using {connection} connection for {instrument} prices')
def step_impl(context, env, connection, instrument):
    context.instrument = instrument
    settings = read_settings(CONFIG_PATH_FOR_FEATURE_STEPS, env)
    context.streamer = \
        get_price_streamer(context, connection, env, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID'], 'EUR_USD')
    price_thread = threading.Thread(target=context.streamer.stream, args=[])
    price_thread.start()
    time.sleep(3.5)
    context.streamer.stop()
