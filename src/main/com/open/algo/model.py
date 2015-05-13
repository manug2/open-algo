from abc import ABCMeta, abstractmethod

from com.open.algo.utils import get_time


# FX Events Abstract Class
class Event:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.TYPE = None

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    def to_string(self):
        return self.__class__.__name__

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class ExceptionEvent(Event):
    def __init__(self, caller, message, orig_event=None):
        self.TYPE = 'EXCEPTION'
        self.caller = caller
        self.message = message
        self.time = get_time()
        self.orig_event = orig_event

    def __str__(self):
        if self.orig_event is None:
            return '%s(%s) from "%s"' % (self.TYPE, self.message, self.caller)
        else:
            return '%s(%s) from "%s" while processing event [%s]' % (self.TYPE, self.message, self.caller, self.orig_event)


# Classes that can log stuff
class Loggables:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.logger = None

    def __str__(self):
        return self.__class__.__name__

    def startLogging(self):
        if self.logger == None:
            import logging

            self.logger = logging.getLogger(self.__class__.__name__)

    def stopLogging(self):
        if self.logger != None:
            self.logger = None


# DataHandler Abstract Classes
class DataHandler(Loggables):
    def __init__(self):
        self.TYPE = None

    @abstractmethod
    def connect(self):
        raise NotImplementedError("Should implement 'connect()' method")


class StreamDataHandler(DataHandler):
    @abstractmethod
    def stream(self):
        raise NotImplementedError("Should implement 'stream()' method")

    @abstractmethod
    def stop(self):
        raise NotImplementedError("Should implement 'stream()' method")

    def get_latest_price(self, instrument):
        raise NotImplementedError("Should implement 'get_latest_price()' method")

    def get_historic_prices(self, instrument):
        raise NotImplementedError("Should implement 'get_historic_prices()' method")


# Execution Handler Abstract Class
class ExecutionHandler(Loggables):
    @abstractmethod
    def execute_order(self, event):
        raise NotImplementedError("Should implement 'execute_order()' method")

    @abstractmethod
    def get_orders(self, params=None):
        raise NotImplementedError("Should implement 'get_orders()' method")

    @abstractmethod
    def get_order(self, order_id):
        raise NotImplementedError("Should implement 'get_orders()' method")

    @abstractmethod
    def stop(self):
        raise NotImplementedError("Should implement 'stream()' method")


# Portfolio management
class Portfolio(Loggables):
    @abstractmethod
    def manage(self):
        raise NotImplementedError("Should implement 'manage()' method")

    @abstractmethod
    def stop(self):
        raise NotImplementedError("Should implement 'obtain_connection()' method")

    def list_positions(self):
        raise NotImplementedError("Should implement 'list_positions()' method")

    def close_all_positions(self):
        raise NotImplementedError("Should implement 'close_all_positions()' method")

    def close_position(self, instrument):
        raise NotImplementedError("Should implement 'close_positions()' method")

    def close_position_id(self, position_id):
        raise NotImplementedError("Should implement 'close_position()' method")

    def reval_position(self, instrument):
        raise NotImplementedError("Should implement 'reval_position()' method")

    def reval_positions(self):
        raise NotImplementedError("Should implement 'reval_positions()' method")

    def append_position(self, position):
        raise NotImplementedError("Should implement 'append_position()' method")

    def list_position(self, instrument):
        raise NotImplementedError("Should implement 'list_positions()' method")

    @abstractmethod
    def get_base_ccy(self):
        raise NotImplementedError("Should implement 'get_base_ccy()' method")


class RiskManager(Loggables):
    def filter_order(self, order):
        raise NotImplementedError("Should implement 'filter_order()' method")

    def reval_positions(self):
        raise NotImplementedError("Should implement 'reval_for_positions()' method")

    def append_position(self, position):
        raise NotImplementedError("Should implement 'append_position()' method")


class ExecutionCostPredictor(Loggables):
    def eval_cost(self, order):
        raise NotImplementedError("Should implement 'eval_cost()' method")


class MarketRateCache(Loggables):
    def get_rate(self, instrument):
        raise NotImplementedError("Should implement 'get_rate()' method")

    def start(self):
        raise NotImplementedError("Should implement 'start()' method")

    @abstractmethod
    def stop(self):
        raise NotImplementedError("Should implement 'stop()' method")


class CurrencyRiskManager(RiskManager):
    def get_base_ccy(self):
        raise NotImplementedError("Should implement 'get_base_ccy()' method")


class Heartbeat(Event):
    def __init__(self, alias):
        self.TYPE = 'HB'
        self.alias = alias

    def to_string(self):
        return '%s[%s]' % (self.__class__.__name__, self.alias)


