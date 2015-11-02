__author__ = 'ManuGarg'

from threading import Thread
from com.open.algo.utils import COMMAND_STOP
from queue import Empty


class QueueCommandListener:

    """
    this class implements a simple loop which will invoke the method configured
    to be invoked when there is any event in the 'command_q'
    it runs in its own Thread, local to process where the commands need to be listened
    """
    def __init__(self, command_q, on_command_method):
        self.command_q = command_q
        self.on_command_method = on_command_method
        self.poll_interval = 5
        self.name = 'default'
        self.listening = False

    def __str__(self):
        return '%s[%s]' % (self.__class__.__name__, self.name)

    def __repr__(self):
        return '%s[%s]' % (self.__class__.__name__, self.name)

    def start_thread(self):
        if not self.command_q:
            raise RuntimeError('cannot setup command listener as no "command_q" was specified')
        if not self.on_command_method:
            raise RuntimeError('cannot setup command listener as no "on_command_method" was specified')

        command_thread = Thread(name='COMMANDER-' + self.name, target=self.start, args=[])
        command_thread.start()
        return command_thread

    def start(self):
        self.listen()

    def listen(self):
        import logging
        logger = logging.getLogger(self.__class__.__name__)

        self.listening = True
        logger.info('starting to listen [%s]' % (self.name))
        while self.listening:
            logger.info('listening flag is [%s] [%s]' % (self.name, self.listening))
            try:
                command_event = self.command_q.get(self.poll_interval)
                logger.info('received command event [%s] [%s]' % (self.name, command_event))
                self.on_command_method(command_event)
                if COMMAND_STOP == command_event:
                    logger.info('stopping listener [%s]' % (self.name))
                    self.listening = False
            except Empty:
                pass
        # end of while
        return

    def set_command_q(self, command_q):
        self.command_q = command_q
        return self

    def set_poll_interval(self, poll_interval):
        self.poll_interval = poll_interval
        return self

    def set_name(self, name):
        self.name = name
        return self

    def force_stop(self):
        self.listening = False
