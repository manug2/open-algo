__author__ = 'ManuGarg'

import unittest
from queue import Queue
from com.open.algo.utils import COMMAND_STOP
from com.open.algo.wiring.commandListener import QueueCommandListener
from time import sleep


class TestQueuedCommandListener(unittest.TestCase):

    def on_command(self, command):
        self.last_command = command

    def setUp(self):
        self.command_q = Queue()
        self.listener = QueueCommandListener(self.command_q, self.on_command)
        self.last_command = None

    def tearDown(self):
        pass # self.listener.stop()

    def test_should_allow_sending_commands(self):
        self.listener.start()
        self.command_q.put_nowait(COMMAND_STOP)
        sleep(0.1)
        self.assertEqual(COMMAND_STOP, self.last_command)

