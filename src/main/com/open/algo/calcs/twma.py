__author__ = 'ManuGarg'


def extract_time_and_value(record, time_attr, val_attr):
    if isinstance(record, dict):
        value = record[val_attr]
        time = record[time_attr]
    else:
        value = getattr(record, val_attr)
        time = getattr(record, time_attr)
    return time, value


def extract_value(record, attr):
    if isinstance(record, dict):
        value = record[attr]
    else:
        value = getattr(record, attr)
    return value

from com.open.algo.utils import get_age_seconds
TIME_CALC_TOLERANCE = 0.000000001


class TWMA:
    def __init__(self, time_period, time_attr, val_attr):
        assert time_period > 0, 'time period is required'
        assert time_attr is not None, 'time field is required'
        assert val_attr is not None, 'value field is required'

        self.time_period = time_period
        self.time_attr = time_attr
        self.val_attr = val_attr

    def __call__(self, now, data):
        assert data is not None, 'input data list is required'

        len_data = len(data)
        assert len_data > 0, 'input data list is empty'
        assert now is not None, 'time now is required'

        upper_time = now
        total_time = 0
        accumulator = 0
        index = len_data - 1
        latest_value = 0

        while total_time < self.time_period and index >= 0:
            lower_time, val_at_index = extract_time_and_value(data[index], self.time_attr, self.val_attr)
            delta = get_age_seconds(upper_time, lower_time)

            if delta <= 0.0:
                index -= 1
                continue
            else:
                latest_value = val_at_index

            accumulator += latest_value * delta
            total_time += delta
            upper_time = lower_time
            index -= 1

        if total_time < self.time_period:
            oldest_value = extract_value(data[0], self.val_attr)
            accumulator += oldest_value * (self.time_period-total_time)
        return accumulator / self.time_period
