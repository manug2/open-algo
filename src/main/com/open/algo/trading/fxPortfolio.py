__author__ = 'ManuGarg'


from com.open.algo.model import Portfolio
from com.open.algo.eventLoop import EventHandler
from com.open.algo.trading.fxEvents import EVENT_TYPES_ORDER, EVENT_TYPES_FILL


class FxPortfolio(Portfolio, EventHandler):
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
        self.risk_managers = list()

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
            new_units = executed_order.units
        else:
            new_units = -executed_order.units

        if executed_order.order.instrument not in self.positions:
            self.positions[executed_order.order.instrument] = new_units
            self.positions_avg_price[executed_order.order.instrument] = executed_order.price
        else:
            old_units = self.positions[executed_order.order.instrument]
            nett_units = old_units + new_units
            if nett_units == 0:
                self.close_out_position(executed_order)
            elif abs(nett_units) < executed_order.units or abs(nett_units) < abs(old_units):
                self.partial_close_position(executed_order, new_units, nett_units, old_units)
            else:
                self.extend_position(executed_order, new_units, nett_units, old_units)

        # now append individual currency positions
        if self.ccy_exposure_manager is not None:
            currencies = executed_order.order.instrument.split('_')
            self.ccy_exposure_manager.append_position(currencies[0],  new_units)
            self.ccy_exposure_manager.append_position(currencies[1], -new_units)

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

    def partial_close_position(self, executed_order, new_units, nett_units, old_units):
        assert old_units * new_units < 0, \
            'For partial close of position, new and old units must have opposite sign, found [%s, %s]' % \
                (new_units, old_units)
        old_avg_price = self.positions_avg_price[executed_order.order.instrument]
        position_pnl = executed_order.units * (executed_order.price - old_avg_price)
        position_pnl_in_port_ccy = position_pnl
        self.realized_pnl += round(position_pnl_in_port_ccy, self.decimals)

        if abs(old_units) > abs(new_units):
            new_avg_price = old_avg_price
        else:
            new_avg_price = executed_order.price
        self.positions[executed_order.order.instrument] = nett_units
        self.positions_avg_price[executed_order.order.instrument] = abs(new_avg_price)

    def extend_position(self, executed_order, new_units, nett_units, old_units):
        old_avg_price = self.positions_avg_price[executed_order.order.instrument]
        new_avg_price1 = (old_units * old_avg_price + new_units * executed_order.price)
        new_avg_price = round(new_avg_price1 / nett_units, self.decimals)
        self.positions[executed_order.order.instrument] = nett_units
        self.positions_avg_price[executed_order.order.instrument] = abs(new_avg_price)

    def start(self):
        # read state from journals
        pass

    def stop(self):
        # write state from journals
        pass

    def process(self, order):
        if order is None:
            raise ValueError('Found "None", was expecting to process order')
        elif not hasattr(order, 'TYPE'):
            raise TypeError('Cannot evaluate input event as it does not have field "%s" - [%s]' % ('TYPE', order))

        if order.TYPE == EVENT_TYPES_ORDER:
            return self.check_order(order)
        elif order.TYPE == EVENT_TYPES_FILL:
            self.append_position(order)
        # end of process

    def check_order(self, order):
        filtered_order = self.ccy_exposure_manager.filter_order(order)
        if filtered_order.units == 0:
            raise RuntimeError('order is filtered completely by currency exposure manager - [%s]' % order)
        for rm in self.risk_managers:
            filtered_order = rm.filter_order(filtered_order)
            if filtered_order.units == 0:
                raise RuntimeError('order is filtered completely by risk manager [%s] - [%s]' % (rm, order))
        return filtered_order
    # end of check_order

    def add_risk_manager(self, risk_manager):
        if risk_manager in self.risk_managers:
            raise ValueError('risk manager has already been added to portfolio - [%s]' % risk_manager)
        else:
            self.risk_managers.append(risk_manager)
        return self

