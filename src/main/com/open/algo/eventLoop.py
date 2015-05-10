from queue import Empty
import sys
from com.open.algo.model import ExceptionEvent

__author__ = 'ManuGarg'


class EventLoop(object):
    def __init__(self, events_q, handler, heartbeat=0.1, journaler=None, exceptions_q=None):
        assert heartbeat > 0, 'Expecting [%s] to be > 0, found [%s]' % ('heartbeat', heartbeat)
        self.heartbeat = heartbeat
        assert events_q is not None, 'Expecting [%s] to be not None, found [%s]' % ('events queue', events_q)
        self.events_q = events_q
        assert handler is not None, 'Expecting [%s] to be not None, found [%s]' % ('event handler', handler)
        self.handler = handler
        self.started = False
        self.journaler = journaler
        self.exceptions_q = exceptions_q

    def start(self):
        """
        Carries out an infinite while loop.
        Polls events queue and directs each event to handler.
        The loop will then pause for "heartbeat" seconds and continue.
        """
        if self.journaler is not None:
            self.journaler.log_message('starting..')
        self.started = True
        self.handler.start()
        self.run_in_loop()

    def run_in_loop(self):
        while self.started:
            # outer while loop will trigger inner while loop after 'heartbeat'
            if self.journaler is not None:
                self.journaler.log_message('run_in_loop..')
            self.pull_process()
        if self.journaler is not None:
            self.journaler.log_message('stopped!')


    def pull_process(self):
        while self.started:
            # while loop to poll for events
            try:
                event = self.events_q.get(True, self.heartbeat)
            except Empty:
                break
            else:
                if self.journaler is not None:
                    self.journaler.logEvent(event)
                if event is not None:
                    try:
                        self.handler.process(event)
                    except:
                        err_msg = 'Unexpected error-%s' % sys.exc_info()[0]
                        if self.journaler is not None:
                            self.journaler.log_message(err_msg)
                        if self.exceptions_q is not None:
                            self.exceptions_q.put(ExceptionEvent(str(self), err_msg, event))
                        else:
                            print(err_msg)
        # end of while loop after collecting all events in queue

    def stop(self):
        if self.journaler is not None:
            self.journaler.log_message('stopping..')
        self.started = False
        self.handler.stop()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '%s[%s]' % (self.__class__.__name__, self.handler)

