import copy
from com.open.algo.model import RiskManager


class CcyExposureLimitRiskEvaluator(RiskManager):
    """CcyExposureLimitRiskEvaluator helps pre check and orders against limits
        #limits:
        #1. ccy exposure per traded ccy expressed in terms of base currency
        #1. ccy exposure for whole portfolio

        It also helps in issuing liquidating transactions which breach exposure limits

        ccy_limit  - default individual ccy exposure limit for per ccy
        ccy_limits  - specific individual position limits in terms of units
        port_limit - ccy exposure limit for whole portfolio
        port_limit_short - ccy exposure limit for whole portfolio
        ccy_limit_short  - default individual short position limit in terms of units
        ccy_limits_short  - specific individual short position limits in terms of units
        short limits are specified in -ve numbers, with a max of 0
        short limits are specified in -ve numbers, with a max of 0
    """

    def __init__(self, base_ccy
                 , ccy_limit=5000, ccy_limits=None
                 , ccy_limit_short=-5000, ccy_limits_short=None
                 , port_limit=100, port_limit_short=-100, rates=None):

        assert base_ccy is not None, '[%s] is None for [%s]' % ("base ccy", self.__class__.__name__)
        self.base_ccy = base_ccy

        self.positions = {}

        assert ccy_limit > 0, '[%s] is [%s] for [%s]' % ("position limit", ccy_limit, self.__class__.__name__)
        self.ccy_limit = ccy_limit  # default individual position limit in terms of units

        assert port_limit > 0, '[%s] is [%s] for [%s]' % ("portfolio limit", port_limit, self.__class__.__name__)
        self.port_limit = port_limit  # ccy exposure limit for whole portfolio
        assert port_limit_short < 0, '[%s] is -ve for [%s]' % ("portfolio short limit", self.__class__.__name__)
        self.port_limit_short = port_limit_short  # ccy exposure limit for whole portfolio

        if rates is None:
            self.rates = {}
        else:
            self.rates = rates

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
        # currAmounts = []
        fx_rates_wrt_base_ccy = []

        try:
            if order.side == 'buy':
                if currencies[0] == self.base_ccy:
                    fx_rates_wrt_base_ccy.append(1)
                else:
                    fx_rates_wrt_base_ccy.append(self.rates[currencies[0]]['ask'])
                # currAmounts.append(order.units / fx_rates_wrt_base_ccy[0])

                if currencies[1] == self.base_ccy:
                    fx_rates_wrt_base_ccy.append(1)
                else:
                    fx_rates_wrt_base_ccy.append(self.rates[currencies[1]]['bid'])
                    # currAmounts.append(order.units * -1 / fx_rates_wrt_base_ccy[1])
            else:
                if currencies[0] == self.base_ccy:
                    fx_rates_wrt_base_ccy.append(1)
                else:
                    fx_rates_wrt_base_ccy.append(self.rates[currencies[0]]['bid'])
                # currAmounts.append(order.units/ fx_rates_wrt_base_ccy[0])

                if currencies[1] == self.base_ccy:
                    fx_rates_wrt_base_ccy.append(1)
                else:
                    fx_rates_wrt_base_ccy.append(self.rates[currencies[1]]['ask'])
                    # currAmounts.append(order.units * -1 / fx_rates_wrt_base_ccy[1])
        except KeyError as e:
            raise AssertionError('Could not find rate for evaluating [%s] - [%s]' % (order.instrument, str(e)))

        filtered_order = copy.copy(order)

        ccy_position = 0
        if currencies[0] in self.positions:
            ccy_position = self.positions[currencies[0]]
        max_exposure = 0

        ccy_position2nd = 0
        if currencies[1] in self.positions:
            ccy_position2nd = self.positions[currencies[1]]
        max_exposure2nd = 0

        if order.side == 'buy':
            limit = self.ccy_limit
            if currencies[0] in self.ccy_limits:
                limit = self.ccy_limits[currencies[0]]
                assert limit >= 0, '[%s] cannot be -ve for [%s]' % ("ccy limit", currencies[0])
            if ccy_position < limit:
                max_exposure = limit - ccy_position
            max_units = round(max_exposure / fx_rates_wrt_base_ccy[0], 0)
            if max_units < filtered_order.units:
                filtered_order.units = max_units

            # 2nd currency in a buy order
            limit = self.ccy_limit_short
            if currencies[1] in self.ccy_limits_short:
                limit = self.ccy_limits_short[currencies[1]]
                assert limit <= 0, '[%s] cannot be +ve for [%s]' % ("short ccy limit", currencies[0])
            if ccy_position2nd > limit:
                max_exposure2nd = ccy_position2nd - limit
            max_units = round(max_exposure2nd / fx_rates_wrt_base_ccy[1], 0)
            if max_units < filtered_order.units:
                filtered_order.units = max_units

        else:  # sell order
            limit = self.ccy_limit_short
            if currencies[0] in self.ccy_limits_short:
                limit = self.ccy_limits_short[currencies[0]]
                assert limit <= 0, '[%s] cannot be +ve for [%s]' % ("short position limit", order.instrument)
            if ccy_position > limit:
                max_exposure = ccy_position - limit
            max_units = round(max_exposure / fx_rates_wrt_base_ccy[0], 0)
            if max_units < order.units:
                filtered_order.units = max_units

            # 2nd currency in a sell order
            limit = self.ccy_limit
            if currencies[1] in self.ccy_limits:
                limit = self.ccy_limits[currencies[1]]
                assert limit >= 0, '[%s] cannot be -ve for [%s]' % ("ccy limit", currencies[1])
            if ccy_position2nd < limit:
                max_exposure2nd = limit - ccy_position2nd
            max_units = round(max_exposure2nd / fx_rates_wrt_base_ccy[1], 0)
            if max_units < filtered_order.units:
                filtered_order.units = max_units

        # now check currency level limits
        return filtered_order

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

    def set_rate(self, tick):
        assert tick is not None
        assert tick.instrument is not None
        assert tick.bid is not None
        assert tick.ask is not None

        if tick.instrument not in self.rates:
            self.rates[tick.instrument] = {}
        self.rates[tick.instrument]['bid'] = tick.bid
        self.rates[tick.instrument]['ask'] = tick.ask

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


