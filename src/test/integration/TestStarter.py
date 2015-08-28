import sys

sys.path.append('../../main')
sys.path.append('../../../../fx-oanda')
import unittest
from threading import Thread
from time import sleep
from com.open.algo.wiring.starter import *


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


class DummyWorker:
    def __init__(self, name):
        self.name = name

    def do_work(self):
        for i in range (0, 5):
            logger.info('%s->%d..', self.name, i)
            sleep(0.2)


worker1 = DummyWorker('w1')
worker2 = DummyWorker('w2')


class Test2InParallel(unittest.TestCase):

    def test_2_parallel_workers(self):
        t1 = Thread(target=worker1.do_work)
        t2 = Thread(target=worker2.do_work)

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
        starter = ThreadStarter()
        starter.add_target(worker1.do_work).add_target(worker2.do_work)

        logger.info('starting..')
        starter.start()
        logger.info('joining..')
        starter.join()
        logger.info('finished!')

    def test_start_2_parallel_workers_in_default_group(self):
        starter = ProcessStarter()
        starter.add_target(worker1.do_work)
        starter.add_target(worker2.do_work)

        logger.info('starting..')
        starter.start()
        logger.info('joining..')
        starter.join()
        logger.info('finished!')

    def test_start_2_parallel_workers_in_one_group(self):
        starter = ProcessStarter()
        starter.add_target(worker1.do_work, process_group='test_proc')
        starter.add_target(worker2.do_work, process_group='test_proc')

        logger.info('starting..')
        starter.start()
        logger.info('joining..')
        starter.join()
        logger.info('finished!')

    def test_start_2_parallel_workers_with_one_each_in_separate_group(self):
        starter = ProcessStarter()
        starter.add_target(worker1.do_work, process_group='test_proc1')
        starter.add_target(worker2.do_work, process_group='test_proc2')

        logger.info('starting..')
        starter.start()
        logger.info('joining..')
        starter.join()
        logger.info('finished!')

    def test_start_2_parallel_workers_with_2_each_in_separate_group(self):
        starter = ProcessStarter()
        starter.add_target(DummyWorker('w11'), process_group='test_proc1')
        starter.add_target(DummyWorker('w12'), process_group='test_proc1')
        starter.add_target(DummyWorker('w21'), process_group='test_proc2')
        starter.add_target(DummyWorker('w22'), process_group='test_proc2')

        logger.info('starting..')
        starter.start()
        logger.info('joining..')
        starter.join()
        logger.info('finished!')

    def test_ThreadStarter_should_allow_different_group_targets(self):
        starter = ThreadStarter()
        starter.add_target(worker1.do_work, 'w1')
        try:
            starter.add_target(worker2.do_work, 'w2')
        except:
            self.fail('should not have raised exception')

    def test_ThreadStarter_should_allow_same_group_targets(self):
        starter = ThreadStarter()
        starter.add_target(worker1.do_work, 'w1')
        try:
            starter.add_target(worker2.do_work, 'w1')
        except:
            self.fail('should not have raised exception')

