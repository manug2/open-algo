import datetime
import importlib
import os
from time import gmtime, strftime
from abc import ABCMeta, abstractmethod

from configparser import ConfigParser
from logging import DEBUG


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


def get_time(offset=None):
    now = datetime.datetime.now()
    if offset is None:
        return now.strftime("%Y-%m-%dT%H:%M:%S.000000Z")
    else:
        now = now + datetime.timedelta(seconds=offset)
        return now.strftime("%Y-%m-%dT%H:%M:%S.000000Z")


