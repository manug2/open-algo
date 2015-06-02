import datetime
import importlib
import os
from abc import ABCMeta, abstractmethod

from configparser import ConfigParser

OA_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
OA_TIME_FORMAT_ZERO_MILLIS = '%Y-%m-%dT%H:%M:%S.000000Z'

EVENT_TYPES_TICK = 'TICK'
EVENT_TYPES_ORDER = 'ORDER'
EVENT_TYPES_FILL = 'FILL'
EVENT_TYPES_FILTERED = 'FILTERED'
EVENT_TYPES_REJECTED = 'REJECTED'


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


# class that handles events run by EventLoop
class EventHandler:
    __metaclass__ = ABCMeta

    @abstractmethod
    def start(self):
        print('Nothing to start! - [%s]' % str(self))

    @abstractmethod
    def stop(self):
        print('Nothing to stop! - [%s]' % str(self))

    @abstractmethod
    def process(self, event):
        raise NotImplementedError('sub-class should implement "%s"' % 'process()')

    @abstractmethod
    def process_all(self, events):
        raise NotImplementedError('sub-class should implement "%s"' % 'process_all()')

    def __init__(self):
        pass

    def __str__(self):
        return self.__class__.__name__


def get_time(offset=None):
    now = datetime.datetime.now()
    if offset is None:
        return now.strftime(OA_TIME_FORMAT)
    else:
        now = now + datetime.timedelta(seconds=offset)
        return now.strftime(OA_TIME_FORMAT)


def get_time_with_zero_millis(offset=None):
    now = datetime.datetime.now()
    if offset is None:
        return now.strftime(OA_TIME_FORMAT_ZERO_MILLIS)
    else:
        now = now + datetime.timedelta(seconds=offset)
        return now.strftime(OA_TIME_FORMAT_ZERO_MILLIS)


def get_age_seconds(old_time, new_time=None):
    if old_time is None:
        raise ValueError('old time cannot be None for getting age - found [%s]' % old_time)

    datetime1 = datetime.datetime.strptime(old_time, OA_TIME_FORMAT)
    if new_time is None:
        datetime2 = datetime.datetime.now()
    else:
        datetime2 = datetime.datetime.strptime(new_time, OA_TIME_FORMAT)

    timedelta = datetime1 - datetime2
    return timedelta.total_seconds()




