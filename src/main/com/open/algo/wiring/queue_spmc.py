__author__ = 'ManuGarg'

import sys
from queue import Queue, Full, Empty
from com.open.algo.utils import get_time
from threading import Thread
from time import sleep

def prepare_journal(message, event, consumer_q):
    return '%s|consumer[%s]|%s' % (message, consumer_q, event)


def prepare_staging_journal(message, event, consumer_q):
    return '%s|staging[%s]|%s' % (message, consumer_q, event)


def parse_journal(jounral_entry):
    return str(jounral_entry).split('|')[2]


class QueueSPMC(Queue):
    """
    Single Producer Multiple Consumer Queue
    """
    def __init__(self, journaler, monitor_interval=0.5):
        super(Queue, self).__init__()
        self.consumer_queues = list()
        self.journaler = journaler
        self.consumer_timeout = list()
        self.consumer_thread = dict()
        self.staging_queues = list()

        self.monitor = False
        self.monitor_thread = None
        self.monitor_interval = monitor_interval

    def add_consumer(self, consumer_q, timeout=0.5):
        if consumer_q not in self.consumer_queues:
            self.consumer_queues.append(consumer_q)
            staging_queue = Queue()
            self.staging_queues.append(staging_queue)
            self.consumer_timeout.append(timeout)
        else:
            raise ValueError('consumer q already added to SPMC queue - [%s]' % consumer_q)

    def put_nowait(self, item):
        for q in self.consumer_queues:
            try:
                q.put_nowait(item)
            except Full:
                self.journaler.log_event(get_time(), prepare_journal('consumer q is full', item, q))

    def put(self, item, block=True, timeout=None):
        if not block:
            self.put_nowait(item)
            return
        if timeout is not None:
            print('timeout [%f] will be ignored and defaulted per consumer' % timeout)

        if not self.monitor:
            self.start()
        for sq in self.staging_queues:
            try:
                sq.put_nowait(item)
            except Full:
                self.journaler.log_event(get_time(), prepare_staging_journal('staging q is full', item, sq))

        self.submit()
        self.await_puts()

    def submit(self):
        for i in range(0, len(self.staging_queues)):
            staging_queue = self.staging_queues[i]
            try:
                item = staging_queue.get_nowait()
            except Empty:
                continue
            consumer_q = self.consumer_queues[i]
            consumer_timeout = self.consumer_timeout[i]
            consumer_qt = Thread(target=self._put_in_q, args=[consumer_q, item, consumer_timeout], name='cons_%s' % i)
            self.consumer_thread[i] = consumer_qt
            try:
                print('starting thread %s' % consumer_qt.getName())
                consumer_qt.start()
            except:
                self.journaler.log_event(get_time(), prepare_journal(sys.exc_info().args[0], item, consumer_q))

    def _put_in_q(self, q, item, timeout):
        try:
            q.put(item, True, timeout=timeout)
            print('successfully put item on queue [%s <- %s]' % (q, item))
        except Full:
            self.journaler.log_event(get_time(), prepare_journal('target queue was full', item, q))

    def await_puts(self):
        for i in range(0, len(self.staging_queues)):
            if i in self.consumer_thread:
                cq_t = self.consumer_thread[i]
                if cq_t is not None and cq_t.is_alive():
                    timeout = self.consumer_timeout[i]
                    cq_t.join(timeout)

    def stop(self):
        self.monitor = False
        self.consumer_queues.clear()
        self.consumer_timeout.clear()
        self.consumer_thread.clear()
        self.staging_queues.clear()

    def start(self):
        self.monitor = True
        self.monitor_thread = Thread(target=self.monitor_threads, args=[])
        self.monitor_thread.start()

    def monitor_threads(self):
        while self.monitor:
            for cq_t in self.consumer_thread.values():
                if cq_t.is_alive():
                    print('%s -> thread [%s] is alive..' % (self.__class__.__name__, cq_t.getName()))
            sleep(self.monitor_interval)
