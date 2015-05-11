import datetime
import importlib
import os
from abc import ABCMeta, abstractmethod

from configparser import ConfigParser


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
        if event is None:
            raise NotImplementedError('Cannot handle None event')
        else:
            print('Nothing to do, ignoring all events [%s]!' % event)
            return event

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


