import copy
from com.open.algo.model import CurrencyRiskManager


class CcyExposureLimitRiskEvaluator(CurrencyRiskManager):
    """CcyExposureLimitRiskEvaluator helps pre check and orders against limits
        #limits:
        #1. ccy exposure per traded ccy expressed in terms of base currency
        #1. ccy exposure for whole portfolio

        It also helps in issuing liquidating transactions which breach exposure limits

        ccy_limit  - default individual ccy exposure limit for per ccy
        ccy_limits  - specific individual position limits in terms of units
        ccy_limit_short  - default individual short position limit in terms of units
        ccy_limits_short  - specific individual short position limits in terms of units
        short limits are specified in -ve numbers, with a max of 0
        short limits are specified in -ve numbers, with a max of 0
    """

    def __init__(self, base_ccy, rates_cache
                 , ccy_limit=5000, ccy_limits=None
                 , ccy_limit_short=-5000, ccy_limits_short=None):

        assert base_ccy is not None, '[%s] is None for [%s]' % ("base ccy", self.__class__.__name__)
        self.base_ccy = base_ccy

        assert rates_cache is not None, '[%s] is None for [%s]' % ("rates cache", self.__class__.__name__)
        self.rates_cache = rates_cache

        self.positions = {}

        assert ccy_limit > 0, '[%s] is [%s] for [%s]' % ("position limit", ccy_limit, self.__class__.__name__)
        self.ccy_limit = ccy_limit  # default individual position limit in terms of units

        if ccy_limits is None:
            self.ccy_limits = {}
        else:
            self.ccy_limits = ccy_limits

        assert ccy_limit_short <= 0, '[%s] is [%s] for [%s]' % ("short position limit", ccy_limit_short, self.__class__.__name__)
        self.ccy_limit_short = ccy_limit_short  # default individual short position limit in terms of units
        if ccy_limits_short is None:
            self.ccy_limits_short = {}
        else:
            self.ccy_limits_short = ccy_limits_short

        assert self.ccy_limit >= 0, '[%s] cannot be -ve for [%s]' % ("position limit", self.__class__.__name__)
        assert self.ccy_limit_short <= 0, '[%s] cannot be +ve for [%s]' % ("short position limit", self.__class__.__name__)

    def filter_order(self, order):

        currencies = order.instrument.split('_')
        fx_rates_wrt_base_ccy = []

        try:
            if order.side == 'buy':
                fx_rates_wrt_base_ccy.append(self.rates_cache.get_rate(currencies[0]+'_'+self.base_ccy)['ask'])
                fx_rates_wrt_base_ccy.append(self.rates_cache.get_rate(currencies[1]+'_'+self.base_ccy)['bid'])
            else:
                fx_rates_wrt_base_ccy.append(self.rates_cache.get_rate(currencies[0]+'_'+self.base_ccy)['bid'])
                fx_rates_wrt_base_ccy.append(self.rates_cache.get_rate(currencies[1]+'_'+self.base_ccy)['ask'])

        except KeyError as e:
            raise AssertionError('Could not find rate for evaluating [%s] - [%s]' % (order.instrument, str(e)))

        filtered_order = copy.copy(order)

        position_in_base_ccy_ = 0
        if currencies[0] in self.positions:
            position_in_base_ccy_ = self.positions[currencies[0]] # * fx_rates_wrt_base_ccy[0]
        max_exposure = 0

        position_in_base_ccy_2nd = 0
        if currencies[1] in self.positions:
            position_in_base_ccy_2nd = self.positions[currencies[1]] # * fx_rates_wrt_base_ccy[1]
        max_exposure2nd = 0

        if order.side == 'buy':
            limit = self.ccy_limit
            if currencies[0] in self.ccy_limits:
                limit = self.ccy_limits[currencies[0]]
                assert limit >= 0, '[%s] cannot be -ve for [%s]' % ("ccy limit", currencies[0])
            if position_in_base_ccy_ < limit:
                max_exposure = limit - position_in_base_ccy_
            max_units = round(max_exposure / fx_rates_wrt_base_ccy[0], 0)
            if max_units < filtered_order.units:
                filtered_order.units = max_units

            # 2nd currency in a buy order
            limit = self.ccy_limit_short
            if currencies[1] in self.ccy_limits_short:
                limit = self.ccy_limits_short[currencies[1]]
                assert limit <= 0, '[%s] cannot be +ve for [%s]' % ("short ccy limit", currencies[0])
            if position_in_base_ccy_2nd > limit:
                max_exposure2nd = position_in_base_ccy_2nd - limit
            max_units = round(max_exposure2nd / fx_rates_wrt_base_ccy[1], 0)
            if max_units < filtered_order.units:
                filtered_order.units = max_units

        else:  # sell order
            limit = self.ccy_limit_short
            if currencies[0] in self.ccy_limits_short:
                limit = self.ccy_limits_short[currencies[0]]
                assert limit <= 0, '[%s] cannot be +ve for [%s]' % ("short position limit", order.instrument)
            if position_in_base_ccy_ > limit:
                max_exposure = position_in_base_ccy_ - limit
            max_units = round(max_exposure / fx_rates_wrt_base_ccy[0], 0)
            if max_units < order.units:
                filtered_order.units = max_units

            # 2nd currency in a sell order
            limit = self.ccy_limit
            if currencies[1] in self.ccy_limits:
                limit = self.ccy_limits[currencies[1]]
                assert limit >= 0, '[%s] cannot be -ve for [%s]' % ("ccy limit", currencies[1])
            if position_in_base_ccy_2nd < limit:
                max_exposure2nd = limit - position_in_base_ccy_2nd
            max_units = round(max_exposure2nd / fx_rates_wrt_base_ccy[1], 0)
            if max_units < filtered_order.units:
                filtered_order.units = max_units

        # now check currency level limits
        return filtered_order

    def reval_positions(self):
        raise NotImplementedError("Should implement 'reval_positions()' method")

    def append_position(self, ccy, units):
        if ccy in self.positions:
            curr = self.positions[ccy]
        else:
            curr = 0
        self.positions[ccy] = curr + units

    def append_positions(self, positions):
        raise NotImplementedError("Should implement 'append_positions()' method")

    def reval_positions_internal(self, instrument, bid, ask):
        raise NotImplementedError("Should implement 'reval_positions()' method")

    def set_limit(self, instrument, ccy_limit=None, ccy_limit_short=None):
        if ccy_limit:
            self.ccy_limits[instrument] = ccy_limit
        else:
            if instrument in self.ccy_limits:
                del self.ccy_limits[instrument]
        if ccy_limit_short:
            self.ccy_limits_short[instrument] = ccy_limit_short
        else:
            if instrument in self.ccy_limits_short:
                del self.ccy_limits_short[instrument]

    def list_ccy_position_map(self):
        return self.positions

    def get_base_ccy(self):
        return self.base_ccy
