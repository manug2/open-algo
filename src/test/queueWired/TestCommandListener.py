__author__ = 'ManuGarg'

import unittest
from queue import Queue
from com.open.algo.utils import COMMAND_STOP
from com.open.algo.wiring.commandListener import QueueCommandListener


class TestQueuedCommandListener(unittest.TestCase):

    def on_command(self, command):
        self.last_command = command

    def setUp(self):
        self.command_q = Queue()
        self.listener = QueueCommandListener(self.command_q, self.on_command)
        self.last_command = None
        self.command_thread = self.listener.start_thread()

    def tearDown(self):
        if self.listener.listening:
            self.listener.force_stop()
        self.command_thread.join(timeout=2)

    def test_should_listen_to_STOP_command(self):
        self.command_q.put_nowait(COMMAND_STOP)
        self.command_thread.join(timeout=2)
        self.assertEqual(COMMAND_STOP, self.last_command)

    def test_should_stop_listening_after_STOP_command(self):
        self.command_q.put_nowait(COMMAND_STOP)
        self.command_thread.join(timeout=2)
        self.assertFalse(self.listener.listening, 'listening should have stopped, but did not')
