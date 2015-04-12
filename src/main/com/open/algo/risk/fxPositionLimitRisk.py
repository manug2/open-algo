
import copy
from com.open.algo.model import RiskManager

class FxPositionLimitRiskEvaluator(RiskManager):
	"""FxRiskManager helps pre check and orders against limits
		#limits:
		#1. net open cost price - price to liquidate

		posLimit  - default individual position limit in terms of units
		posLimits  - specific individual position limits in terms of units
		portLimit - ccy exposure limit for whole portfolio
		posLimitShort  - default individual short position limit in terms of units
		posLimitsShort  - specific individual short position limits in terms of units
		short limits are specified in -ve numbers, with a max of 0
	"""

	def __init__(self, posLimit=1000, posLimits={}
			, posLimitShort=0, posLimitsShort={}):

		self.positions = {}

		assert posLimit != None, '[%s] is None for [%s]' % ("position limit", self.__class__.__name__)
		self.posLimit = posLimit   #default individual position limit in terms of units

		if posLimits == None:
			self.posLimits = {}
		else:
			self.posLimits = posLimits

		assert posLimitShort != None, '[%s] is None for [%s]' % ("short position limit", self.__class__.__name__)
		self.posLimitShort = posLimitShort   #default individual short position limit in terms of units
		if posLimitsShort == None:
			self.posLimitsShort = {}
		else:
			self.posLimitsShort = posLimitsShort

		assert self.posLimit >= 0, '[%s] cannot be -ve for [%s]' % ("position limit", self.__class__.__name__)
		assert self.posLimitShort <= 0, '[%s] cannot be +ve for [%s]' % ("short position limit", self.__class__.__name__)

	def filter_order(self, order):
		currUnits = 0
		if order.instrument in self.positions:
			currUnits = self.positions[order.instrument]

		filteredOrder = copy.copy(order)
		maxUnits = 0
		
		if order.side == "buy":
			limit = self.posLimit
			if order.instrument in self.posLimits:
				limit = self.posLimits[order.instrument]
				assert limit >= 0, '[%s] cannot be -ve for [%s]' % ("position limit", order.instrument)
			#if self.logger != None:
				#self.logger.info ('Using limit [%d] for checking order [%s]'%(limit, order))
			if currUnits < limit:
				maxUnits = limit - currUnits
			if maxUnits < order.units:
				filteredOrder.units = maxUnits
		else: #sell order
			limit = self.posLimitShort
			if order.instrument in self.posLimitsShort:
				limit = self.posLimitsShort[order.instrument]
				assert limit <= 0, '[%s] cannot be +ve for [%s]' % ("short position limit", order.instrument)
			#if self.logger != None:
				#self.logger.info ('Using limit [%d] for checking order [%s]'%(limit, order))
			if currUnits > limit:
				maxUnits = currUnits - limit
			if maxUnits < order.units:
				filteredOrder.units = maxUnits
		
		#now check currency level limits
		return filteredOrder
	
	def reval_positions(self):
		raise NotImplementedError("Should implement 'reval_positions()' method")

	def append_position(self, instrument, units):
		if instrument in self.positions:
			curr = self.positions[instrument]
		else:
			curr = 0
		self.positions[instrument] = curr + units

	def append_positions(self, positions):
		raise NotImplementedError("Should implement 'append_positions()' method")
	
	def reval_positions_internal(self, instrument, bid, ask):
		raise NotImplementedError("Should implement 'reval_positions()' method")
	
	def fix_rate(self, instrument, bid, ask):
		raise NotImplementedError("Should implement 'fix_rate()' method")
	
	def set_limit(self, instrument, posLimit=None, posLimitShort=None):
		if posLimit:
			self.posLimits[instrument] = posLimit
		else:
			if instrument in self.posLimits:
				del self.posLimits[instrument]
		if posLimitShort:
			self.posLimitsShort[instrument] = posLimitShort
		else:
			if instrument in self.posLimitsShort:
				del self.posLimitsShort[instrument]


