__author__ = 'ManuGarg'

import os, sys
from optparse import OptionParser
from scripts import prices_collector


if __name__ == '__main__':
    print('starting process %s-%s, for [%s]' % (os.getppid(), os.getpid(), 'collect_prices'))
    parser = OptionParser()
    parser.add_option("-t", "--time", type="int", dest="collection_duration", default=1*60)
    parser.add_option("-i", "--instruments", type="string", dest="instruments", default='EUR_USD')
    # parser.add_option("-d", "--debug", action="store_true", dest="debug", default=False)
    parser.add_option("-s", "--monitor_interval", type="int", dest="sleepy", default=10)
    parser.add_option("-f", "--file_path", type="string", dest="file_path", default='prices_collected_tp.txt')

    (options, args) = parser.parse_args()
    print('using settings =>', options)
    from queue import Queue as QueueClass
    from com.open.algo.wiring.starter import ThreadStarter as StarterClass

    try:
        prices_collector.collect(options.collection_duration, options.instruments, options.sleepy, options.file_path,
                                 StarterClass, QueueClass)
    except:
        print('Unexpected error:', sys.exc_info()[0])
    finally:
        print('completed collection!')
    print('stopping process %s-%s, for [%s]' % (os.getppid(), os.getpid(), 'collect_prices_tp'))
