__author__ = 'ManuGarg'


def extract_value(record, attr):
    if isinstance(record, dict):
        value = record[attr]
    else:
        value = getattr(record, attr)
    return value

from com.open.algo.utils import get_age_seconds, get_time
TIME_CALC_TOLERANCE = 0.000000001


class TWMA:

    def __init__(self, period, base_value=0.0, base_time=get_time()):
        assert period > 0.0, 'require time period > 0 for calculating time weighted moving averages, given [%s]' % period
        self.period = period
        self.last_time = base_time
        self.last_twma = base_value

    def __call__(self, time, value):
        age = get_age_seconds(time, self.last_time)

        if age - self.period > TIME_CALC_TOLERANCE:
            new_twma = value
        else:
            c = (self.period - age) / self.period
            new_twma = (c * self.last_twma) + ((1 - c) * value)

        self.last_time = time
        self.last_twma = new_twma
        return new_twma


class TickTWMA:
    def __init__(self, period, base_tick, attribute, time_attribute='time'):
        self.attr = attribute
        self.time_attr = time_attribute
        last_value = extract_value(base_tick, self.attr)
        last_time = extract_value(base_tick, self.time_attr)
        self.ma_func = TWMA(period, base_value=last_value, base_time=last_time)

    def __call__(self, tick):
        new_value = extract_value(tick, self.attr)
        new_time = extract_value(tick, self.time_attr)
        return self.ma_func(new_time, new_value)
