__author__ = 'ManuGarg'

from com.open.algo.oanda.streaming import OandaEventStreamer
from com.open.algo.wiring.eventLoop import EventLoop
from com.open.algo.oanda.environments import ENVIRONMENTS
from com.open.algo.utils import read_settings
from com.open.algo.trading.fxPricesCache import FxPricesCache, DEFAULT_ACCEPTABLE_TICK_AGE
from com.open.algo.wiring.queue_spmc import *
from com.open.algo.wiring.commandListener import QueueCommandListener


class WireOandaPrices:

    def __init__(self):
        self.journaler = None
        self.target_env = None
        self.config_path = None
        self.instruments = 'EUR_USD'

    def wire(self, com_q=None, in_q=None, out_q=None, hb_q=None, e_q=None):
        domain = ENVIRONMENTS['streaming'][self.target_env]
        settings = read_settings(self.config_path, self.target_env)

        rates_streamer = OandaEventStreamer(
            domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID'], self.journaler)
        rates_streamer.set_instruments(self.instruments)
        rates_streamer.set_events_q(out_q).set_heartbeat_q(hb_q).set_exception_q(e_q)

        if com_q:
            listener = QueueCommandListener(com_q, rates_streamer.on_command)
            return rates_streamer, listener
        else:
            # Not required to return anything, but streamer reference can be used in shut down
            return rates_streamer

    def set_journaler(self, journaler):
        self.journaler = journaler
        return self

    # setup config file details and environment to connect to
    def set_target_env(self, target_env):
        self.target_env = target_env
        return self

    def set_config_path(self, config_path):
        self.config_path = config_path
        return self

    def set_instruments(self, instruments):
        self.instruments = instruments
        return self


class WireRateCache:

    def __init__(self):
        self.max_tick_age = DEFAULT_ACCEPTABLE_TICK_AGE
        self.component = None

    def wire(self, com_q=None, in_q=None, out_q=None, hb_q=None, e_q=None):
        rates_cache = FxPricesCache(max_tick_age=self.max_tick_age)
        rates_cache_loop = EventLoop(events_q=in_q, handler=rates_cache, forward_q=out_q)
        rates_cache_loop.set_command_q(com_q)
        self.component = rates_cache
        return rates_cache_loop

    def set_max_tick_age(self, max_tick_age):
        self.max_tick_age = max_tick_age
        return self


from com.open.algo.trading.fxPortfolio import *
from com.open.algo.risk.ccyExposureLimitRisk import CcyExposureLimitRiskEvaluator
from com.open.algo.risk.fxPositionLimitRisk import FxPositionLimitRiskEvaluator


class WirePortfolio:

    def __init__(self):
        self.portfolio_ccy = None
        self.portfolio_balance = None
        self.portfolio_limit = None
        self.portfolio_limit_short = None
        self.prices_cache = None

    def wire(self, com_q=None, in_q=None, out_q=None, hb_q=None, e_q=None):
        portfolio = FxPortfolio(self.portfolio_ccy, self.portfolio_balance
                                , port_limit=self.portfolio_limit, port_limit_short=self.portfolio_limit_short)

        ccy_exposure_manager = \
            CcyExposureLimitRiskEvaluator(self.portfolio_ccy, self.prices_cache, ccy_limit=10000, ccy_limit_short=-10000)

        portfolio.set_price_cache(self.prices_cache).set_ccy_exposure_manager(ccy_exposure_manager)
        rm = FxPositionLimitRiskEvaluator(posLimit=10000, posLimitShort=-10000)
        portfolio.add_risk_manager(rm)

        portfolio_loop = EventLoop(in_q, portfolio, processed_event_q=out_q)
        portfolio_loop.set_command_q(com_q)
        return portfolio_loop

    def set_portfolio_ccy(self, portfolio_ccy):
        self.portfolio_ccy = portfolio_ccy
        return self

    def set_portfolio_balance(self, portfolio_balance):
        self.portfolio_balance = portfolio_balance
        return self

    def set_portfolio_limit(self, portfolio_limit):
        self.portfolio_limit = portfolio_limit
        return self

    def set_portfolio_limit_short(self, portfolio_limit_short):
        self.portfolio_limit_short = portfolio_limit_short
        return self

    def set_prices_cache(self, prices_cache):
        self.prices_cache = prices_cache
        return self


from com.open.algo.oanda.execution import OandaExecutionHandler


class WireExecutor:

    def __init__(self):
        self.command_q = None
        self.execution_result_q = None
        self.execution_q = None
        self.journaler = None

        self.target_env = None
        self.config_path = None

    def wire(self, com_q=None, in_q=None, out_q=None, hb_q=None, e_q=None):
        domain = ENVIRONMENTS['api'][self.target_env]
        settings = read_settings(self.config_path, self.target_env)
        executor = OandaExecutionHandler(domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID'], self.journaler)

        execution_loop = EventLoop(in_q, executor, processed_event_q=out_q)
        execution_loop.set_command_q(com_q)
        return execution_loop

    # setup config file details and environment to connect to
    def set_target_env(self, target_env):
        self.target_env = target_env
        return self

    def set_config_path(self, config_path):
        self.config_path = config_path
        return self

    def set_journaler(self, journaler):
        self.journaler = journaler
        return self


class WireStrategy:

    def __init__(self):
        self.command_q = None
        self.strategy = None

    def wire(self, com_q=None, in_q=None, out_q=None, hb_q=None, e_q=None):
        strategy_loop = EventLoop(in_q, self.strategy, processed_event_q=out_q)
        strategy_loop.set_command_q(com_q)
        return strategy_loop

    def set_strategy(self, strategy):
        self.strategy = strategy
        return self


from copy import copy


class WireAll:

    def __init__(self):
        self.rates_q = Queue()
        self.portfolio_q = Queue()
        self.execution_q = Queue()
        self.ticks_and_ack_q = Queue()
        self.journaler = None
        self.max_tick_age = DEFAULT_ACCEPTABLE_TICK_AGE
        self.target_env = None
        self.config_path = None
        self.strategy = None
        self.port_wiring = WirePortfolio()
        self.execution_ack_nack_q = Queue()

    def wire(self, command_q=None, in_q=None, out_q=None, hb_q=None, e_q=None):
        if command_q and not in_q:
            raise ValueError('both "command_q" and "in_q" should be None, or both not None')

        command_q_for_cloning = in_q

        prices_wiring = WireOandaPrices()
        prices_wiring.set_journaler(self.journaler)
        prices_wiring.set_target_env(self.target_env).set_config_path(self.config_path)

        rates_cache_wiring = WireRateCache()
        rates_cache_wiring.set_max_tick_age(self.max_tick_age)

        self.execution_ack_nack_q = QueueSPMC(self.journaler)
        self.execution_ack_nack_q.add_consumer(self.portfolio_q, timeout=5)
        self.execution_ack_nack_q.add_consumer(self.ticks_and_ack_q, timeout=5)

        executor_wiring = WireExecutor().set_journaler(self.journaler)
        executor_wiring.set_target_env(self.target_env).set_config_path(self.config_path)

        strategy_wiring = WireStrategy().set_strategy(self.strategy)

        if command_q:
            prices_command_q = copy(command_q_for_cloning)
            rates_cache_command_q = copy(command_q_for_cloning)
            port_command_q = copy(command_q_for_cloning)
            executor_command_q = copy(command_q_for_cloning)
            strategy_command_q = copy(command_q_for_cloning)

            command_q.add_consumer(prices_command_q).add_consumer(rates_cache_command_q)\
                .add_consumer(port_command_q).add_consumer(executor_command_q).add_consumer(strategy_command_q)
        else:
            prices_command_q = None
            rates_cache_command_q = None
            port_command_q = None
            executor_command_q = None
            strategy_command_q = None

        # end of assigning command listener q

        rates_cache_loop = rates_cache_wiring.wire(com_q=rates_cache_command_q, in_q=self.rates_q,
                                           out_q=self.ticks_and_ack_q, hb_q=hb_q, e_q=e_q)

        self.port_wiring.set_prices_cache(rates_cache_loop.handler)
        portfolio_loop = self.port_wiring.wire(com_q=port_command_q, in_q=self.portfolio_q, out_q=self.execution_q,
                                               hb_q=hb_q, e_q=e_q)

        execution_loop = executor_wiring.wire(com_q=executor_command_q, in_q=self.execution_q,
                                           out_q=self.execution_ack_nack_q, hb_q=hb_q, e_q=e_q)

        strategy_loop = strategy_wiring.wire(com_q=strategy_command_q, in_q=self.ticks_and_ack_q,
                                           out_q=self.portfolio_q, hb_q=hb_q, e_q=e_q)

        if command_q:
            rates_streamer, rates_listener = prices_wiring.wire(com_q=prices_command_q, out_q=self.rates_q,
                                               hb_q=hb_q, e_q=e_q)
            return rates_streamer, rates_listener, rates_cache_loop, portfolio_loop, execution_loop, strategy_loop
        else:
            rates_streamer = prices_wiring.wire(out_q=self.rates_q, hb_q=hb_q, e_q=e_q)
            return rates_streamer, rates_cache_loop, portfolio_loop, execution_loop, strategy_loop

    # setup config file details and environment to connect to
    def set_target_env(self, target_env):
        self.target_env = target_env
        return self

    def set_config_path(self, config_path):
        self.config_path = config_path
        return self

    def set_journaler(self, journaler):
        self.journaler = journaler
        return self

    def set_max_tick_age(self, max_tick_age):
        self.max_tick_age = max_tick_age
        return self

    def set_strategy(self, strategy):
        self.strategy = strategy
        return self


import logging


def wire_logger():
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def wire_file_logger(file_path):
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(file_path)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger
