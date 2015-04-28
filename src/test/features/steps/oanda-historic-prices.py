import sys

sys.path.append('../main/')

from com.open.algo.oanda.history import *
from com.open.algo.oanda.environments import ENVIRONMENTS, CONFIG_PATH_FOR_FEATURE_STEPS
from com.open.algo.utils import read_settings

from behave import *

@when('i say query prices for {instrument}')
def step_impl(context, instrument):
    context.response = None
    domain = ENVIRONMENTS[context.connection][context.env]
    settings = read_settings(CONFIG_PATH_FOR_FEATURE_STEPS, context.env)

    context.prices = HistoricForexPrices(
        domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID']
    )
    context.instrument = instrument
    context.response = context.prices.query(instrument)

@then('we receive historical ticks for this instrument')
def step_impl(context):
    assert context.response is not None
    assert type(context.response) is list
    print (context.response)
    assert context.response[0] is not None
    assert isinstance(context.response[0], TickEvent)
    assert context.response[0].bid is not None
    assert context.response[0].ask is not None
