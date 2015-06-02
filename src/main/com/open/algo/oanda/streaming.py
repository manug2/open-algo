import json
from queue import Full

import requests

from com.open.algo.oanda.parser import parse_event
from com.open.algo.trading.fxEvents import TickEvent
from com.open.algo.model import StreamDataProvider, ExceptionEvent, Heartbeat
from com.open.algo.utils import get_time


class StreamingForexPrices(StreamDataProvider):
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

        self.context = '/v1/prices'
    # end of init

    def __str__(self):
        return '%s[%s;%s;%s;%s;%s]' % (
            self.__class__.__name__, self.domain, self.access_token, self.account_id, self.context, self.instruments)

    def connect(self):
        if self.events_q is None:
            raise Exception('"%s" is not set' % 'events_q')
        if self.journaler is None:
            raise Exception('"%s" is not set' % 'journaler')

        self.session = requests.Session()
        url = self.domain + self.context
        headers = {'Authorization': 'Bearer ' + self.access_token}
        params = {'accountId': self.account_id}
        if self.instruments is not None:
            params['instruments'] = self.instruments

        req = requests.Request('GET', url, headers=headers, params=params)
        pre = req.prepare()
        resp = self.session.send(pre, stream=True, verify=False)
        return resp

    def stream(self):
        self.streaming = True
        response = self.connect()
        if response.status_code != 200:
            raise RuntimeError('Web response not OK (%d), "%s"' % (response.status_code, response.text))

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
                        print(exm)

                if parsed_event is not None:
                    try:
                        if isinstance(parsed_event, TickEvent):
                            self.events_q.put_nowait(parsed_event)
                        elif isinstance(parsed_event, Heartbeat) and self.heartbeat_q is not None:
                            self.heartbeat_q.put_nowait(parsed_event)
                    except Full:
                        print('WARNING: queue is full, could not put event [%s]' % parsed_event)

            if not self.streaming:
                break

    def stop(self):
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
        self.context = context
        return self
