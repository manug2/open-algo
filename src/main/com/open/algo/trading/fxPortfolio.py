__author__ = 'ManuGarg'


from com.open.algo.model import Portfolio


class FxPortfolio(Portfolio):
    """
        port_limit - ccy exposure limit for whole portfolio
        port_limit_short - ccy exposure limit for whole portfolio

        short limits are specified in -ve numbers, with a max of 0
        short limits are specified in -ve numbers, with a max of 0
    """

    def __init__(self, base_ccy, prices_cache=None, ccy_exposure_manager=None, decimals=2
                 , port_limit=100, port_limit_short=-100):
        self.positions = {}         # used to capture total number of open positions per instrument
        self.executions = []        # used to capture all executions
        self.positions_avg_price = {}   # used to capture avg price of open positions per instrument
        self.realized_pnl = 0.0     # captures realized pnl

        assert base_ccy is not None, 'portfolio manager needs a base currency'
        assert base_ccy != '', 'portfolio manager needs a base currency'
        self.base_ccy = base_ccy
        self.price_cache = prices_cache

        if ccy_exposure_manager is not None and base_ccy != ccy_exposure_manager.get_base_ccy():
            raise ValueError('portfolio base currency [%s] does not match ccy exposure manager base currency [%s]'
                             % (base_ccy, ccy_exposure_manager.get_base_ccy()))
        self.ccy_exposure_manager = ccy_exposure_manager
        self.decimals = decimals

        assert port_limit > 0, '[%s] is [%s] for [%s]' % ("portfolio limit", port_limit, self.__class__.__name__)
        self.port_limit = port_limit  # ccy exposure limit for whole portfolio
        assert port_limit_short < 0, '[%s] is -ve for [%s]' % ("portfolio short limit", self.__class__.__name__)
        self.port_limit_short = port_limit_short  # ccy exposure limit for whole portfolio

    def list_positions(self):
        return self.positions

    def append_position(self, executed_order):
        self.executions.append(executed_order)
        if executed_order.order.side == 'buy':
            if executed_order.order.instrument not in self.positions:
                self.positions[executed_order.order.instrument] = executed_order.units
                self.positions_avg_price[executed_order.order.instrument] = executed_order.price
            else:
                old_units = self.positions[executed_order.order.instrument]
                new_units = old_units + executed_order.units
                if new_units == 0:
                    self.positions[executed_order.order.instrument] = 0
                    self.positions_avg_price[executed_order.order.instrument] = 0
                else:
                    old_avg_price = self.positions_avg_price[executed_order.order.instrument]
                    new_avg_price = round((old_units * old_avg_price + executed_order.units * executed_order.price)
                                          / new_units, self.decimals)
                    self.positions[executed_order.order.instrument] = new_units
                    self.positions_avg_price[executed_order.order.instrument] = abs(new_avg_price)
        else:
            if executed_order.order.instrument not in self.positions:
                self.positions[executed_order.order.instrument] = -executed_order.units
                self.positions_avg_price[executed_order.order.instrument] = executed_order.price
            else:
                old_units = self.positions[executed_order.order.instrument]
                new_units = old_units - executed_order.units
                if new_units == 0:
                    self.positions[executed_order.order.instrument] = 0
                    self.positions_avg_price[executed_order.order.instrument] = 0
                else:
                    old_avg_price = self.positions_avg_price[executed_order.order.instrument]
                    new_avg_price = round((old_units * old_avg_price - executed_order.units * executed_order.price)
                                          / new_units, self.decimals)
                    self.positions[executed_order.order.instrument] = new_units
                    self.positions_avg_price[executed_order.order.instrument] = abs(new_avg_price)

        # now append individual currency positions
        if self.ccy_exposure_manager is not None:
            currencies = executed_order.order.instrument.split('_')
            if executed_order.order.side == 'buy':
                self.ccy_exposure_manager.append_position(currencies[0],  executed_order.units)
                self.ccy_exposure_manager.append_position(currencies[1], -executed_order.units)
            else:
                self.ccy_exposure_manager.append_position(currencies[0], -executed_order.units)
                self.ccy_exposure_manager.append_position(currencies[1],  executed_order.units)

    # end of append

    def list_executions(self):
        return self.executions

    def list_position(self, instrument):
        return self.positions[instrument]

    def reval_position(self, instrument):
        position = self.positions[instrument]
        if position == 0:
            return 0

        old_price = self.positions_avg_price[instrument]
        rates = self.price_cache.get_rate(instrument)

        if position < 0:
            new_price = rates['bid']
        else:
            new_price = rates['ask']

        return round(position * (new_price-old_price), self.decimals)

    def get_avg_price(self, instrument):
        return self.positions_avg_price[instrument]

    def reval_positions(self):
        if self.ccy_exposure_manager is None:
            raise NotImplementedError('Cannot reval without a currency exposure manager configured')

        ccy_position_map = self.ccy_exposure_manager.list_ccy_position_map()
        value = 0.0
        for ccy, units in ccy_position_map.items():
            if units == 0:
                continue
            if ccy == self.base_ccy:
                value += units
            else:
                rates = self.price_cache.get_rate(ccy + '_' + self.base_ccy)
                if units > 0:
                    cv = units / rates['ask']
                else:
                    cv = units / rates['bid']
                value += cv

        return round(value, self.decimals)

    def get_base_ccy(self):
        return self.base_ccy

    def get_realized_pnl(self):
        return self.realized_pnl