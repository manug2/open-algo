__author__ = 'ManuGarg'

import sys
sys.path.append('../src/main')

ENVIRONMENTS_CONFIG_PATH = '../../fx-oanda/'
OA_OUTPUT_DIR = '.'

from com.open.algo.journal import *
from com.open.algo.wiring.wiring import *
from com.open.algo.utils import COMMAND_STOP


def collect(duration, instruments, sleepy_time, file_path, StarterClass, QueueClass):

    from time import sleep

    logger = wire_logger()
    # wire_file_logger(os.path.join(OA_OUTPUT_DIR, 'EUR_USD.log'))

    logger.info('preparing journaler..')
    filename = os.path.join(OA_OUTPUT_DIR, file_path)
    journaler = FileJournaler(full_path=filename)
    journal_loop = EventLoop(journaler.events_q, journaler).set_process_all_on()
    # journaler = Journaler()

    logger.info('wiring oanda prices streaming..')
    wiring_prices = WireOandaPrices()
    wiring_prices.set_rates_q(QueueClass()).set_journaler(journaler)
    wiring_prices.set_target_env('practice').set_config_path(ENVIRONMENTS_CONFIG_PATH)
    wiring_prices.set_instruments(instruments)

    logger.info('wiring rates cache..')
    wiring_cache = WireRateCache()
    wiring_cache.set_rates_q(wiring_prices.rates_q)
    wiring_cache.set_max_tick_age(24*60*60)

    # for debugging over weekend
    wiring_cache.set_max_tick_age(150000)

    # setup command queues
    command_q = QueueSPMC(Journaler())
    command_q_streamer = QueueClass()
    command_q_journaler = QueueClass()
    command_q_cache = QueueClass()
    wiring_prices.set_command_q(command_q_streamer)
    wiring_cache.set_command_q(command_q_cache)
    journal_loop.set_command_q(command_q_journaler)
    command_q.add_consumer(command_q_streamer).add_consumer(command_q_cache).add_consumer(command_q_journaler)

    rates_streamer, stream_command_listener = wiring_prices.wire()
    rates_cache_loop = wiring_cache.wire()

    logger.info('adding targets to starter..')
    starter = StarterClass()
    starter.add_target(journal_loop.start, 'prices')
    starter.add_target(rates_streamer.stream, 'prices')
    starter.add_target(rates_cache_loop.start, 'prices')

    starter.add_target(stream_command_listener.start, 'prices')
    starter.add_target(rates_cache_loop.listener.start, 'prices')
    starter.add_target(journal_loop.listener.start, 'prices')

    total_duration = 0

    error = None

    try:
        logger.info('starting tasks..')
        starter.start()

        while total_duration < duration:
            sleep(sleepy_time)
            total_duration += sleepy_time
            # check futures here
            '''
            if journal_thread.is_alive() and rates_stream_thread.is_alive() \
                    and rates_cache_thread.is_alive():
                    logger.info('all threads are active..')
            else:
                error = 'a thread is not active'
                break
            '''
        logger.info('issuing stop command to all components..')
        command_q.put_nowait(COMMAND_STOP)
    except KeyboardInterrupt:
        logger.info('issuing stop command to all components after keyboard interrupt..')
        command_q.put_nowait(COMMAND_STOP)
    finally:
        logger.info('waiting for tasks to wrap up..')
        starter.join()
        # is closing journaler required, or should be moved to FileJournaler.stop()
        logger.info('closing journal..')
        journaler.close()

    if error:
        raise RuntimeError('error detected -> %s' % error)

    logger.info('thank you, journal file has been created at [%s]' % filename)
    return


if __name__ == '__main__':
    print('nothing to do..')
