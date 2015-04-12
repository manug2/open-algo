from abc import ABCMeta, abstractmethod
from time import gmtime, strftime
import datetime


def gettime(offset=None):
    now = datetime.datetime.now()
    if offset == None:
        return now.strftime("%Y-%m-%dT%H:%M:%S.000000Z")
    else:
        now = now + datetime.timedelta(seconds=offset)
        return now.strftime("%Y-%m-%dT%H:%M:%S.000000Z")


# Forex Events Abstract Class
class Event:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.TYPE = None

    def __str__(self):
        return self.__class__.__name__


class ExceptionEvent(Event):
    def __init__(self, caller, message):
        self.TYPE = 'EXCEPTION'
        self.caller = caller
        self.message = message
        self.time = gettime()

    def __str__(self):
        return '%s(%s) from "%s"' % (self.TYPE, self.message, self.caller)


#Classes that can log stuff
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


#DataHandler Abstract Classes
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


#Execution Handler Abstract Class
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


#Generic trading engine
class TradeBot(Loggables):
    @abstractmethod
    def trade(self):
        raise NotImplementedError("Should implement 'obtain_connection()' method")

    @abstractmethod
    def stop(self):
        raise NotImplementedError("Should implement 'obtain_connection()' method")


#Portfolio management
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

    def close_positions(self, instrument):
        raise NotImplementedError("Should implement 'close_positions()' method")

    def close_position(self, position_id):
        raise NotImplementedError("Should implement 'close_position()' method")

    def reval_positions(self):
        raise NotImplementedError("Should implement 'reval_positions()' method")

    def append_position(self, position):
        raise NotImplementedError("Should implement 'append_position()' method")


class RiskManager(Loggables):
    def filter_order(self, order):
        raise NotImplementedError("Should implement 'filter_order()' method")

    def reval_positions(self):
        raise NotImplementedError("Should implement 'reval_for_positions()' method")

    def append_position(self, position):
        raise NotImplementedError("Should implement 'append_position()' method")

