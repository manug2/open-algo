import queue
import threading
import time

from behave import *

from com.open.algo.journal import Journaler
from com.open.algo.oanda.streaming import *
from com.open.algo.oanda.environments import ENVIRONMENTS, CONFIG_PATH_FOR_FEATURE_STEPS
from com.open.algo.utils import read_settings
from com.open.algo.trading.fxEvents import TickEvent


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
    context.streamer = \
        get_price_streamer(context, context.connection, context.env, context.token, context.account_id, 'EUR_USD')
    print(str(context.streamer))
    context.response = context.streamer.connect()


@then('we are able to connect to Oanda')
def step_impl(context):
    context.streamer.stop()
    assert context.response.status_code == 200


# Scenario streaming
@given('we want to stream ticks from Oanda {domainAlias}')
def step_impl(context, domainAlias):
    context.env = domainAlias


@when('i say stream')
def step_impl(context):

    context.streamer = \
        get_price_streamer(context, context.connection, context.env, context.token, context.account_id, 'EUR_USD')

    context.price_thread = threading.Thread(target=context.streamer.stream, args=[])
    context.price_thread.start()


@then('we received a tick')
def step_impl(context):
    print('waiting for a tick..')
    attempts = 0
    while True:
        try:
            event = context.events.get_nowait()
            break
        except queue.Empty:
            attempts += 1
            if attempts > 20:
                break
            else:
                time.sleep(1)

    assert event is not None, 'did not receive tick'
    if event:
        print('got a tick')
    context.streamer.stop()
    context.price_thread.join(timeout=5)
    print('stopped streaming..')
    assert event.TYPE == 'TICK'
    assert event.instrument is not None


@then('we received few ticks for this instrument')
def step_impl(context):
    try:
        event = context.events.get(timeout=25)
        assert context.last_tick is not None, 'did not receive tick'
        assert isinstance(context.last_tick, TickEvent), 'expected to receive TickEvent, but go [%s]' % event
        assert event.TYPE == 'TICK'
        assert event.instrument == context.instrument
        context.last_tick = event
    except queue.Empty:
        pass
    finally:
        context.streamer.stop()
        context.price_thread.join(timeout=5)


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
    pricer = OandaEventStreamer(domain, token, account_id, context.journaler)
    pricer.set_instruments(instruments)
    pricer.set_events_q(context.events).set_heartbeat_q(context.heartbeat_events).set_exception_q(context.exceptions)
    return pricer


@given('System is connected to Oanda {env} using {connection} connection for {instrument} prices')
def step_impl(context, env, connection, instrument):
    context.instrument = instrument
    settings = read_settings(CONFIG_PATH_FOR_FEATURE_STEPS, env)
    context.streamer = \
        get_price_streamer(context, connection, env, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID'], 'EUR_USD')
    context.price_thread = threading.Thread(target=context.streamer.stream, args=[])
    context.price_thread.start()
    time.sleep(5)
    context.streamer.stop()
    context.price_thread.join(timeout=10)


@given('System is connecting to Oanda {env} using {connection} connection for {instrument} prices')
def step_impl(context, env, connection, instrument):
    context.instrument = instrument
    settings = read_settings(CONFIG_PATH_FOR_FEATURE_STEPS, env)
    context.streamer = \
        get_price_streamer(context, connection, env, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID'], 'EUR_USD')
    context.price_thread = threading.Thread(target=context.streamer.stream, args=[])
    context.price_thread.start()


@then('Oanda rates connection is stopped')
def step_impl(context):
    context.streamer.stop()


@then('we wait for Oanda to sends heartbeat and stop')
def step_impl(context):
    try:
        context.last_hb = context.heartbeat_events.get(timeout=10)
        assert isinstance(context.last_hb, Heartbeat), 'expecting heartbeat, received event [%s]' % context.last_hb
        assert context.last_hb.TYPE == 'HB', 'expecting heartbeat, received event of type [%s]' % context.last_hb.TYPE
        assert context.last_hb.alias == 'oanda-stream', \
            'expecting from oanda-stream, received event of alias [%s]' % context.last_hb.alias
    except queue.Empty:
        assert context.last_hb is not None, 'did not received heartbeat'
    finally:
        context.streamer.stop()


