import sys

sys.path.append('../main/')

from behave import *

from com.open.algo.risk.ccyExposureLimitRisk import CcyExposureLimitRiskEvaluator
from com.open.algo.trading.fxEvents import TickEvent
from com.open.algo.model import gettime


@then('we use RiskManager to evaluate currency exposure')
def step_impl(context):
    assert None != CcyExposureLimitRiskEvaluator('BC')


@given('we have ccy exposure manager with base currency {base_ccy}, default ccy limit')
def step_impl(context, base_ccy):
    context.rm = CcyExposureLimitRiskEvaluator(base_ccy, ccy_limit=5000)

@given('we have ccy exposure manager with base currency {base_ccy}, default ccy short limit')
def step_impl(context, base_ccy):
    context.rm = CcyExposureLimitRiskEvaluator(base_ccy, ccy_limit_short=-5000)

@given('there is no specific exposure limit for currencies {ccy1} and {ccy2}')
def step_impl(context, ccy1, ccy2):
    context.rm.set_limit(ccy1)
    context.rm.set_limit(ccy2)

@given('there is no specific short exposure limit for currency {ccy}')
def step_impl(context, ccy):
    context.rm.set_limit(ccy)

@given('market rate for {ccy} is {bid}/{ask} wrt {base_ccy}')
def step_impl(context, ccy, bid, ask, base_ccy):
    assert context.rm.base_ccy == base_ccy, 'fx rate specified in currency [%s] which is not base currency [%s]' % (base_ccy, context.rm.base_ccy)
    context.rm.set_rate(TickEvent(ccy, gettime(), float(bid), float(ask)))

@given('we have ccy exposure manager with base currency {base_ccy}, default ccy limit of {def_limit}')
def step_impl(context, base_ccy, def_limit):
    context.rm = CcyExposureLimitRiskEvaluator(base_ccy, ccy_limit=float(def_limit))

@given('we have ccy exposure manager with base currency {base_ccy}, default ccy short limit of {def_limit}')
def step_impl(context, base_ccy, def_limit):
    context.rm = CcyExposureLimitRiskEvaluator(base_ccy, ccy_limit_short=-1*float(def_limit))

@given('the specific short limit for currency {ccy} is {ccy_limit_short}')
def step_impl(context, ccy, ccy_limit_short):
    context.rm.set_limit(ccy, ccy_limit_short=-1*float(ccy_limit_short))

@given('the specific exposure limit for currency {ccy} is {ccy_limit}')
def step_impl(context, ccy, ccy_limit):
    context.rm.set_limit(ccy, float(ccy_limit))

@given('we have ccy exposure manager, base currency {base_ccy}, large short limit, default ccy limit of {def_limit}')
def step_impl(context, base_ccy, def_limit):
    context.rm = CcyExposureLimitRiskEvaluator(base_ccy, ccy_limit=float(def_limit), ccy_limit_short=-100000)

@given('we have ccy exposure manager, base currency {base_ccy}, default short limit, default ccy limit of {def_limit}')
def step_impl(context, base_ccy, def_limit):
    context.rm = CcyExposureLimitRiskEvaluator(base_ccy, ccy_limit=float(def_limit), ccy_limit_short=-5000)

@given('we have ccy exposure manager, base currency {base_ccy}, large default limit, default short ccy limit of {def_limit}')
def step_impl(context, base_ccy, def_limit):
    context.rm = CcyExposureLimitRiskEvaluator(base_ccy, ccy_limit=100000, ccy_limit_short=-1*float(def_limit))
