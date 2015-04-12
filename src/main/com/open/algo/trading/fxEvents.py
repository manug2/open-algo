from com.open.algo.model import Event

class TickEvent (Event):
	def __init__ (self, instrument, time, bid, ask):
		self.TYPE = 'TICK'
		self.instrument = instrument
		self.time = time
		self.bid = bid
		self.ask = ask

	def __str__(self):
		msg = __class__.__name__ + "(" + self.instrument + ","
		msg = msg + str(self.bid) + "," + str(self.ask) + "," + self.time + ")"
		return msg

class OrderEvent (Event) :
	def __init__ (self, instrument, units, side, order_type='market', price=None, lowerBound=None, upperBound=None, stopLoss=None, takeProfit=None, expiry=None, trailingStop=None):
		self.TYPE = 'ORDER'
		self.instrument = instrument
		self.units = units
		self.order_type = order_type
		self.side = side
		
		self.price = price
		self.lowerBound = lowerBound
		self.upperBound = upperBound
		self.stopLoss = stopLoss
		self.takeProfit = takeProfit
		self.expiry = expiry
		self.trailingStop = trailingStop 

	def __str__(self):
		msg = '%s(%s,%s,%s,%s' %(__class__.__name__, self.instrument, self.units
			, self.order_type, self.side)
		for attr in ['price', 'lowerBound', 'upperBound', 'stopLoss', 'takeProfit', 'trailingStop', 'expiry']:
			value = getattr(self, attr)
			if value != None:
				msg = '%s, %s=%s'%(msg, attr, value)
		msg = msg + ")"
		return msg


