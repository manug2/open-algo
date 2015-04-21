import copy
from com.open.algo.model import RiskManager


class CcyExposureLimitRiskEvaluator(RiskManager):
    """CcyExposureLimitRiskEvaluator helps pre check and orders against limits
        #limits:
        #1. ccy exposure per traded ccy expressed in terms of base currency
        #1. ccy exposure for whole portfolio

        It also helps in issuing liquidating transactions which breach exposure limits

        ccyLimit  - default individual ccy exposure limit for per ccy
        ccyLimits  - specific individual position limits in terms of units
        portLimit - ccy exposure limit for whole portfolio
        portLimitShort - ccy exposure limit for whole portfolio
        ccyLimitShort  - default individual short position limit in terms of units
        ccyLimitsShort  - specific individual short position limits in terms of units
        short limits are specified in -ve numbers, with a max of 0
        short limits are specified in -ve numbers, with a max of 0
    """

    def __init__(self, baseCurrency
                 , ccyLimit=5000, ccyLimits={}
                 , ccyLimitShort=-5000, ccyLimitsShort={}
                 , portLimit=100, portLimitShort=-100, ratesMap={}):

        assert baseCurrency != None, '[%s] is None for [%s]' % ("base ccy", self.__class__.__name__)
        self.baseCcy = baseCurrency

        self.positions = {}

        assert ccyLimit > 0, '[%s] is [%s] for [%s]' % ("position limit", ccyLimit, self.__class__.__name__)
        self.ccyLimit = ccyLimit  # default individual position limit in terms of units

        assert portLimit > 0, '[%s] is [%s] for [%s]' % ("portfolio limit", portLimit, self.__class__.__name__)
        self.portLimit = portLimit  # ccy exposure limit for whole portfolio
        assert portLimitShort < 0, '[%s] is -ve for [%s]' % ("portfolio short limit", self.__class__.__name__)
        self.portLimitShort = portLimitShort  # ccy exposure limit for whole portfolio

        self.ratesMap = ratesMap
        if ccyLimits == None:
            self.ccyLimits = {}
        else:
            self.ccyLimits = ccyLimits

        assert ccyLimitShort <= 0, '[%s] is [%s] for [%s]' % (
        "short position limit", ccyLimitShort, self.__class__.__name__)
        self.ccyLimitShort = ccyLimitShort  # default individual short position limit in terms of units
        if ccyLimitsShort == None:
            self.ccyLimitsShort = {}
        else:
            self.ccyLimitsShort = ccyLimitsShort

        assert self.ccyLimit >= 0, '[%s] cannot be -ve for [%s]' % ("position limit", self.__class__.__name__)
        assert self.ccyLimitShort <= 0, '[%s] cannot be +ve for [%s]' % (
        "short position limit", self.__class__.__name__)

    def filter_order(self, order):

        currencies = order.instrument.split('_')
        # currAmounts = []
        fxRatesWrtBase = []

        try:
            if order.side == 'buy':
                if currencies[0] == self.baseCcy:
                    fxRatesWrtBase.append(1)
                else:
                    fxRatesWrtBase.append(self.ratesMap[currencies[0]]['ask'])
                #currAmounts.append(order.units / fxRatesWrtBase[0])

                if currencies[1] == self.baseCcy:
                    fxRatesWrtBase.append(1)
                else:
                    fxRatesWrtBase.append(self.ratesMap[currencies[1]]['bid'])
                    #currAmounts.append(order.units * -1 / fxRatesWrtBase[1])
            else:
                if currencies[0] == self.baseCcy:
                    fxRatesWrtBase.append(1)
                else:
                    fxRatesWrtBase.append(self.ratesMap[currencies[0]]['bid'])
                #currAmounts.append(order.units/ fxRatesWrtBase[0])

                if currencies[1] == self.baseCcy:
                    fxRatesWrtBase.append(1)
                else:
                    fxRatesWrtBase.append(self.ratesMap[currencies[1]]['ask'])
                    #currAmounts.append(order.units * -1 / fxRatesWrtBase[1])
        except KeyError as e:
            raise AssertionError('Could not find rate for evaluating [%s] - [%s]' % (order.instrument, str(e)))

        filteredOrder = copy.copy(order)

        ccyPosition = 0
        if currencies[0] in self.positions:
            ccyPosition = self.positions[currencies[0]]
        maxExposure = 0

        ccyPosition2nd = 0
        if currencies[1] in self.positions:
            ccyPosition2nd = self.positions[currencies[1]]
        maxExposure2nd=0

        if order.side == 'buy':
            limit = self.ccyLimit
            if currencies[0] in self.ccyLimits:
                limit = self.ccyLimits[currencies[0]]
                assert limit >= 0, '[%s] cannot be -ve for [%s]' % ("ccy limit", currencies[0])
            if ccyPosition < limit:
                maxExposure = limit - ccyPosition
            maxUnits = round(maxExposure * fxRatesWrtBase[0], 0)
            if maxUnits < filteredOrder.units:
                filteredOrder.units = maxUnits

            # 2nd currency in a buy order
            limit = self.ccyLimitShort
            if currencies[1] in self.ccyLimitsShort:
                limit = self.ccyLimitsShort[currencies[1]]
                assert limit <= 0, '[%s] cannot be +ve for [%s]' % ("short ccy limit", currencies[0])
            if ccyPosition2nd > limit:
                maxExposure2nd = ccyPosition2nd - limit
            maxUnits = round(maxExposure2nd * fxRatesWrtBase[1], 0)
            if maxUnits < filteredOrder.units:
                filteredOrder.units = maxUnits

        else:  # sell order
            limit = self.ccyLimitShort
            if currencies[0] in self.ccyLimitsShort:
                limit = self.ccyLimitsShort[currencies[0]]
                assert limit <= 0, '[%s] cannot be +ve for [%s]' % ("short position limit", order.instrument)
            if ccyPosition > limit:
                maxExposure = ccyPosition - limit
            maxUnits = round(maxExposure * fxRatesWrtBase[0], 0)
            if maxUnits < order.units:
                filteredOrder.units = maxUnits

            # 2nd currency in a sell order
            limit = self.ccyLimit
            if currencies[1] in self.ccyLimits:
                limit = self.ccyLimits[currencies[1]]
                assert limit >= 0, '[%s] cannot be -ve for [%s]' % ("ccy limit", currencies[1])
            if ccyPosition2nd < limit:
                maxExposure2nd = limit - ccyPosition2nd
            maxUnits = round(maxExposure2nd * fxRatesWrtBase[1], 0)
            if maxUnits < filteredOrder.units:
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
        if instrument not in self.ratesMap:
            self.ratesMap[instrument] = {}
        self.ratesMap[instrument]['bid'] = bid
        self.ratesMap[instrument]['ask'] = ask

    def set_limit(self, instrument, ccyLimit=None, ccyLimitShort=None):
        if ccyLimit:
            self.ccyLimits[instrument] = ccyLimit
        else:
            if instrument in self.ccyLimits:
                del self.ccyLimits[instrument]
        if ccyLimitShort:
            self.ccyLimitsShort[instrument] = ccyLimitShort
        else:
            if instrument in self.ccyLimitsShort:
                del self.ccyLimitsShort[instrument]


