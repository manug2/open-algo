from abc import ABCMeta, abstractmethod

from com.open.algo.utils import get_time, EVENT_TYPES_EXCEPTION


# FX Events Abstract Class
class Event:
    __metaclass__ = ABCMeta

    def __init__(self, event_type):
        self.TYPE = event_type

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
        super(ExceptionEvent, self).__init__(EVENT_TYPES_EXCEPTION)
        self.caller = caller
        self.message = message
        self.time = get_time()
        self.orig_event = orig_event

    def __str__(self):
        if self.orig_event is None:
            return '%s(%s) from "%s"' % (self.TYPE, self.message, self.caller)
        else:
            return '%s(%s) from "%s" while processing event [%s]' % (self.TYPE, self.message, self.caller, self.orig_event)


# DataProvider Abstract Classes
class DataProvider():
    __metaclass__ = ABCMeta

    def __init__(self):
        self.TYPE = None

    @abstractmethod
    def connect(self):
        raise NotImplementedError("Should implement 'connect()' method")


class StreamDataProvider(DataProvider):
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
class ExecutionHandler:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

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
    def close_position(self, instrument):
        raise NotImplementedError("Should implement 'close_position()' method")


# Portfolio management
class Portfolio:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    def list_positions(self):
        raise NotImplementedError("Should implement 'list_positions()' method")

    def close_all_positions(self, executor):
        raise NotImplementedError("Should implement 'close_all_positions()' method")

    def close_position(self, executor, instrument):
        raise NotImplementedError("Should implement 'close_positions()' method")

    def close_position_id(self, executor, position_id):
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

    def check_and_issue_order(self, order):
        raise NotImplementedError("Should implement 'check_and_issue_order()' method")


class RiskManager:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    def filter_order(self, order):
        raise NotImplementedError("Should implement 'filter_order()' method")

    def reval_positions(self):
        raise NotImplementedError("Should implement 'reval_for_positions()' method")

    def append_position(self, position):
        raise NotImplementedError("Should implement 'append_position()' method")


class ExecutionCostPredictor:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    def eval_cost(self, order):
        raise NotImplementedError("Should implement 'eval_cost()' method")


class MarketRateCache:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

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
    def __init__(self, alias, receive_time, sent_time):
        super(Heartbeat, self).__init__('HB')
        self.alias = alias
        self.receive_time = receive_time
        self.sent_time = sent_time

    def to_string(self):
        return '%s[%s(received=%s, sent=%s)]' % (self.__class__.__name__, self.alias, self.receive_time, self.sent_time)

