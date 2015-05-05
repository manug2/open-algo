import importlib
import os
from time import gmtime, strftime
from abc import ABCMeta, abstractmethod

from configparser import ConfigParser
from queue import Empty
import sys
from logging import DEBUG
from com.open.algo.model import ExceptionEvent

class DynamicLoader(object):
    def load(self, realtivePath):
        my_module = importlib.import_module(realtivePath)
        return my_module

    def loadFromPath(self, path, name, dictionary):
        if len(path.strip()) > 0:
            fPath = path + '/' + name
        else:
            fPath = name

        if not fPath.endswith('.py'):
            fPath = fPath + '.py'

        loadedDict = {}
        with open(fPath, 'r') as file:
            code = compile(file.read(), fPath, 'exec', dont_inherit=True)
            exec(code, dictionary, loadedDict)
        return loadedDict


def read_settings(path, env):
    config = ConfigParser()
    cf = os.path.join(path, env + '.oanda.config')
    config.read(cf)
    settings = config['CONFIG']
    return settings


# journaler
class Journaler(object):
    def __init__(self):
        self.lastEvent = None

    @abstractmethod
    def logEvent(self, event):
        print('%s -> %s' % (strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()), event))
        self.lastEvent = event

    @abstractmethod
    def getLastEvent(self):
        return self.lastEvent

    @abstractmethod
    def log_message(self, message, level=DEBUG):
        print(message)


class EventLoop(object):
    def __init__(self, events_q, handler, heartbeat=0.1, journaler=None, exceptions_q=None):
        assert heartbeat > 0, 'Expecting [%s] to be > 0, found [%s]' % ('heartbeat', heartbeat)
        self.heartbeat = heartbeat
        assert events_q is not None, 'Expecting [%s] to be not None, found [%s]' % ('events queue', events_q)
        self.events_q = events_q
        assert handler is not None, 'Expecting [%s] to be not None, found [%s]' % ('event handler', handler)
        self.handler = handler
        self.started = False
        self.journaler = journaler
        self.exceptions_q = exceptions_q

    def start(self):
        """
        Carries out an infinite while loop.
        Polls events queue and directs each event to handler.
        The loop will then pause for "heartbeat" seconds and continue.
        """
        if self.journaler is not None:
            self.journaler.log_message('starting..')
        self.started = True
        self.handler.start()
        self.run_in_loop()

    def run_in_loop(self):
        while self.started:
            # outer while loop will trigger inner while loop after 'heartbeat'
            if self.journaler is not None:
                self.journaler.log_message('run_in_loop..')
            self.pull_process()
        if self.journaler is not None:
            self.journaler.log_message('stopped!')


    def pull_process(self):
        while self.started:
            # while loop to poll for events
            try:
                event = self.events_q.get(True, self.heartbeat)
            except Empty:
                break
            else:
                if self.journaler is not None:
                    self.journaler.logEvent(event)
                if event is not None:
                    try:
                        self.handler.process(event)
                    except:
                        err_msg = 'Unexpected error-%s' % sys.exc_info()[0]
                        if self.journaler is not None:
                            self.journaler.log_message(err_msg)
                        if self.exceptions_q is not None:
                            self.exceptions_q.put(ExceptionEvent(str(self), err_msg, event))
                        else:
                            print(err_msg)
        # end of while loop after collecting all events in queue

    def stop(self):
        if self.journaler is not None:
            self.journaler.log_message('stopping..')
        self.started = False
        self.handler.stop()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '%s[%s]' % (self.__class__.__name__, self.handler)

# End of EventLoop


class EventHandler(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def start(self):
        print('Nothing to start!')

    @abstractmethod
    def stop(self):
        print('Nothing to stop!')

    @abstractmethod
    def process(self, event):
        raise NotImplementedError('"process" is not implemented, cannot process [%s]' % event)

    def __init__(self):
        self.logger = None

    def __str__(self):
        return self.__class__.__name__

