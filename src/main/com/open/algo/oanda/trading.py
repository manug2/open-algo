import queue
import time
import threading
import os
import sys
import configparser
import importlib

sys.path.append('../../../..')

from optparse import OptionParser

from com.open.algo.oanda.environments import COMPONENT_CONFIG_PATH, STRATEGY_CONFIG_PATH, CONFIG_PATH
from com.open.algo.oanda.environments import ENVIRONMENTS
from com.open.algo.utils import DynamicLoader


def main():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-b", "--displayHeartBeat", dest="verbose", action="store_true", default=False
                      , help="Display HeartBeat in streaming data")
    parser.add_option("-e", "--environment", dest="env", action="store", default="practice"
                      , help="sandbox, practice or real")
    parser.add_option("-s", "--settingFile", dest="settingFile", action="store_true", default="oanda.config"
                      , help="name of settings file to configure TradeBot settings")
    parser.add_option("-p", "--paramFile", dest="paramFile", action="store"
                      , help="name of parameters file to configure strategy")
    parser.add_option("-c", "--componentFile", dest="componentFile", action="store", default="oandaComponents"
                      , help="name of components file to create components dynamically")

    (options, args) = parser.parse_args()
    print(options)

    settingFile = options.env + "." + options.settingFile

    config = configparser.ConfigParser()
    config.read(os.path.join(CONFIG_PATH, settingFile))
    print("Using 'settingFile' :", settingFile, " loaded following values :")
    # print ( config.sections())
    #print ( config.options('CONFIG'))


    #Set access variables for use in setting up streaming and execution
    ACCESS_TOKEN = config.get('CONFIG', 'ACCESS_TOKEN')
    ACCOUNT_ID = config.get('CONFIG', 'ACCOUNT_ID')

    #Set target instruments for use in setting up streaming and execution
    #May be revised to feed from back tester
    INSTRUMENTS = config.get('CONFIG', 'INSTRUMENTS')
    UNITS = config.get('CONFIG', 'UNITS')
    print(ACCESS_TOKEN, ACCOUNT_ID, INSTRUMENTS, UNITS)

    #Set domain variables for use in setting up streaming and execution
    STREAM_DOMAIN = ENVIRONMENTS["streaming"][options.env]
    API_DOMAIN = ENVIRONMENTS["api"][options.env]

    #Import oanda pricing, execution and trade bot components using speicifed componeny file
    components = DynamicLoader.loadFromPath(COMPONENT_CONFIG_PATH, options.componentFile)
    print(components.__dict__)

    #Create two separate threads:
    #One for trading loop
    #Another for market price streaming
    #trade_thread = threading.Thread(target=trade, args=(events, strategy, execution))
    #price_thread = threading.Thread(target=prices.stream_to_queue, args=[])

    #Start both threads
    #trade_thread.start()
    #price_thread.start()


if __name__ == "__main__":
    main()


