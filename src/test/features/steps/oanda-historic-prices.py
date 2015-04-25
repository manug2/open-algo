import sys

sys.path.append('../main/')
import queue

from com.open.algo.utils import Journaler
from com.open.algo.oanda.history import *
from com.open.algo.oanda.environments import ENVIRONMENTS

from behave import *

@when('i say query prices for {instrument}')
def step_impl(context, instrument):
    context.response = None
    context.journaler = Journaler()
    domain = ENVIRONMENTS[context.connection][context.env]
    context.events = queue.Queue()
    context.exceptions = queue.Queue()
    context.prices = HistoricForexPrices(
        domain, context.token, context.account_id,
        context.events, context.journaler, context.exceptions
    )
    context.prices.query(instrument)

