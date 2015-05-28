from abc import ABCMeta, abstractmethod

from com.open.algo.utils import get_time, EventHandler
EVENT_TYPES_TICK = 'TICK'
EVENT_TYPES_ORDER = 'ORDER'
EVENT_TYPES_FILL = 'FILL'
EVENT_TYPES_FILTERED = 'FILTERED'
EVENT_TYPES_REJECTED = 'REJECTED'


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


# DataProvider Abstract Classes
class DataProvider():
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
class ExecutionHandler():
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
class Portfolio():
    @abstractmethod
    def manage(self):
        raise NotImplementedError("Should implement 'manage()' method")

    @abstractmethod
    def stop(self):
        raise NotImplementedError("Should implement 'obtain_connection()' method")

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

class RiskManager():
    def filter_order(self, order):
        raise NotImplementedError("Should implement 'filter_order()' method")

    def reval_positions(self):
        raise NotImplementedError("Should implement 'reval_for_positions()' method")

    def append_position(self, position):
        raise NotImplementedError("Should implement 'append_position()' method")


class ExecutionCostPredictor():
    def eval_cost(self, order):
        raise NotImplementedError("Should implement 'eval_cost()' method")


class MarketRateCache():
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


class Strategy(EventHandler):

    @abstractmethod
    def calculate_signals(self, event):
        raise NotImplementedError('sub-classes should implement this')

    @abstractmethod
    def get_open_interests(self):
        raise NotImplementedError('sub-classes should implement this')

    @abstractmethod
    def get_open_interest(self, instrument):
        raise NotImplementedError('sub-classes should implement this')

    @abstractmethod
    def get_signaled_positions(self):
        raise NotImplementedError('sub-classes should implement this')

    @abstractmethod
    def get_signaled_position(self, instrument):
        raise NotImplementedError('sub-classes should implement this')

    def process(self, event):
        if event.TYPE == EVENT_TYPES_TICK:
            self.calculate_signals(event)
        elif event.TYPE == EVENT_TYPES_FILL:
            self.acknowledge_execution(event)
        elif event.TYPE == EVENT_TYPES_FILTERED or event.TYPE == EVENT_TYPES_REJECTED:
            self.acknowledge_rejection(event)
        else:
            raise ValueError('Don\'t know how to handle event of type "%s" - [%s]' % (event.TYPE, event))

    @abstractmethod
    def acknowledge_execution(self, event):
        raise NotImplementedError('sub-classes should implement this')

    @abstractmethod
    def acknowledge_rejection(self, event):
        raise NotImplementedError('sub-classes should implement this')
