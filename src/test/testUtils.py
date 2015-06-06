__author__ = 'ManuGarg'

import sys
sys.path.append('../../main')
from queue import Empty

TARGET_ENV = "practice"
MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM = 5
CONFIG_PATH_FOR_UNIT_TESTS = '../../../../fx-oanda'


def await_event_receipt(test_case, queue, timeout_message, timeout=MAX_TIME_TO_ALLOW_SOME_EVENTS_TO_STREAM):
    try:
        return queue.get(True, timeout=timeout)
    except Empty:
        test_case.fail('%s, within timeout of "%s"' % (timeout_message, timeout))
