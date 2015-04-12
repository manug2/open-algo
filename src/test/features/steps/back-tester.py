from behave import *
import queue


@given('we have a back tester initialized')
def step_impl(context):
    context.backTester = None
    context.events = queue.Queue()


@then('tester gives no output')
def step_impl(context):
    pass
