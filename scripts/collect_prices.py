__author__ = 'ManuGarg'

import sys
sys.path.append('../src/main')
from optparse import OptionParser

ENVIRONMENTS_CONFIG_PATH = '../../fx-oanda/'
OA_OUTPUT_DIR = '../output/'

from com.open.algo.journal import *
from com.open.algo.wiring.wiring import *


def collect(duration, instruments, sleepy_time, file_path):

    from queue import Queue
    from threading import Thread
    from time import sleep

    # wire_file_logger(os.path.join(OA_OUTPUT_DIR, 'EUR_USD.log'))
    wire_logger()
    logger = logging.getLogger('')

    logger.info('preparing journaler..')
    filename = os.path.join(OA_OUTPUT_DIR, file_path)
    journal_q = Queue()
    journaler = FileJournaler(journal_q, full_path=filename)
    journal_loop = EventLoop(journal_q, journaler).set_process_all_on()
    # journaler = Journaler()

    logger.info('wiring oanda prices streaming..')
    wiring_prices = WireOandaPrices()
    wiring_prices.set_rates_q(Queue()).set_journaler(journaler)
    wiring_prices.set_target_env('practice').set_config_path(ENVIRONMENTS_CONFIG_PATH)
    wiring_prices.set_instruments(instruments)

    logger.info('wiring rates cache..')
    wiring_cache = WireRateCache()
    wiring_cache.set_rates_q(wiring_prices.rates_q)
    wiring_cache.set_max_tick_age(24*60*60)

    # for debugging over weekend
    wiring_cache.set_max_tick_age(150000)

    rates_streamer = wiring_prices.wire()
    rates_cache_loop = wiring_cache.wire()

    logger.info('creating threads..')
    journal_thread = Thread(target=journal_loop.start, args=[])
    rates_stream_thread = Thread(target=rates_streamer.stream)
    rates_cache_thread = Thread(target=rates_cache_loop.start)

    total_duration = 0

    logger.info('starting threads..')
    journal_thread.start()
    rates_stream_thread.start()
    rates_cache_thread.start()

    while total_duration < duration:
        sleep(sleepy_time)
        total_duration += sleepy_time
        if not journal_thread.is_alive():
            rates_streamer.stop()
            rates_cache_loop.stop()
            raise RuntimeError('journal thread is no more active')
        elif not rates_stream_thread.is_alive():
            rates_cache_loop.stop()
            journal_loop.stop()
            raise RuntimeError('rates streaming thread is no more active')
        elif not rates_cache_thread.is_alive():
            rates_streamer.stop()
            journal_loop.stop()
            raise RuntimeError('rates cache thread is no more active')
        else:
            logger.info('all threads are active..')

    logger.info('stopping threads..')
    rates_streamer.stop()
    rates_cache_loop.stop()
    journal_loop.stop()

    logger.info('waiting for threads to wrap up..')
    rates_stream_thread.join(timeout=sleepy_time)
    rates_cache_thread.join(timeout=sleepy_time)
    journal_thread.join(timeout=sleepy_time)
    logger.info('closing journal..')
    journaler.close()

    logger.info('checking whether all thread are now inactive..')
    if rates_stream_thread.is_alive():
        logger.warn('rates stream thread is still active')
    if rates_cache_thread.is_alive():
        logger.warn('rates cache thread is still active')
    if journal_thread.is_alive():
        logger.warn('journal thread is still active')

    logger.info('thank you, journal file has been created at [%s]' % filename)
    return


if __name__ == '__main__':
    print('starting process %s-%s, for [%s]' % (os.getppid(), os.getpid(), 'collect_prices'))
    parser = OptionParser()
    parser.add_option("-t", "--time", type="int", dest="collection_duration", default=1*60)
    parser.add_option("-i", "--instruments", type="string", dest="instruments", default='EUR_USD')
    # parser.add_option("-d", "--debug", action="store_true", dest="debug", default=False)
    parser.add_option("-s", "--monitor_interval", type="int", dest="sleepy", default=10)
    parser.add_option("-f", "--file_path", type="string", dest="file_path", default='prices.txt')

    (options, args) = parser.parse_args()
    print('using settings =>', options)
    try:
        collect(options.collection_duration, options.instruments, options.sleepy, options.file_path)
    except:
        print('Unexpected error:', sys.exc_info()[0])
    finally:
        print('completed collection!')
    print('stopping process %s-%s, for [%s]' % (os.getppid(), os.getpid(), 'collect_prices'))
