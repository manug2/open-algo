import logging
from behave import *
from com.open.algo.model import RiskManager
from com.open.algo.risk.fxPositionLimitRisk import FxPositionLimitRiskEvaluator

@given('RiskManager with default position limit')
def step_impl(context):
	context.rm = FxPositionLimitRiskEvaluator()

@given('RiskManager with default position limit of {limitAmount}')
def step_impl(context, limitAmount):
	context.rm = None
	context.rm = FxPositionLimitRiskEvaluator(posLimit=float(limitAmount))

@given('position limit for instrument {instrument} is {limitAmount} units')
def step_impl(context, instrument, limitAmount):
	context.rm.set_limit(instrument, posLimit=float(limitAmount))

@when('when i say filter order')
def step_impl(context):
	context.filteredOrder = None
	logger = logging.getLogger('fx-risk-manager')
	logger.info(context.orderEvent)
	context.filteredOrder = context.rm.filter_order(context.orderEvent)

@then('RiskManager returns filtered order')
def step_impl(context):
	assert context.filteredOrder != None, 'there is no filtered order'

@then('filtered order has {field}={value} and {field1}={value1}')
def step_impl(context, field, value, field1, value1):
	assert getattr(context.filteredOrder,field) == value, 'value of [%s] is wrongly [%s]' % (field, value)
	assert getattr(context.filteredOrder,field1) == value1, 'value of [%s] is wrongly [%s]' % (field1, value1)

@then('filtered order has {field}={value}, {field1}={value1}, {field2}={value2}')
def step_impl(context, field, value, field1, value1, field2, value2):
	assert getattr(context.filteredOrder,field) == value, 'value of [%s] is wrongly [%s]' % (field, value)
	assert getattr(context.filteredOrder,field1) == value1, 'value of [%s] is wrongly [%s]' % (field1, value1)
	assert getattr(context.filteredOrder,field2) == value2, 'value of [%s] is wrongly [%s]' % (field2, value2)

@then('filtered order has numerical {field}={value}')
def step_impl(context, field, value):
	expected = value
	observed = getattr(context.filteredOrder,field)
	assert float(expected) == float(observed), 'value of [%s] in filtered order is wrongly [%s], expected=[%s]' % (field, observed, expected)

@then('filtered order has numerical {field} equal to default position limit')
def step_impl(context, field):
	expected = context.rm.posLimit
	observed = getattr(context.filteredOrder,field)
	assert float(expected) == float(observed), 'value of [%s] in filtered order is wrong [%s], expected=[%s]' % (field, observed, expected)

@given('RiskManager with default short position limit of {limitAmount}')
def step_impl(context, limitAmount):
	context.rm = None
	context.rm = FxPositionLimitRiskEvaluator(posLimitShort= -1 * float(limitAmount))

@then('filtered order has numerical {field} equal to default short position limit')
def step_impl(context, field):
	expected = context.rm.posLimitShort
	observed = getattr(context.filteredOrder,field)
	assert float(expected) == float(observed), 'value of [%s] in filtered order is wrong [%s], expected=[%s]' % (field, observed, expected)

@given('short position limit for instrument {instrument} is {limitAmount} units')
def step_impl(context, instrument, limitAmount):
	context.rm.set_limit(instrument, posLimitShort=-1*float(limitAmount))

@given('current holding of {instrument} is {amount}')
def step_impl(context, instrument, amount):
	context.rm.append_position(instrument, float(amount))

@then('filtered order has numerical {field} equal to default position limit minus {currValue}')
def step_impl(context, field, currValue):
	expected = context.rm.posLimit - float(currValue)
	observed = getattr(context.filteredOrder,field)
	assert expected == float(observed), 'value of [%s] in filtered order is wrong [%s], expected=[%s]' % (field, observed, expected)

@then('filtered order has numerical {field} equal to default short position limit minus {currValue}')
def step_impl(context, field, currValue):
	assert float(getattr(context.filteredOrder,field)) == context.rm.posLimitShort - float(currValue)

@given('there is no position limit for instrument {instrument}')
def step_impl(context, instrument):
	context.rm.set_limit(instrument)

