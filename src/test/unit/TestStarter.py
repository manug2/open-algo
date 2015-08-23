import sys

sys.path.append('../../main')
sys.path.append('../../../../fx-oanda')
import unittest
from threading import Thread
from time import sleep
import logging
from com.open.algo.starter import *


def wire_logger():
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

logger = wire_logger()


def dummy_worker(name):

    for i in range (0, 5):
        logger.info('%s->%d..', name, i)
        sleep(1)


class Test2InParallel(unittest.TestCase):

    def test_2_parallel_workers(self):
        t1 = Thread(target=dummy_worker, args=['w1'])
        t2 = Thread(target=dummy_worker, args=['w2'])

        logger.info('starting t1..')
        t1.start()
        sleep(1)
        logger.info('starting t2..')
        t2.start()

        logger.info('waiting for thread t1 to finish..')
        t1.join()
        logger.info('waiting for thread t2 to finish..')
        t2.join()
        logger.info('finished!')

    def test_ThreadStarter_2_parallel_workers_in_default_group(self):
        starter = ThreadStarter('def', [(dummy_worker, ['w1']), (dummy_worker, ['w2'])])

        logger.info('starting..')
        starter.start()
        logger.info('joining..')
        starter.join()
        logger.info('finished!')

    def test_start_2_parallel_workers_in_default_group(self):
        starter = ProcessStarter()
        starter.add_target(dummy_worker, args=['w1'])
        starter.add_target(dummy_worker, args=['w2'])

        logger.info('starting..')
        starter.start_all()
        logger.info('joining..')
        starter.join_all()
        logger.info('finished!')

    def test_start_2_parallel_workers_in_one_group(self):
        starter = ProcessStarter()
        starter.add_target(dummy_worker, args=['w1'], process_group='test_proc')
        starter.add_target(dummy_worker, args=['w2'], process_group='test_proc')

        logger.info('starting..')
        starter.start_all()
        logger.info('joining..')
        starter.join_all()
        logger.info('finished!')

    def test_start_2_parallel_workers_with_one_each_in_separate_group(self):
        starter = ProcessStarter()
        starter.add_target(dummy_worker, args=['w1'], process_group='test_proc1')
        starter.add_target(dummy_worker, args=['w2'], process_group='test_proc2')

        logger.info('starting..')
        starter.start_all()
        logger.info('joining..')
        starter.join_all()
        logger.info('finished!')

    def test_start_2_parallel_workers_with_2_each_in_separate_group(self):
        starter = ProcessStarter()
        starter.add_target(dummy_worker, args=['w11'], process_group='test_proc1')
        starter.add_target(dummy_worker, args=['w12'], process_group='test_proc1')
        starter.add_target(dummy_worker, args=['w21'], process_group='test_proc2')
        starter.add_target(dummy_worker, args=['w22'], process_group='test_proc2')

        logger.info('starting..')
        starter.start_all()
        logger.info('joining..')
        starter.join_all()
        logger.info('finished!')

