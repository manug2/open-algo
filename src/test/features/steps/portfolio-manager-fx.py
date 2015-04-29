__author__ = 'ManuGarg'

from behave import *

from com.open.algo.trading.fxPortfolio import *
from com.open.algo.trading.fxEvents import *

@given('Portfolio Manager is initialized')
def step_impl(context):
    context.pm = FxPortfolio()


@then('Portfolio Manager yields empty position list')
def step_impl(context):
    assert context.pm.list_positions() is not None, 'positions list is None, should be 0 entry map'
    assert len(context.pm.list_positions()) == 0, 'positions list is not empty'


@given('a new executed order is available')
def step_impl(context):
    context.executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, 'buy'), 1.1, 100)


@then('executed order can be appended to Portfolio Manager')
def step_impl(context):
    context.pm.append_position(context.executed_order)


@given('executed order is appended to Portfolio Manager')
def step_impl(context):
    context.pm.append_position(context.executed_order)


@then('Portfolio Manager yields non-empty position list')
def step_impl(context):
    assert len(context.pm.list_positions()) > 0, 'position list is empty'


@then('Portfolio Manager yields positions list with number of items = {num_of_pos}')
def step_impl(context, num_of_pos):
    assert len(context.pm.list_positions()) == int(num_of_pos), \
        'position list has [%s] items, expecting [%s] items' % (len(context.pm.list_positions()), num_of_pos)


@then('Portfolio Manager yields empty executions list')
def step_impl(context):
    assert context.pm.list_executions() is not None, 'executions list is None, should be 0 entry list'
    assert len(context.pm.list_executions()) == 0, 'executions list is not empty'


@then('Portfolio Manager yields non-empty executions list')
def step_impl(context):
    assert len(context.pm.list_executions()) > 0, 'executions list is empty'


@given('a new executed order is available to {side} {units} units')
def step_impl(context, side, units):
    context.executed_order = ExecutedOrder(OrderEvent('CHF_USD', 100, side), 1.1, int(units))


@then('Portfolio Manager yields executions list with number of items = {num_of_pos}')
def step_impl(context, num_of_pos):
    assert len(context.pm.list_executions()) == int(num_of_pos), \
        'executions list has [%s] items, expecting [%s] items' % (len(context.pm.list_executions()), num_of_pos)


@then('Portfolio Manager yields positions list with units = {units}')
def step_impl(context, units):
    assert context.pm.list_position(context.executed_order.order.instrument) == int(units), \
        'position list has [%s] items, expecting [%s] units' % (len(context.pm.list_positions()), units)
