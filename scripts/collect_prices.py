__author__ = 'ManuGarg'

import sys
sys.path.append('../src/main')
ENVIRONMENTS_CONFIG_PATH = '../../fx-oanda/'
OA_OUTPUT_DIR = '../output/'

from com.open.algo.journal import *
from com.open.algo.wiring.wiring import *


def collect(duration=1*60, instruments='EUR_USD', sleepy_time=10):

    from queue import Queue
    from threading import Thread
    from time import sleep

    # wire_file_logger(os.path.join(OA_OUTPUT_DIR, 'EUR_USD.log'))
    wire_logger()
    logger = logging.getLogger('')

    logger.info('preparing journaler..')
    filename = os.path.join(OA_OUTPUT_DIR, 'EUR_USD.txt')
    journal_q = Queue()
    journaler = FileJournaler(journal_q, full_path=filename)
    journal_loop = EventLoop(journal_q, journaler).set_process_all_on()
    # journaler = Journaler()

    logger.info('wiring rates cache..')
    wiring = WireRateCache()
    wiring.set_rates_q(Queue()).set_journaler(journaler)
    wiring.set_target_env('practice').set_config_path(ENVIRONMENTS_CONFIG_PATH)
    wiring.set_max_tick_age(24*60*60)
    wiring.set_instruments(instruments)

    rates_streamer, rates_cache_loop = wiring.wire()

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
            raise RuntimeError('journal thread is no more active')
        elif not rates_stream_thread.is_alive():
            raise RuntimeError('rates streaming thread is no more active')
        elif not rates_stream_thread.is_alive():
            raise RuntimeError('rates cache thread is no more active')
        else:
            logger.info('all threads are active..')

    logger.info('stopping threads..')
    rates_streamer.stop()
    rates_cache_loop.handler.stop()
    journal_loop.stop()

    logger.info('waiting for threads to wrap up..')
    rates_stream_thread.join(timeout=sleepy_time)
    rates_cache_thread.join(timeout=sleepy_time)
    journal_thread.join(timeout=sleepy_time)
    logger.info('closing journal..')
    journaler.close()
    logger.info('thank you, journal file has been created at [%s]' % filename)
    return

if __name__ == '__main__':
    try:
        collect()
    except:
        print('Unexpected error:', sys.exc_info()[0])
    finally:
        print('completed collection!')
