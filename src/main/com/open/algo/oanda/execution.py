import http.client
import urllib
import requests
import json

from com.open.algo.model import ExecutionHandler


class OandaExecutionHandler(ExecutionHandler):
	def __init__(self, domain, access_token, account_id, logEnabled=False):
		self.TYPE="https/urlencoded"
		self.executing = False
		self.session = None
		self.headers = {
			"Content-Type": "application/x-www-form-urlencoded"
			, "Authorization": "Bearer " + access_token
		}
		self.url = domain + '/v1/accounts/%s/orders' % (account_id)
		if logEnabled == True:
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
		#if self.logger != None:
			#self.logger.debug ('Response from execution server : "%s"' % response)

		if response == None:
			return {'code':-1, 'message': 'No response from Oanda execution server'}
		elif response.content == None:
			return {'code':-1, 'message': 'No response from Oanda execution server'}
		else:
			content = response.content.decode('utf-8')
			#put this into journal
			if content == None:
				return {'code':-1, 'message': 'No response from Oanda execution server'}
			else:
				#if self.logger != None:
					#self.logger.debug('Response from execution server : "%s"' % content)
				content = json.loads(content)
				if self.logger != None:
					self.logger.info('Response parsed : "%s"' % content)
				return content
		
	def stop(self):
		self.executing = False
		
	def execute_order(self, event):
		if self.logger != None:
			self.logger.debug(event)

		if self.executing == False:
			if self.logger != None:
				self.logger.warn('Executor in stop mode, will not execute order: "%s"' % event)
			return

		params = {
			"instrument" : event.instrument,
			"units" : event.units,
			"type" : event.order_type,
			"side" : event.side
		}
		for attr in ['price', 'lowerBound', 'upperBound', 'stopLoss', 'takeProfit', 'trailingStop', 'expiry']:
			value = getattr(event, attr)
			if value != None:
				params[attr] = value
		
		request_args = {}
		request_args['data'] = urllib.parse.urlencode(params)

		if self.logger != None:
			self.logger.debug('URL:%s, PARAM:%s'% (self.url, request_args))

		func = getattr(self.session, 'post')
		try:
			response = func(self.url, **request_args)
			return self.parseResponse(response)
		except requests.RequestException as e:
			if self.logger != None:
				self.logger.error(e)
			#put in exception queue
			return {'code':-2, 'message':str(e)}


	def stop(self):
		self.executing = False
		if self.session != None:
			self.session.close()
		self.session = None

	def get_orders(self, params=None):
	#def get_orders(self, order_type="market", instrument=None):
		if self.executing == False:
			if self.logger != None:
				self.logger.warn('Executor in stop mode, will not query orders')
			return
		
		request_args = {}
		if params != None:
			request_args['data'] = urllib.parse.urlencode(params)

		if self.logger != None:
			self.logger.debug('URL:%s, PARAM:%s'% (self.url, request_args))

		func = getattr(self.session, 'get')
		try:
			response = func(self.url, **request_args)
			return self.parseResponse(response)
		except requests.RequestException as e:
			if self.logger != None:
				self.logger.error(e)
			#put in exception queue
			return {'code':-2, 'message':str(e)}
	#end of get_orders

	def get_order(self, order_id):
		if self.executing == False:
			if self.logger != None:
				self.logger.warn('Executor in stop mode, will not query order')
			return
		
		request_args = {}
		url = '%s/%s' % (self.url, order_id)
		if self.logger != None:
			self.logger.debug('URL:%s'% url)

		func = getattr(self.session, 'get')
		try:
			response = func(url, **request_args)
			return self.parseResponse(response)
		except requests.RequestException as e:
			if self.logger != None:
				self.logger.error(e)
			#put in exception queue
			return {'code':-2, 'message':str(e)}
	#end of get_order

