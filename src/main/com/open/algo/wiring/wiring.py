__author__ = 'ManuGarg'

from com.open.algo.oanda.streaming import OandaEventStreamer
from com.open.algo.wiring.eventLoop import EventLoop
from com.open.algo.oanda.environments import ENVIRONMENTS
from com.open.algo.utils import read_settings
from com.open.algo.trading.fxPricesCache import FxPricesCache, DEFAULT_ACCEPTABLE_TICK_AGE
from com.open.algo.wiring.queue_spmc import *


class WireRateCache:

    def __init__(self):
        self.rates_q = None
        self.heartbeat_q = None
        self.exception_q = None
        self.forward_q = None
        self.journaler = None
        self.target_env = None
        self.config_path = None
        self.max_tick_age = DEFAULT_ACCEPTABLE_TICK_AGE

    def wire(self):
        domain = ENVIRONMENTS['streaming'][self.target_env]
        settings = read_settings(self.config_path, self.target_env)

        rates_streamer = OandaEventStreamer(
            domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID'], self.journaler)
        rates_streamer.set_instruments('EUR_USD')
        rates_streamer.set_events_q(self.rates_q).set_heartbeat_q(self.heartbeat_q).set_exception_q(self.exception_q)

        rates_cache = FxPricesCache(max_tick_age=self.max_tick_age)
        rates_cache_loop = EventLoop(self.rates_q, rates_cache, forward_q=self.forward_q)

        return rates_streamer, rates_cache_loop

    # setup queues
    def set_rates_q(self, rates_q):
        self.rates_q = rates_q
        return self

    def set_heartbeat_q(self, heartbeat_q):
        self.heartbeat_q = heartbeat_q
        return self

    def set_exception_q(self, exception_q):
        self.exception_q = exception_q
        return self

    def set_forward_q(self, forward_q):
        self.forward_q = forward_q
        return self

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
        self.portfolio_q = None
        self.execution_q = None

    def wire(self):
        portfolio = FxPortfolio(self.portfolio_ccy, self.portfolio_balance
                                , port_limit=self.portfolio_limit, port_limit_short=self.portfolio_limit_short)

        ccy_exposure_manager = \
            CcyExposureLimitRiskEvaluator(self.portfolio_ccy, self.prices_cache, ccy_limit=10000, ccy_limit_short=-10000)

        portfolio.set_price_cache(self.prices_cache).set_ccy_exposure_manager(ccy_exposure_manager)
        rm = FxPositionLimitRiskEvaluator(posLimit=10000, posLimitShort=-10000)
        portfolio.add_risk_manager(rm)

        portfolio_loop = EventLoop(self.portfolio_q, portfolio, processed_event_q=self.execution_q)
        return portfolio_loop

    # setup queues
    def set_portfolio_q(self, portfolio_q):
        self.portfolio_q = portfolio_q
        return self

    def set_execution_q(self, execution_q):
        self.execution_q = execution_q
        return self

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
        self.execution_result_q = None
        self.execution_q = None
        self.journaler = None

        self.target_env = None
        self.config_path = None

    def wire(self):
        domain = ENVIRONMENTS['api'][self.target_env]
        settings = read_settings(self.config_path, self.target_env)
        executor = OandaExecutionHandler(domain, settings['ACCESS_TOKEN'], settings['ACCOUNT_ID'], self.journaler)

        execution_loop = EventLoop(self.execution_q, executor, processed_event_q=self.execution_result_q)
        return execution_loop

    # setup queues
    def set_execution_result_q(self, execution_result_q):
        self.execution_result_q = execution_result_q
        return self

    def set_execution_q(self, execution_q):
        self.execution_q = execution_q
        return self

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
        self.ticks_and_ack_q = None
        self.signal_output_q = None
        self.strategy = None

    def wire(self):
        strategy_loop = EventLoop(self.ticks_and_ack_q, self.strategy, processed_event_q=self.signal_output_q)
        return strategy_loop

    # setup queues
    def set_ticks_and_ack_q(self, ticks_and_ack_q):
        self.ticks_and_ack_q = ticks_and_ack_q
        return self

    def set_signal_output_q(self, signal_output_q):
        self.signal_output_q = signal_output_q
        return self

    def set_strategy(self, strategy):
        self.strategy = strategy
        return self


class WireAll:
    def __init__(self):
        self.rates_q = None
        self.heartbeat_q = None
        self.exception_q = None
        self.portfolio_q = None
        self.execution_q = None
        self.ticks_and_ack_q = None
        self.journaler = None
        self.max_tick_age = DEFAULT_ACCEPTABLE_TICK_AGE
        self.target_env = None
        self.config_path = None
        self.strategy = None
        self.port_wiring = WirePortfolio()
        self.execution_ack_nack_q = None

    def wire(self):
        rates_wiring = WireRateCache()
        rates_wiring.set_max_tick_age(self.max_tick_age)
        rates_wiring.set_rates_q(self.rates_q).set_forward_q(self.ticks_and_ack_q).set_journaler(self.journaler)
        rates_wiring.set_heartbeat_q(self.heartbeat_q).set_exception_q(self.exception_q)
        rates_wiring.set_target_env(self.target_env).set_config_path(self.config_path)
        rates_streamer, rates_cache_loop = rates_wiring.wire()

        self.port_wiring.set_portfolio_q(self.portfolio_q).set_execution_q(self.execution_q)
        self.port_wiring.set_prices_cache(rates_cache_loop.handler)
        portfolio_loop = self.port_wiring.wire()

        self.execution_ack_nack_q = QueueSPMC(self.journaler)
        self.execution_ack_nack_q.add_consumer(self.portfolio_q, timeout=5)
        self.execution_ack_nack_q.add_consumer(self.ticks_and_ack_q, timeout=5)

        executor_wiring = WireExecutor().set_journaler(self.journaler)
        executor_wiring.set_execution_q(self.execution_q)
        executor_wiring.set_target_env(self.target_env).set_config_path(self.config_path)
        executor_wiring.set_execution_result_q(self.execution_ack_nack_q)
        execution_loop = executor_wiring.wire()

        strategy_wiring = WireStrategy().set_strategy(self.strategy)
        strategy_wiring.set_signal_output_q(self.portfolio_q).set_ticks_and_ack_q(self.ticks_and_ack_q)
        strategy_loop = strategy_wiring.wire()

        return rates_streamer, rates_cache_loop, portfolio_loop, execution_loop, strategy_loop

    def set_portfolio_q(self, portfolio_q):
        self.portfolio_q = portfolio_q
        return self

    def set_execution_q(self, execution_q):
        self.execution_q = execution_q
        return self

    def set_ticks_and_ack_q(self, ticks_and_ack_q):
        self.ticks_and_ack_q = ticks_and_ack_q
        return self

    # setup queues
    def set_rates_q(self, rates_q):
        self.rates_q = rates_q
        return self

    def set_heartbeat_q(self, heartbeat_q):
        self.heartbeat_q = heartbeat_q
        return self

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
