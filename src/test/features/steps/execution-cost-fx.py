from behave import *
from com.open.algo.trading.fxCostPredictor import FxSpreadCostEvaluator
from com.open.algo.trading.fxEvents import TickEvent, OrderEvent
from com.open.algo.model import gettime
import queue


@given('Queue for market rates is initialized')
def step_impl(context):
    context.rates_events = queue.Queue()


@given('Cost Predictor is initialized')
def step_impl(context):
    context.cost_predictor = FxSpreadCostEvaluator(context.rates_events)


@when('a new order arrives')
def step_impl(context):
    context.response = None
    context.order = OrderEvent('CHF_USD', 100, 'buy')


@then('Cost Predictor gives error')
def step_impl(context):
    context.cost_predictor.pull_process()
    try:
        context.cost_predictor.eval_cost(context.order)
        assert False, 'there should not be any tick read received by cost evaluator hence no spreads to calculate cost'
    except KeyError:
        pass

@when('a new tick arrives')
def step_impl(context):
    context.response = None
    context.tick = TickEvent('CHF_USD', gettime(), 1.0, 1.0)
    context.rates_events.put(context.tick)


@then('Cost Predictor has last event same as arrived tick')
def step_impl(context):
    context.cost_predictor.pull_process()
    assert context.cost_predictor.get_last_tick() == context.tick


# to refactor slippage into a separate class, test etc

@given('Slippage Calculator is initialized')
def step_impl(context):
    context.slippage_calculator = None


@then('Slippage Calculator gives no output')
def step_impl(context):
    pass


@then('Cost Predictor has last spread based on last tick')
def step_impl(context):
    context.cost_predictor.pull_process()
    assert context.cost_predictor.get_last_spread(context.tick.instrument) == context.tick.ask - context.tick.bid, \
        'expecting last spread [%s] found [%s]' % \
        (context.cost_predictor.get_last_spread(context.tick.instrument), context.tick.ask - context.tick.bid)


@then('Cost Predictor can evaluate cost = {cost}')
def step_impl(context, cost):
    context.cost_predictor.pull_process()
    order = context.orderEvent
    evaluated = context.cost_predictor.eval_cost(order)
    assert evaluated == float(cost), 'wrongly evaluated cost to be [%s], expected [%s]' % (evaluated, cost)
