import urllib
import requests
import json

from com.open.algo.model import ExecutionHandler
from com.open.algo.utils import EventHandler
from com.open.algo.oanda.parser import parse_execution_response


class OandaExecutionHandler(ExecutionHandler, EventHandler):
    def __init__(self, domain, access_token, account_id, logEnabled=False):
        super(ExecutionHandler, self).__init__()
        self.TYPE = "https/urlencoded"
        self.executing = False
        self.session = None
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded"
            , "Authorization": "Bearer " + access_token
        }
        self.url = domain + '/v1/accounts/%s/orders' % account_id
        if logEnabled:
            import logging

            self.logger = logging.getLogger(self.__class__.__name__)
        else:
            self.logger = None

    def __str__(self):
        val = self.__class__.__name__ + "{" + self.url + "|" + str(self.headers) + "}"
        return val

    def __repr__(self):
        return self.__str__()

    def connect(self):
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.executing = True

    def parseResponse(self, response):

        if response is None:
            return {'code': -1, 'message': 'No response from Oanda execution server'}
        elif response.content is None:
            return {'code': -1, 'message': 'No response from Oanda execution server'}
        else:
            content = response.content.decode('utf-8')
            # put this into journal
            if content is None:
                return {'code': -1, 'message': 'No response from Oanda execution server'}
            else:
                # if self.logger != None:
                # self.logger.debug('Response from execution server : "%s"' % content)
                content = json.loads(content)
                if self.logger is not None:
                    self.logger.info('Response parsed : "%s"' % content)
                return content

    def execute_order(self, event):
        if self.logger is not None:
            self.logger.debug(event)

        if not self.executing:
            if self.logger is not None:
                self.logger.warn('Executor in stop mode, will not execute order: "%s"' % event)
            return

        params = {
            "instrument": event.instrument,
            "units": event.units,
            "type": event.order_type,
            "side": event.side
        }
        for attr in ['price', 'lowerBound', 'upperBound', 'stopLoss', 'takeProfit', 'trailingStop', 'expiry']:
            value = getattr(event, attr)
            if value is not None:
                params[attr] = value

        request_args = dict()
        request_args['data'] = urllib.parse.urlencode(params)

        if self.logger is not None:
            self.logger.debug('URL:%s, PARAM:%s' % (self.url, request_args))

        func = getattr(self.session, 'post')
        try:
            response = func(self.url, **request_args)
            return self.parseResponse(response)
        except requests.RequestException as e:
            if self.logger is not None:
                self.logger.error(e)
            # put in exception queue
            return {'code': -2, 'message': str(e)}

    def stop(self):
        self.executing = False
        if self.session is not None:
            self.session.close()
        self.session = None

    def get_orders(self, params=None):
        # def get_orders(self, order_type="market", instrument=None):
        if not self.executing:
            if self.logger is not None:
                self.logger.warn('Executor in stop mode, will not query orders')
            return

        request_args = {}
        if params is not None:
            request_args['data'] = urllib.parse.urlencode(params)

        if self.logger is not None:
            self.logger.debug('URL:%s, PARAM:%s' % (self.url, request_args))

        func = getattr(self.session, 'get')
        try:
            response = func(self.url, **request_args)
            return self.parseResponse(response)
        except requests.RequestException as e:
            if self.logger is not None:
                self.logger.error(e)
            # put in exception queue
            return {'code': -2, 'message': str(e)}

    # end of get_orders

    def get_order(self, order_id):
        if not self.executing:
            if self.logger is not None:
                self.logger.warn('Executor in stop mode, will not query order')
            return

        request_args = {}
        url = '%s/%s' % (self.url, order_id)
        if self.logger is not None:
            self.logger.debug('URL:%s' % url)

        func = getattr(self.session, 'get')
        try:
            response = func(url, **request_args)
            return self.parseResponse(response)
        except requests.RequestException as e:
            if self.logger is not None:
                self.logger.error(e)
            # put in exception queue
            return {'code': -2, 'message': str(e)}
            # end of get_order

    def start(self):
        self.connect()

    def process(self, event):
        return self.execute_order_and_parse_response(event)

    def execute_order_and_parse_response(self, event):
        response_dict = self.execute_order(event)
        return parse_execution_response(response_dict, str(self), event)