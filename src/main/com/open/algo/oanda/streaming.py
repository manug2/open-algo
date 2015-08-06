import json
from queue import Full

import requests

from com.open.algo.oanda.parser import parse_event
from com.open.algo.model import StreamDataProvider, ExceptionEvent, Heartbeat
from com.open.algo.utils import get_time, COMMAND_STOP
import logging
import os


OANDA_CONTEXT_RATES = '/v1/prices'
OANDA_CONTEXT_EVENTS = '/v1/events'


class OandaEventStreamer(StreamDataProvider):
    def __init__(self, domain, access_token, account_id, journaler):
        self.TYPE = "streaming/json"
        self.domain = domain
        self.access_token = access_token
        self.account_id = account_id
        self.journaler = journaler

        self.session = None
        self.streaming = False

        self.instruments = None
        self.events_q = None
        self.heartbeat_q = None
        self.exception_q = None

        self.context = OANDA_CONTEXT_RATES
        self.logger = logging.getLogger(self.__class__.__name__)

        self.logger.info('using domain [%s]' % self.domain)
        self.logger.info('%s using account[%s], token[%s]' %
                          (self.__class__.__name__, self.account_id, self.access_token))

    # end of init

    def __str__(self):
        return '%s[%s%s]' % (
            self.__class__.__name__, self.domain, self.context)

    def connect(self):
        url = self.domain + self.context
        self.logger.info('preparing connection to streaming end point [%s]' % url)
        if self.events_q is None:
            raise Exception('"%s" is not set' % 'events_q')
        if self.journaler is None:
            raise Exception('"%s" is not set' % 'journaler')

        self.session = requests.Session()
        headers = {'Authorization': 'Bearer ' + self.access_token}
        params = {'accountId': self.account_id}
        if self.instruments is not None:
            params['instruments'] = self.instruments

        self.logger.info('using headers [%s]' % headers)
        self.logger.info('using params [%s]' % params)

        req = requests.Request('GET', url, headers=headers, params=params)
        pre = req.prepare()
        self.logger.info('connecting to streaming end point..')
        resp = self.session.send(pre, stream=True, verify=False)
        self.logger.info('connection to streaming end point successful, now receiving..')
        return resp

    def stream(self):
        print('starting process %s-%s, for [%s]' % (os.getppid(), os.getpid(), str(self)))
        self.streaming = True
        response = self.connect()
        if response.status_code != 200:
            raise RuntimeError('HTTP response not OK (%d), "%s"' % (response.status_code, response.text))

        if not self.streaming:
            return
        for line in response.iter_lines(1):
            if line:
                parsed_event = None
                try:
                    receive_time = get_time()
                    line_str = line.decode("utf-8")
                    self.journaler.log_event(receive_time, line_str)
                    msg = json.loads(line_str)
                    parsed_event = parse_event(receive_time, msg)
                except Exception as e:
                    exm = 'Cannot parse line from streaming response - [%s], error [%s]' % (line, e)
                    try:
                        self.exception_q.put_nowait(ExceptionEvent(self, exm))
                    except Full:
                        self.logger.error(exm)

                if parsed_event is not None:
                    try:
                        if isinstance(parsed_event, Heartbeat):
                            if self.heartbeat_q is not None:
                                self.heartbeat_q.put_nowait(parsed_event)
                        else:
                            self.events_q.put_nowait(parsed_event)
                    except Full:
                        self.logger.error('queue is full, could not put event received [%s]' % parsed_event)
            if not self.streaming:
                break

    def stop(self):
        print('stopping process %s-%s, for [%s]' % (os.getppid(), os.getpid(), str(self)))
        self.streaming = False
        if self.session is not None:
            self.session.close()
            self.session = None

    def set_instruments(self, instruments):
        self.instruments = instruments
        return self

    def set_events_q(self, events_q):
        self.events_q = events_q
        return self

    def set_heartbeat_q(self, heartbeat_q):
        self.heartbeat_q = heartbeat_q
        return self

    def set_exception_q(self, exception_q):
        self.exception_q = exception_q
        return self

    def set_context(self, context):
        if self.streaming:
            raise RuntimeError('cannot change context after events streaming has started')
        if context == OANDA_CONTEXT_RATES or context == OANDA_CONTEXT_EVENTS:
            self.context = context
        else:
            raise ValueError('expecting context to be one of (%s,%s), found "%s"'
                             % (OANDA_CONTEXT_RATES, OANDA_CONTEXT_EVENTS, context))
        return self

    def on_command(self, command):
        self.logger.info('command received "%s"' % command)
        if command == COMMAND_STOP:
            self.stop()
