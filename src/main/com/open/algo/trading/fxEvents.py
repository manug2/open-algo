from com.open.algo.model import Event
from com.open.algo.utils import EVENT_TYPES_FILL, EVENT_TYPES_FILTERED, EVENT_TYPES_TICK, EVENT_TYPES_REJECTED, EVENT_TYPES_ORDER

ORDER_SIDE_BUY = 'buy'
ORDER_SIDE_SELL = 'sell'

ORDER_TYPE_MARKET = 'market'
ORDER_TYPE_LIMIT = 'limit'


class TickEvent(Event):
    def __init__(self, instrument, time, bid, ask, receive_time=None):
        super(TickEvent, self).__init__(EVENT_TYPES_TICK)
        self.instrument = instrument
        self.time = time
        self.bid = bid
        self.ask = ask
        self.receive_time = receive_time

    def to_string(self):
        msg = '%s(%s,%f,%f,%s, %s)' % \
              (self.__class__.__name__, self.instrument, self.bid, self.ask, self.time, self.receive_time)
        return msg


class OrderEvent(Event):
    def __init__(self, instrument, units, side, order_type=ORDER_TYPE_MARKET, price=None, lowerBound=None, upperBound=None,
                 stopLoss=None, takeProfit=None, expiry=None, trailingStop=None):

        super(OrderEvent, self).__init__(EVENT_TYPES_ORDER)

        assert instrument is not None, 'order cannot be made with none "instrument"'
        assert len(instrument) > 0, 'order cannot be made with empty "instrument" string'
        self.instrument = instrument
        assert isinstance(units, int), 'order can be made with integral "units" only, found %s' % units
        assert units > 0, 'order cannot be made with "units" less than or equal to zero, found %s' % units
        self.units = units
        self.orig_units = units
        assert order_type == ORDER_TYPE_MARKET or order_type == ORDER_TYPE_LIMIT, \
            'order type can be only "%s" or "%s", found "%s"' % (ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT, order_type)
        self.order_type = order_type
        assert side == ORDER_SIDE_BUY or side == ORDER_SIDE_SELL, \
            'side can be only "%s" or "%s", found "%s"' % (ORDER_SIDE_BUY, ORDER_SIDE_SELL, side)
        self.side = side

        if price is not None:
            assert isinstance(price, float), 'order can be made with decimal "price" only, found %s' % price
        self.price = price
        self.lowerBound = lowerBound
        self.upperBound = upperBound
        self.stopLoss = stopLoss
        self.takeProfit = takeProfit
        self.expiry = expiry
        self.trailingStop = trailingStop

    def to_string(self):
        msg = '%s(%s,%s,%s,%s,%s' % (self.__class__.__name__, self.TYPE, self.instrument, self.units
                                  , self.order_type, self.side)
        for attr in ['price', 'lowerBound', 'upperBound', 'stopLoss', 'takeProfit', 'trailingStop', 'expiry']:
            value = getattr(self, attr)
            if value is not None:
                msg = '%s, %s=%s' % (msg, attr, value)
        msg += ')'
        return msg

    def get_signed_units(self):
        if self.side == ORDER_SIDE_BUY:
            return self.units
        else:
            return -self.units

    def get_signed_orig_units(self):
        if self.side == ORDER_SIDE_BUY:
            return self.orig_units
        else:
            return -self.orig_units


class ExecutedOrder(Event):
    def __init__(self, order_event, execution_price, execution_units, receive_time=None):

        super(ExecutedOrder, self).__init__(EVENT_TYPES_FILL)

        self.order = order_event
        assert isinstance(execution_price, float), \
            'executed order can be made with decimal "units" only, found %s' % execution_price
        self.price = execution_price
        assert isinstance(execution_units, int), \
            'executed order can be made with integral "units" only, found %s' % execution_units
        assert execution_units >= 0, 'executed order cannot be made with amount less than zero'
        self.units = execution_units
        self.receive_time = receive_time

    def get_signed_units(self):
        if self.order.side == ORDER_SIDE_BUY:
            return self.units
        else:
            return -self.units

    def to_string(self):
        msg = '%s(%f,%s,%s,%s)' % (self.__class__.__name__, self.price, self.units, self.receive_time, self.order)
        return msg
