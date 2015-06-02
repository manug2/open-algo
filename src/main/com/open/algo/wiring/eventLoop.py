__author__ = 'ManuGarg'

from queue import Empty, Full
import sys
from time import sleep

from com.open.algo.model import ExceptionEvent
from com.open.algo.utils import EventHandler


class EventLoop(object):
    def __init__(self, events_q, handler, heartbeat=0.1, exceptions_q=None, forward_q=None, processed_event_q=None):
        assert heartbeat > 0, 'Expecting [%s] to be > 0, found [%s]' % ('heartbeat', heartbeat)
        self.heartbeat = heartbeat
        assert events_q is not None, 'Expecting [%s] to be not None, found [%s]' % ('events queue', events_q)
        self.events_q = events_q
        assert handler is not None, 'Expecting [%s] to be not None, found [%s]' % ('event handler', handler)
        assert isinstance(handler, EventHandler), 'handler should be a sub-class of "%s", found to be of type "%s"' %\
                                                  (type(EventHandler), type(handler))
        self.handler = handler
        self.started = False
        self.exceptions_q = exceptions_q
        self.forward_q = forward_q
        self.processed_event_q = processed_event_q
        self.process_all = False

    def start(self):
        """
        Carries out an infinite while loop.
        Polls events queue and directs each event to handler.
        The loop will then pause for "heartbeat" seconds and continue.
        """
        self.started = True
        self.handler.start()
        self.run_in_loop()

    def run_in_loop(self):
        while self.started:
            # outer while loop will trigger inner while loop after 'heartbeat'
            if self.process_all:
                self.pull_process_all()
            else:
                self.pull_process()

    def pull_process(self):
        while self.started:
            # while loop to poll for events
            try:
                event = self.events_q.get(True, self.heartbeat)
            except Empty:
                break
            else:
                try:
                    processed_event = self.handler.process(event)
                    if processed_event is not None and self.processed_event_q is not None:
                        self.processed_event_q.put(processed_event)
                except:
                    if self.exceptions_q is not None:
                        err_msg = 'Unexpected error-%s' % sys.exc_info()[0]
                        self.exceptions_q.put(ExceptionEvent(str(self), err_msg, event))
                    else:
                        # self.stop()
                        raise
                finally:
                    if self.forward_q is not None:
                        try:
                            self.forward_q.put(event, self.heartbeat)
                        except Full:
                            print('Could not forward as q is full - [%s]' % event)
        # end of while loop after collecting all events in queue

    def stop(self):
        self.started = False
        self.handler.stop()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '%s[%s]' % (self.__class__.__name__, self.handler)

    def set_process_all_on(self):
        self.process_all = True
        return self

    def set_process_all_off(self):
        self.process_all = False
        return self

    def pull_process_all(self):
        events = list()
        while self.started:
            # while loop to poll for events
            events.clear()
            try:
                while True:
                    # drain out all events from queue
                    event = self.events_q.get_nowait()
                    events.append(event)
            except Empty:
                if len(events) == 0:
                    sleep(self.heartbeat)
                    continue

            # process the drained out events in one go
            try:
                processed_event = self.handler.process_all(events)
                if processed_event is not None and self.processed_event_q is not None:
                    self.processed_event_q.put(processed_event)
            except:
                if self.exceptions_q is not None:
                    err_msg = 'Unexpected error-%s' % sys.exc_info()[0]
                    self.exceptions_q.put(ExceptionEvent(str(self), err_msg, events))
                else:
                    # self.stop()
                    raise
            finally:
                if self.forward_q is not None:
                    while len(events) > 0:
                        try:
                            self.forward_q.put(events.pop(0), self.heartbeat)
                        except Full:
                            print('Could not forward as q is full - [%s]' % event)
                            while len(events) > 0:
                                print('Could not forward as q was full - [%s]' % events.pop(0))

        # end of while loop after collecting all events in queue


