import sys, time

sys.path.append('../main/')
import queue, threading, time

from com.open.algo.utils import Journaler, DynamicLoader
from com.open.algo.oanda.streaming import *
from com.open.algo.oanda.environments import ENVIRONMENTS, COMPONENT_CONFIG_PATH

from behave import *


@given('we want to dynamically load module "{module}"')
def step_impl(context, module):
    context.module = module


@when('i say load given oanda components definition file')
def step_impl(context):
    globals()['STREAM_DOMAIN'] = ENVIRONMENTS['streaming'][context.env]
    globals()['API_DOMAIN'] = ENVIRONMENTS['api'][context.env]
    globals()['ACCOUNT_ID'] = context.account_id
    globals()['ACCESS_TOKEN'] = context.token
    globals()['INSTRUMENT'] = context.instrument
    globals()['UNITS'] = 1000

    context.myMod = DynamicLoader().loadFromPath(COMPONENT_CONFIG_PATH, context.module, globals())


@then('we can start thread "{thread_component}" for component "{component}"')
def step_impl(context, thread_component, component):
    c = context.myMod[component]
    t = context.myMod[thread_component]
    t.start()
    time.sleep(1)
    c.stop()
	
