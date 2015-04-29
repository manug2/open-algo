from com.open.algo.model import Event


class TickEvent(Event):
    def __init__(self, instrument, time, bid, ask):
        self.TYPE = 'TICK'
        self.instrument = instrument
        self.time = time
        self.bid = bid
        self.ask = ask

    def to_string(self):
        msg = self.__class__.__name__ + "(" + self.instrument + ","
        msg = msg + str(self.bid) + "," + str(self.ask) + "," + self.time + ")"
        return msg

class OrderEvent(Event):
    def __init__(self, instrument, units, side, order_type='market', price=None, lowerBound=None, upperBound=None,
                 stopLoss=None, takeProfit=None, expiry=None, trailingStop=None):
        self.TYPE = 'ORDER'
        assert instrument is not None, 'order cannot be made with none "instrument"'
        assert len(instrument) > 0, 'order cannot be made with empty "instrument" string'
        self.instrument = instrument
        assert units > 0, 'order cannot be made with "units" less than or equal to zero'
        self.units = units
        assert order_type == 'market' or order_type == 'limit', 'side can be only "market" or "limit"'
        self.order_type = order_type
        assert side == 'buy' or side == 'sell', 'side can be only "buy" or "sell"'
        self.side = side

        self.price = price
        self.lowerBound = lowerBound
        self.upperBound = upperBound
        self.stopLoss = stopLoss
        self.takeProfit = takeProfit
        self.expiry = expiry
        self.trailingStop = trailingStop

    def to_string(self):
        msg = '%s(%s,%s,%s,%s' % (self.__class__.__name__, self.instrument, self.units
                                  , self.order_type, self.side)
        for attr in ['price', 'lowerBound', 'upperBound', 'stopLoss', 'takeProfit', 'trailingStop', 'expiry']:
            value = getattr(self, attr)
            if value is None:
                msg = '%s, %s=%s' % (msg, attr, value)
        msg += ')'
        return msg


class ExecutedOrder(Event):
    def __init__(self, order_event, execution_price, execution_units):
        self.TYPE = 'EXECUTED ORDER'
        self.order = order_event
        self.price = execution_price
        assert execution_units >= 0, 'executed order cannot be made with amount less than zero'
        self.units = execution_units
