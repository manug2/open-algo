__author__ = 'ManuGarg'

from abc import abstractmethod
from queue import Empty, Full
import sys
from com.open.algo.model import ExceptionEvent
from com.open.algo.utils import EventHandler, get_time
import os


class EventLoop(object):
    def __init__(self, events_q, handler, heartbeat=0.1, exceptions_q=None, forward_q=None, processed_event_q=None):
        assert heartbeat > 0, 'Expecting [%s] to be > 0, found [%s]' % ('heartbeat', heartbeat)
        self.heartbeat = heartbeat
        assert events_q is not None, 'Expecting [%s] to be not None, found [%s]' % ('events queue', events_q)
        self.events_q = events_q
        assert handler is not None, 'Expecting [%s] to be not None, found [%s]' % ('event handler', handler)
        self.handler = handler
        self.started = False
        self.exceptions_q = exceptions_q
        self.forward_q = forward_q
        self.processed_event_q = processed_event_q

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
                        self.forward_q.put(event)
        # end of while loop after collecting all events in queue

    def stop(self):
        self.started = False
        self.handler.stop()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '%s[%s]' % (self.__class__.__name__, self.handler)


JOURNAL_SEPARATOR = '=>'


def prepare_journal_entry(receive_time, event):
    return '%s%s%s' % (receive_time, JOURNAL_SEPARATOR, event)


def parse_journal_entry(entry):
    parts = entry.split(JOURNAL_SEPARATOR)
    return parts[1]


class Journaler(object):

    def __init__(self):
        self.last_event = None
        self.last_received = None

    @abstractmethod
    def log_event(self, receive_time, event):
        print(prepare_journal_entry(receive_time, event))
        self.last_event = event
        self.last_received = receive_time

    @abstractmethod
    def get_last_event(self):
        return self.last_event

    @abstractmethod
    def get_last_received(self):
        return self.last_received


class FileJournaler(Journaler, EventHandler):

    def __init__(self, events_q, full_path=None, name_scheme=None):
        super(Journaler, self).__init__()
        self.writer = None
        self.events = events_q
        assert full_path is not None or name_scheme is not None, 'both full path and name scheme cannot be None'
        self.full_path = full_path
        self.name_scheme = name_scheme

    def log_event(self, receive_time, event):
        try:
            msg = prepare_journal_entry(receive_time, event)
            self.events.put_nowait(msg)
        except Full:
            print('WARNING: Count not journal event [%s] as queue is full' % event)
        self.last_event = event
        self.last_received = receive_time

    def process(self, event):
        self.writer.write(event)
        self.writer.write(os.linesep)
        self.writer.flush()

    def start(self):
        if self.writer is None:
            fp = self.full_path
            if fp is None:
                fp = self.name_scheme.get_file_name()
            self.writer = open(fp, 'a')

    def stop(self):
        pass

    def close(self):
        if self.writer is not None:
            if not self.writer.closed:
                self.writer.close()
            self.writer = None


class FileJournalerReader():

    def __init__(self, events, full_path=None, name_scheme=None):
        self.reader = None
        self.events = events
        self.lastEvent = None
        assert full_path is not None or name_scheme is not None, 'both full path and name scheme cannot be None'
        self.full_path = full_path
        self.name_scheme = name_scheme

    def read_events(self):
        # maybe will work out time difference between two events for pausing
        # does it need to manipulate time if it is an attribute within the actual message logged
        fp = self.full_path
        if fp is None:
            fp = self.name_scheme.get_file_name()

        self.reader = open(fp, 'r')
        for line in self.reader.read().splitlines():
            ev_str = parse_journal_entry(line)
            try:
                self.events.put_nowait(ev_str)
            except Full:
                # maybe wait and retry
                print('WARNING: Could not put event read from file to queue as it is full. file[%s] - event[%s]' % (fp, ev_str))
            self.lastEvent = ev_str
        self.reader.close()


class JournalNamingScheme():
    def __init__(self, path='', name='journal', prefix='', suffix='', ext='.txt'):
        self.path = path
        self.name = name
        self.prefix = prefix
        self.suffix = suffix
        self.ext = ext

    def get_file_name(self):
        file_name = '%s%s%s%s' % (self.prefix, self.name, self.suffix, self.ext)
        if self.path == '' or self.path is None:
            return file_name
        else:
            return os.path.join(self.path, file_name)

