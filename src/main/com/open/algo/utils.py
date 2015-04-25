import imp, importlib
import os
from time import gmtime, strftime
from abc import ABCMeta, abstractmethod

from com.open.algo.model import Event


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

