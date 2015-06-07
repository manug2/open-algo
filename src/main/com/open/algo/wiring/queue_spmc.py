__author__ = 'ManuGarg'

import sys
from queue import Queue, Full
from com.open.algo.utils import get_time
from threading import Thread


def prepare_journal(message, event, consumer_q):
    return '%s|consumer[%s]|%s' % (message, consumer_q, event)


def parse_journal(jounral_entry):
    return jounral_entry.split('|')[2]


class QueueSPMC(Queue):
    def __init__(self, journaler):
        super(Queue, self).__init__()
        self.queues = list()
        self.journaler = journaler
        self.consumer_thread = dict()


    def add_consumer(self, consumer_q):
        if consumer_q not in self.queues:
            self.queues.append(consumer_q)
        else:
            raise ValueError('consumer q already added to SPMC queue - [%s]' % consumer_q)

    def put_nowait(self, item):
        for q in self.queues:
            try:
                q.put_nowait(item)
            except Full:
                self.journaler.log_event(get_time(), prepare_journal('consumer q is full', item, q))

    def put(self, item, block=True, timeout=None):
        if not block:
            self.put_nowait(item)
            return

        for i in range(0, len(self.queues)):
            if self._is_previous_event_done(i):
                self._spawn_and_submit(i, item, timeout)
            else:
                self.journaler.log_event(get_time(), prepare_journal('busy sending last event', item, i))

    def _spawn_and_submit(self, i, item, timeout):
        q = self.queues[i]
        q_t = Thread(target=q.put, args=[item, True, timeout], name='cons_%s' % i)
        self.consumer_thread[i] = q_t
        try:
            q_t.start()
        except:
            self.journaler.log_event(get_time(), prepare_journal(sys.exc_info().args[0], item, q))

    def _is_previous_event_done(self, i):
        if i in self.consumer_thread:
            q_t = self.consumer_thread[i]
            if q_t.is_alive():
                return False
        return True