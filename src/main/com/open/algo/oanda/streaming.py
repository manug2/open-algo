import requests
import json

from com.open.algo.trading.fxEvents import TickEvent
from com.open.algo.model import StreamDataProvider, ExceptionEvent, Heartbeat
from queue import Full


def parse_tick(msg):
    tick = msg["tick"]
    instrument = tick["instrument"]
    time = tick["time"]
    bid = tick["bid"]
    ask = tick["ask"]
    tev = TickEvent(instrument, time, bid, ask)
    return tev


def parse_heartbeat(msg):
    hb_info = msg["heartbeat"]
    hb = Heartbeat('oanda-stream')
    return hb


def parse_event(msg):
    if "tick" in msg:
        return parse_tick(msg)
    elif "heartbeat" in msg:
        return parse_heartbeat(msg)
    else:
        raise ValueError('Unexpected message received')


class StreamingForexPrices(StreamDataProvider):
    def __init__(
            self, domain, access_token
            , account_id, instruments, events_queue, heartbeat_queue, journaler
            , exception_queue
    ):
        self.TYPE = "streaming/json"
        self.domain = domain
        self.access_token = access_token
        self.account_id = account_id
        self.instruments = instruments
        self.events_queue = events_queue
        self.heartbeat_queue = heartbeat_queue
        self.streaming = False
        self.session = None
        self.journaler = journaler
        self.exception_queue = exception_queue
    # end of init

    def __str__(self):
        return '%s[%s;%s;%s;%s]' % (
            self.__class__.__name__, self.domain, self.access_token, self.account_id, self.instruments)

    def connect(self):
        self.session = requests.Session()
        url = self.domain + "/v1/prices"
        headers = {'Authorization': 'Bearer ' + self.access_token}
        params = {'instruments': self.instruments, 'accountId': self.account_id}
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
                    line_str = line.decode("utf-8")
                    self.journaler.log_event(line_str)
                    msg = json.loads(line_str)
                    parsed_event = parse_event(msg)
                except Exception as e:
                    exm = 'Cannot parse line from streaming response - [%s], error [%s]' % (line, e)
                    try:
                        self.exception_queue.put_nowait(ExceptionEvent(self, exm))
                    except Full:
                        print(exm)

                if parsed_event is not None:
                    try:
                        if isinstance(parsed_event, TickEvent):
                            self.events_queue.put_nowait(parsed_event)
                        elif isinstance(parsed_event, Heartbeat):
                            self.heartbeat_queue.put_nowait(parsed_event)
                    except Full:
                        print('WARNING: queue is full, could not put event [%s]' % parsed_event)

            if not self.streaming:
                break

    def stop(self):
        self.streaming = False
        if self.session is not None:
            self.session.close()
            self.session = None
