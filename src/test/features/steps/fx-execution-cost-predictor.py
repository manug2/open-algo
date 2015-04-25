from behave import *
from com.open.algo.trading.fxCostPredictor import FxSpreadCostEvaluator
from com.open.algo.trading.fxEvents import TickEvent, OrderEvent
from com.open.algo.model import gettime
import queue

@given('Cost Predictor is initialized')
def step_impl(context):
    context.events = queue.Queue()
    context.cost_predictor = FxSpreadCostEvaluator(context.events)

@when('a new order arrives')
def step_impl(context):
    context.response = None
    order = OrderEvent('CHF_USD', 100, 'buy')
    try:
        context.response = context.cost_predictor.eval_cost(order)
    except NotImplementedError as e:
        context.response = e.__class__.__name__

@then('Cost Predictor gives assertion error')
def step_impl(context):
    context.cost_predictor.pull_process()
    assert context.response == 'NotImplementedError', 'was this implemented without changing behaviour test'

@when('a new tick arrives')
def step_impl(context):
    context.response = None
    context.tick = TickEvent('CHF_USD', gettime(), 1.0, 1.0)
    context.events.put(context.tick)

@then('Cost Predictor has last event same as arrived tick')
def step_impl(context):
    context.cost_predictor.pull_process()
    assert context.cost_predictor.get_last_tick() == context.tick

# to refactor slippage into a separate class, test etc

@given('Slippage Calculator is initialized')
def step_impl(context):
    context.slippage_calculator = None
    context.events = queue.Queue()

@then('Slippage Calculator gives no output')
def step_impl(context):
    pass
