import requests
import json

from com.open.algo.trading.fxEvents import TickEvent
from com.open.algo.model import StreamDataHandler, ExceptionEvent


class StreamingForexPrices(StreamDataHandler):
	def __init__(
		self, domain, access_token
		, account_id, instruments, events_queue, journaler
		, exception_queue, logEnabled=False
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
		if logEnabled==True:
			import logging
			self.logger = logging.getLogger(self.__class__.__name__)
		else:
			self.logger = None
	#end of init

	def __str__(self):
		return '%s[%s;%s;%s;%s]' %(__class__.__name__, self.domain, self.access_token, self.account_id, self.instruments)

	def connect(self):
		try:
			self.session = requests.Session()
			url = self.domain + "/v1/prices"
			headers = {'Authorization' : 'Bearer ' + self.access_token}
			params = {'instruments' : self.instruments, 'accountId' : self.account_id}
			req = requests.Request('GET', url, headers=headers, params=params)
			pre = req.prepare()
			resp = self.session.send(pre, stream=True, verify=False)
			return resp
		except Exception as e:
			self.session.close()
			exm = 'Caught exception when connecting to stream - %s' % e
			if self.logger != None:
				self.logger.error(exm)
			#using a blocking put to stall application in case of several exceptions
			self.exception_queue.put(ExceptionEvent(self, exm))

	def stream(self):
		self.streaming = True
		response = self.connect()
		if response.status_code != 200:
			exm = 'Web response not OK (%d), "%s"' % (response.status_code, response.text)
			if self.logger != None:
				self.logger.error(exm)
			self.exception_queue.put_nowait(ExceptionEvent(self, exm))
			return
		for line in response.iter_lines(1):
			if self.streaming == False:
				break
			if line:
				try:
					msg = json.loads(line.decode("utf-8"))
				except Exception as e:
					exm = 'Cannot convert response to json - "%s"' % e
					if self.logger != None:
						self.logger.error(exm)
					self.exception_queue.put_nowait(ExceptionEvent(self, exm))
					if self.logger != None:
						self.logger.debug('web response line "%s"' % line)

				if "instrument" in msg or "tick" in msg:
					if self.logger != None:
						self.logger.debug(msg)
					instrument = msg["tick"]["instrument"]
					time = msg["tick"]["time"]
					bid = msg["tick"]["bid"]
					ask = msg["tick"]["ask"]
					tev = TickEvent(instrument, time, bid, ask)
					self.journaler.logEvent(tev)
					self.events_queue.put(tev)

	def stop(self):
		self.streaming = False
		if self.session != None:
			self.session.close()
			self.session = None

