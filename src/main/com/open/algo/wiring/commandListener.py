__author__ = 'ManuGarg'

from threading import Thread
from com.open.algo.utils import COMMAND_STOP


class QueueCommandListener:

    """
    this class implements a simple loop which will invoke the method configured
    to be invoked when there is any event in the 'command_q'
    it runs in its own Thread, local to process where the commands need to be listened
    """
    def __init__(self, command_q, on_command_method):
        self.command_q = command_q
        self.on_command_method = on_command_method
        self.command_thread = None
        self.poll_interval = 2
        self.name = 'default'

    def start(self):
        if not self.command_q:
            raise RuntimeError('cannot setup command listener as no "command_q" was specified')
        if not self.on_command_method:
            raise RuntimeError('cannot setup command listener as no "on_command_method" was specified')

        self.command_thread = Thread(name='COMMANDER-' + self.name, target=self.poll_command_events, args=[])
        self.command_thread.start()

    def poll_command_events(self):
        while True:
            command_event = self.command_q.get(self.poll_interval)
            if command_event:
                self.on_command_method(command_event)
                if COMMAND_STOP == command_event:
                    # finished this thread's work
                    break
        # end of while

    def set_command_q(self, command_q):
        self.command_q = command_q
        return self

    def set_poll_interval(self, poll_interval):
        self.poll_interval = poll_interval
        return self

    def set_name(self, name):
        self.name = name
        return self
