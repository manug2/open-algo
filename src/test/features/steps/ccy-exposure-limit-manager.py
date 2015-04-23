import sys

sys.path.append('../main/')

from behave import *

from com.open.algo.risk.ccyExposureLimitRisk import CcyExposureLimitRiskEvaluator


@then('we use RiskManager to evaluate currency exposure')
def step_impl(context):
    assert None != CcyExposureLimitRiskEvaluator('BC')


@given('we have ccy exposure manager with base currency {base_ccy}, default ccy limit')
def step_impl(context, base_ccy):
    context.rm = CcyExposureLimitRiskEvaluator(base_ccy)

@given('we have ccy exposure manager with base currency {base_ccy}, default ccy short limit')
def step_impl(context, base_ccy):
    context.rm = CcyExposureLimitRiskEvaluator(base_ccy)

@given('there is no specific exposure limit for currencies {ccy1} and {ccy2}')
def step_impl(context, ccy1, ccy2):
    context.rm.set_limit(ccy1)
    context.rm.set_limit(ccy2)

@given('there is no specific short exposure limit for currency {ccy}')
def step_impl(context, ccy):
    context.rm.set_limit(ccy)

@given('market rate for {ccy} is {bid}/{ask} wrt {baseCcy}')
def step_impl(context, ccy, bid, ask, baseCcy):
    context.rm.fix_rate(ccy, float(bid), float(ask))

@given('we have ccy exposure manager with base currency {base_ccy}, default ccy limit of {def_limit}')
def step_impl(context, base_ccy, def_limit):
    context.rm = CcyExposureLimitRiskEvaluator(base_ccy, ccyLimit=float(def_limit))

@given('we have ccy exposure manager with base currency {base_ccy}, default ccy short limit of {def_limit}')
def step_impl(context, base_ccy, def_limit):
    context.rm = CcyExposureLimitRiskEvaluator(base_ccy, ccyLimitShort=-1*float(def_limit))


@given('the specific exposure limit for currency {ccy} is {ccy_limit}')
def step_impl(context, ccy, ccy_limit):
    context.rm.set_limit(ccy, float(ccy_limit))


@given('we have ccy exposure manager, base currency {base_ccy}, large short limit, default ccy limit of {def_limit}')
def step_impl(context, base_ccy, def_limit):
    context.rm = CcyExposureLimitRiskEvaluator(base_ccy, ccyLimit=float(def_limit), ccyLimitShort=-100000)
