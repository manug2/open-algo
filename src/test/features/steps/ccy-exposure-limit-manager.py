import sys

sys.path.append('../main/')

from behave import *

from com.open.algo.risk.ccyExposureLimitRisk import CcyExposureLimitRiskEvaluator


@then('we use RiskManager to evaluate currency exposure')
def step_impl(context):
    assert None != CcyExposureLimitRiskEvaluator('BC')


@given('we have ccy exposure manager with base currency {baseCurrency}, default ccy limit')
def step_impl(context, baseCurrency):
    context.rm = CcyExposureLimitRiskEvaluator(baseCurrency)

@given('we have ccy exposure manager with base currency {baseCurrency}, default ccy short limit')
def step_impl(context, baseCurrency):
    context.rm = CcyExposureLimitRiskEvaluator(baseCurrency)

@given('market rate to {longShort} {ccy} is {ccyRate} units of base ccy')
def step_impl(context, longShort, ccy, ccyRate):
    if longShort == 'buy':
        ccySide = 'ask'
    else:
        ccySide = 'bid'
    if not ccy in context.rm.ratesMap:
        context.rm.ratesMap[ccy] = {}
    context.rm.ratesMap[ccy][ccySide] = float(ccyRate)


@given('there is no specific exposure limit for currencies {ccy1} and {ccy2}')
def step_impl(context, ccy1, ccy2):
    context.rm.set_limit(ccy1)
    context.rm.set_limit(ccy2)

@given('there is no specific short exposure limit for currency {ccy}')
def step_impl(context, ccy):
    context.rm.set_limit(ccy)

@given('market rate for {ccy} is {bid}/{ask} wrt {baseCcy}')
def step_impl(context, ccy, bid, ask, baseCcy):
    if not ccy in context.rm.ratesMap:
        context.rm.ratesMap[ccy] = {}
    context.rm.ratesMap[ccy]['bid'] = float(bid)
    context.rm.ratesMap[ccy]['ask'] = float(ask)


@given('we have ccy exposure manager with base currency {baseCurrency}, default ccy limit of {def_limit}')
def step_impl(context, baseCurrency, def_limit):
    context.rm = CcyExposureLimitRiskEvaluator(baseCurrency, ccyLimit=float(def_limit))

@given('we have ccy exposure manager with base currency {baseCurrency}, default ccy short limit of {def_limit}')
def step_impl(context, baseCurrency, def_limit):
    context.rm = CcyExposureLimitRiskEvaluator(baseCurrency, ccyLimitShort=-1*float(def_limit))


@given('the specific exposure limit for currency {ccy} is {ccy_limit}')
def step_impl(context, ccy, ccy_limit):
    context.rm.set_limit(ccy, float(ccy_limit))

