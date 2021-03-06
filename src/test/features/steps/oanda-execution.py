import sys
from com.open.algo.oanda.execution import *
from com.open.algo.trading.fxEvents import *
from com.open.algo.oanda.environments import ENVIRONMENTS, CONFIG_PATH_FOR_FEATURE_STEPS
from com.open.algo.utils import read_settings, get_time_with_zero_millis
from com.open.algo.journal import Journaler
from behave import *

OANDA_TRADE_KEY = 'tradeOpened'
OANDA_ORDER_KEY = 'orderOpened'


@given('we want to {side} {units} units of {instrument}')
def step_impl(context, side, units, instrument):
    context.orderEvent = OrderEvent(instrument, int(units), side)

@given('using authorization details from config file from path "{path}"')
def step_impl(context, path):
    context.mySettings = read_settings(path, context.env)


def get_executor(connection, env, settings):
    domain = ENVIRONMENTS[connection][env]
    executor = OandaExecutionHandler(domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID'], Journaler())
    return executor


@when('i say execute order')
def step_impl(context):
    context.response = None
    context.response = context.executor.execute_order(context.orderEvent)
    context.executor.stop()


# @then('we received response from Oanda')
# def step_impl(context):
#    assert context.response is not None


@then('Oanda booked a new trade')
def step_impl(context):
    assert context.response is not None
    assert not (('code' in context.response) or ('message' in context.response)), \
        'Unexpected Oanda response, code :(%s), message : "%s"' % \
            (context.response['code'], context.response['message'])
    assert OANDA_TRADE_KEY in context.response
    assert context.response[OANDA_TRADE_KEY] is not None


# @then('Oanda response has {field} equal to {value}')
# def step_impl(context, field, value):
#     assert context.response[field] == value


@then('Oanda trade has {field} = {value}')
def step_impl(context, field, value):
    # assert type(context.response[trade][field]) == type(value), \
    # 'type found is [%s], expecting [%s]' % (type(context.response[trade][field]), type(value))
    if field == 'instrument':
        assert str(context.response['instrument']) == value, \
            'value found is [%s], expecting [%s]' % (context.response['instrument'], value)
    else:
        assert str(context.response[OANDA_TRADE_KEY][field]) == value, \
            'value found is [%s], expecting [%s]' % (context.response[OANDA_TRADE_KEY][field], value)


@given('we have executed the order')
def step_impl(context):
    context.executor.execute_order(context.orderEvent)


@then('Oanda opened a new order')
def step_impl(context):
    assert context.response is not None
    assert not (('code' in context.response) or ('message' in context.response)), \
        'Unexpected Oanda response, code :(%s), message : "%s"' % \
            (context.response['code'], context.response['message'])
    assert OANDA_ORDER_KEY in context.response
    assert context.response[OANDA_ORDER_KEY] is not None


@then('Oanda order has {field} = {value}')
def step_impl(context, field, value):
    # assert type(context.response[trade][field]) == type(value), \
    # 'type found is [%s], expecting [%s]' % (type(context.response[trade][field]), type(value))
    if field == 'instrument':
        assert str(context.response['instrument']) == value, \
            'value found is [%s], expecting [%s]' % (context.response['instrument'], value)
    else:
        assert str(context.response[OANDA_ORDER_KEY][field]) == value, \
            'value found is [%s], expecting [%s]' % (context.response[OANDA_ORDER_KEY][field], value)


@when('i say query my orders')
def step_impl(context):
    context.response = None
    # executor = get_executor(context.connection, context.env, context.mySettings)
    # executor.connect()
    context.response = context.executor.get_orders()
    context.executor.stop()


@given('we put limit order to {side} {units} units of {instrument} at price {price} expiring in {expiry} minutes')
def step_impl(context, side, units, instrument, price, expiry):
    expiry_time = get_time_with_zero_millis(60 * int(expiry))
    context.orderEvent = \
        OrderEvent(instrument, int(units), side, order_type='limit', price=float(price), expiry=expiry_time)


@then('Oanda lists my original order')
def step_impl(context):
    assert context.response is not None
    assert 'orders' in context.response
    found = False
    oe = context.orderEvent
    for order in context.response['orders']:
        if order['side'] == oe.side and order['units'] == oe.units and order['instrument'] == oe.instrument and \
            order['type'] == oe.order_type and 'expiry' in order and order['expiry'] == oe.expiry and 'price' in order and \
                order['price'] == oe.price:
            found = True
            break
    assert found


@when('Executor connects')
def step_impl(context):
    context.response = None
    try:
        executor = get_executor(context.connection, context.env, context.mySettings)
        executor.connect()
        executor.stop()
    except IOError as e:
        print('I/O error-%s' % e)
        context.response = sys.exc_info()[0]
    except:
        print('Unexpected error-%s' % sys.exc_info()[0])
        context.response = sys.exc_info()[0]


@then('system does not get a failure response')
def step_impl(context):
    assert context.response is None, 'Expecting None response but was [%s]' % context.response


@given('Executor is setup to connect to Oanda {env} using {connection} connection')
def step_impl(context, env, connection):
    context.response = None
    settings = read_settings(CONFIG_PATH_FOR_FEATURE_STEPS, env)
    context.executor = get_executor(connection, env, settings)
    context.executor.connect()

