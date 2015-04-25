import requests
import json

from com.open.algo.trading.fxEvents import TickEvent
from com.open.algo.model import DataHandler, ExceptionEvent


class HistoricForexPrices(DataHandler):
    def __init__(
            self, domain, access_token
            , account_id, log_enabled=False
    ):
        self.TYPE = "streaming/json"
        self.domain = domain
        self.access_token = access_token
        self.account_id = account_id
        if log_enabled:
            import logging
            self.logger = logging.getLogger(self.__class__.__name__)
        else:
            self.logger = None

    # end of init

    def __str__(self):
        return '%s[%s;%s;%s;%s]' % (self.__class__.__name__, self.domain, self.access_token, self.account_id)

    def connect(self):
        pass

    def query(self, instrument, granularity='S5', count=50, other_params=None):
        rates = []
        session = None
        try:
            session = requests.Session()
            url = self.domain + "/v1/candles"
            headers = {'Authorization': 'Bearer ' + self.access_token}

            if other_params is None:
                params = {}
            else:
                params = other_params.copy()

            params['instrument'] = instrument
            # params['granularity'] = granularity
            # params['count'] = count

            req = requests.Request('GET', url, headers=headers, params=params)
            pre = req.prepare()
            response = session.send(pre, stream=False, verify=False)
            if response.status_code != 200:
                exm = 'Web response not OK (%d), "%s"' % (response.status_code, response.text)
                if self.logger is not None:
                    self.logger.error(exm)
                    raise ExceptionEvent(self, exm)

            msg = None
            try:
                msg = json.loads(response.text)
            except Exception as e:
                exm = 'Cannot convert response to json - "%s"' % e
                if self.logger is not None:
                    self.logger.error(exm)
                    raise ExceptionEvent(self, exm)

            if "instrument" in msg or "tick" in msg:
                if self.logger is not None:
                    self.logger.debug(msg)
                instrument = msg["instrument"]
                for candle in msg['candles']:
                    time = candle["time"]
                    bid = candle["closeBid"]
                    ask = candle["closeAsk"]
                    rates.append(TickEvent(instrument, time, bid, ask))

        finally:
            if session is not None:
                session.close()

        return rates

