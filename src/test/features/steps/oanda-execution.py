import sys, os

sys.path.append('../main/')
from configparser import ConfigParser

from com.open.algo.oanda.execution import *
from com.open.algo.model import gettime
from com.open.algo.trading.fxEvents import *
from com.open.algo.oanda.environments import ENVIRONMENTS, CONFIG_PATH

from behave import *
import logging


@given('we want to {side} {units} units of {instrument}')
def step_impl(context, side, units, instrument):
    context.orderEvent = OrderEvent(instrument, int(units), side)


@given('using authorization details from config file from path "{path}"')
def step_impl(context, path):
    context.mySettings = readSettings(path, context.env)


def readSettings(path, env):
    logger = logging.getLogger('oanda-execution')
    config = ConfigParser()
    cf = os.path.join(path, env + '.oanda.config')
    logger.debug('Using config file [%s]' % cf)
    config.read(cf)
    logger.debug('CONFIG section : %s' % config.options('CONFIG'))
    settings = config['CONFIG']
    logger.info('settings : %s' % settings)
    return settings


def getExecutor(context, connection, env, settings):
    domain = ENVIRONMENTS[connection][env]
    executor = OandaExecutionHandler(domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID'])
    return executor


@when('i say execute order')
def step_impl(context):
    context.response = None
    context.response = context.executor.execute_order(context.orderEvent)
    context.executor.stop()


@then('we received response from Oanda')
def step_impl(context):
    assert context.response != None


@then('response has {trade} section')
def step_impl(context, trade):
    assert not (('code' in context.response) or (
    'message' in context.response)), 'Unexpected Oanda response, code :(%s), message : "%s"' % (
    context.response['code'], context.response['message'])
    assert trade in context.response
    assert context.response[trade] != None


@then('response has {field} equal to {value}')
def step_impl(context, field, value):
    context.response[field] == value


@then('response section {trade} has {field} equal to {value}')
def step_impl(context, trade, field, value):
    context.response[trade][field] == value


@given('we have executed the order')
def step_impl(context):
    context.executor.execute_order(context.orderEvent)


@when('i say query my orders')
def step_impl(context):
    context.response = None
    # executor = getExecutor(context, context.connection, context.env, context.mySettings)
    #executor.connect()
    context.response = context.executor.get_orders()
    context.executor.stop()


@given('we put limit order to {side} {units} units of {instrument} at price {price} expiring in {expiry} minutes')
def step_impl(context, side, units, instrument, price, expiry):
    expiryTime = gettime(60 * int(expiry))
    context.orderEvent = OrderEvent(instrument, int(units), side, order_type='limit', price=float(price),
                                    expiry=expiryTime)


@then('response lists my original order')
def step_impl(context):
    assert 'orders' in context.response
    found = False
    oe = context.orderEvent
    for order in context.response['orders']:
        if order['side'] == oe.side and order['units'] == oe.units and order['instrument'] == oe.instrument and order[
            'type'] == oe.order_type and 'expiry' in order and order['expiry'] == oe.expiry and 'price' in order and \
                        order['price'] == oe.price:
            found = True
            break
    assert found


@when('Executor connects')
def step_impl(context):
    context.response = None
    logger = logging.getLogger('oanda-execution')
    try:
        executor = getExecutor(context, context.connection, context.env, context.mySettings)
        executor.connect()
        executor.stop()
    except IOError as e:
        logger.error('I/O error-%s' % e)
        context.response = sys.exc_info()[0]
    except:
        logger.error('Unexpected error-%s' % sys.exc_info()[0])
        context.response = sys.exc_info()[0]


@then('system does not get a failure response')
def step_impl(context):
    assert context.response == None, 'Expecting None response but was [%s]' % context.response


@given('Executor is setup to connect to Oanda {env} using {connection} connection')
def step_impl(context, env, connection):
    context.response = None
    settings = readSettings('../../../fx-oanda/', env)
    context.executor = getExecutor(context, connection, env, settings)
    context.executor.connect()

