import urllib
import requests
import json
from os import linesep
from com.open.algo.model import ExecutionHandler
from com.open.algo.utils import EventHandler, get_time
from com.open.algo.oanda.parser import parse_execution_response
import logging


class OandaExecutionHandler(ExecutionHandler, EventHandler):
    def __init__(self, domain, access_token, account_id, journaler):
        super(ExecutionHandler, self).__init__()
        self.TYPE = "https/urlencoded"
        self.executing = False
        self.session = None
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded"
            , "Authorization": "Bearer " + access_token
        }
        self.url = domain + '/v1/accounts/%s/orders' % account_id
        self.journaler = journaler

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('using url [%s]' % self.url)
        self.logger.info('using headers [%s]' % self.headers)

    def __str__(self):
        val = self.__class__.__name__ + "{" + self.url + "|" + str(self.headers) + "}"
        return val

    def __repr__(self):
        return self.__str__()

    def connect(self):
        self.logger.info('connecting to execution end point..')
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.logger.info('connection to execution end point successful!')
        self.executing = True

    def parse_response(self, receive_time, response):

        if response is None:
            return {'code': -1, 'message': 'No response from execution server'}
        elif response.content is None:
            return {'code': -1, 'message': 'No content in response from execution server'}
        else:

            content = response.content.decode('utf-8')
            self.journaler.log_event(receive_time, content)
            if content is None:
                return {'code': -1, 'message': 'No content after decoding response from execution server'}
            else:
                return json.loads(content)

    def execute_order(self, event):
        if not self.executing:
            self.logger.warn('Executor in stop mode, will not execute order: "%s"' % event)
            return
        self.logger.info('executing order [%s]' % event)

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

        self.logger.info('execution order parameters [%s]' % params)
        request_args = dict()
        request_args['data'] = urllib.parse.urlencode(params)
        func = getattr(self.session, 'post')

        return self.send_and_receive(func, self.url, request_args)

    def stop(self):
        self.executing = False
        if self.session is not None:
            self.session.close()
        self.session = None

    def get_orders(self, params=None):
        # def get_orders(self, order_type="market", instrument=None):
        if not self.executing:
            self.logger.warn('Executor in stop mode, will not query orders')
            return

        request_args = {}
        if params is not None:
            request_args['data'] = urllib.parse.urlencode(params)
        func = getattr(self.session, 'get')

        return self.send_and_receive(func, self.url, request_args)

    def get_order(self, order_id):
        if not self.executing:
            self.logger.warn('Executor in stop mode, will not query order')
            return

        request_args = {}
        url = '%s/%s' % (self.url, order_id)
        func = getattr(self.session, 'get')

        return self.send_and_receive(func, url, request_args)

    def start(self):
        self.connect()

    def process(self, event):
        return self.execute_order_and_parse_response(event)

    def execute_order_and_parse_response(self, event):
        response_dict = self.execute_order(event)
        executed_order = parse_execution_response(response_dict, str(self), event)
        self.logger.info('executor response - %s' % executed_order)
        return executed_order

    def send_and_receive(self, func, url, request_args):
        self.logger.info('execution order parameter (url encoded) [%s]' % request_args)

        try:
            response = func(url, **request_args)
            receive_time = get_time()
            return self.parse_response(receive_time, response)
        except requests.RequestException as e:
            self.logger.error('exception during execution', e)
            return {'code': -2, 'message': e.args[0]}
