from behave import *
import time, threading


@given('bot is trading in a thread')
def step_impl(context):
    context.trade_thread = threading.Thread(target=context.trader_bot.start, args=[])
    context.trade_thread.start()


@when('bot trading thread is stopped')
def step_impl(context):
    context.trader_bot.stop()
    time.sleep(2*context.trader_bot.heartbeat)
