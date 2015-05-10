import requests
import json

from com.open.algo.trading.fxEvents import TickEvent
from com.open.algo.model import StreamDataHandler, ExceptionEvent
from queue import Full


def parse_tick_event(msg):
    instrument = msg["tick"]["instrument"]
    time = msg["tick"]["time"]
    bid = msg["tick"]["bid"]
    ask = msg["tick"]["ask"]
    tev = TickEvent(instrument, time, bid, ask)
    return tev


class StreamingForexPrices(StreamDataHandler):
    def __init__(
            self, domain, access_token
            , account_id, instruments, events_queue, journaler
            , exception_queue
    ):
        self.TYPE = "streaming/json"
        self.domain = domain
        self.access_token = access_token
        self.account_id = account_id
        self.instruments = instruments
        self.events_queue = events_queue
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
                try:
                    msg = json.loads(line.decode("utf-8"))
                    self.journaler.log_event(msg)
                except Exception as e:
                    exm = 'Cannot convert response to json - [%s], error [%s]' % (line, e)
                    try:
                        self.exception_queue.put_nowait(ExceptionEvent(self, exm))
                    except Full:
                        print(exm)

                if "instrument" in msg or "tick" in msg:
                    tev = parse_tick_event(msg)
                    self.events_queue.put_nowait(tev)

            if not self.streaming:
                break

    def stop(self):
        self.streaming = False
        if self.session is not None:
            self.session.close()
            self.session = None
