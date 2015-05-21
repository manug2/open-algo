__author__ = 'ManuGarg'


from com.open.algo.model import Portfolio


class FxPortfolio(Portfolio):
    """
        port_limit - ccy exposure limit for whole portfolio
        port_limit_short - ccy exposure limit for whole portfolio

        short limits are specified in -ve numbers, with a max of 0
        short limits are specified in -ve numbers, with a max of 0
    """

    def __init__(self, base_ccy, balance, decimals=2, port_limit=100, port_limit_short=-100):
        self.positions = {}         # used to capture total number of open positions per instrument
        self.executions = []        # used to capture all executions
        self.positions_avg_price = {}   # used to capture avg price of open positions per instrument
        self.realized_pnl = 0.0     # captures realized pnl
        self.opening_balance = balance
        self.balance = balance
        self.decimals = decimals

        assert base_ccy is not None, 'portfolio manager needs a base currency'
        assert base_ccy != '', 'portfolio manager needs a base currency'
        self.base_ccy = base_ccy

        assert port_limit > 0, '[%s] is [%s] for [%s]' % ("portfolio limit", port_limit, self.__class__.__name__)
        self.port_limit = port_limit  # ccy exposure limit for whole portfolio
        assert port_limit_short < 0, '[%s] is -ve for [%s]' % ("portfolio short limit", self.__class__.__name__)
        self.port_limit_short = port_limit_short  # ccy exposure limit for whole portfolio

        self.price_cache = None
        self.ccy_exposure_manager = None

    def set_price_cache(self, prices_cache):
        if self.price_cache is None:
            self.price_cache = prices_cache
        else:
            raise RuntimeError('[%s] can be only assigned once, cannot be re-assigned' % 'prices_cache')
        return self

    def set_ccy_exposure_manager(self, ccy_exposure_manager):
        if self.ccy_exposure_manager is None:
            if ccy_exposure_manager is None:
                raise ValueError('portfolio ccy exposure manager is None')
            if ccy_exposure_manager is not None and self.base_ccy != ccy_exposure_manager.get_base_ccy():
                raise ValueError('portfolio base currency [%s] does not match ccy exposure manager base currency [%s]'
                                 % (self.base_ccy, ccy_exposure_manager.get_base_ccy()))
            self.ccy_exposure_manager = ccy_exposure_manager
        else:
            raise RuntimeError('[%s] can be only assigned once, cannot be re-assigned' % 'ccy_exposure_manager')
        return self

    def list_positions(self):
        return self.positions

    def append_position(self, executed_order):
        nett_units = executed_order.units
        self.executions.append(executed_order)
        if executed_order.order.side == 'buy':
            multiplier = 1
        else:
            multiplier = -1

        if executed_order.order.instrument not in self.positions:
            self.positions[executed_order.order.instrument] = multiplier * executed_order.units
            self.positions_avg_price[executed_order.order.instrument] = executed_order.price
        else:
            old_units = self.positions[executed_order.order.instrument]
            nett_units = old_units + multiplier * executed_order.units
            if nett_units == 0:
                self.close_out_position(executed_order)
            else:
                old_avg_price = self.positions_avg_price[executed_order.order.instrument]
                new_avg_price1 = (old_units * old_avg_price + multiplier * executed_order.units * executed_order.price)
                new_avg_price = round(new_avg_price1 / nett_units, self.decimals)
                self.positions[executed_order.order.instrument] = nett_units
                self.positions_avg_price[executed_order.order.instrument] = abs(new_avg_price)

        # now append individual currency positions
        if nett_units != 0 and self.ccy_exposure_manager is not None:
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

    def get_balance(self):
        return self.balance

    def close_out_position(self, executed_order):
        old_avg_price = self.positions_avg_price[executed_order.order.instrument]
        position_pnl = executed_order.units * (executed_order.price - old_avg_price)
        position_pnl_in_port_ccy = position_pnl
        self.realized_pnl += round(position_pnl_in_port_ccy, self.decimals)
        self.positions[executed_order.order.instrument] = 0
        self.positions_avg_price[executed_order.order.instrument] = 0