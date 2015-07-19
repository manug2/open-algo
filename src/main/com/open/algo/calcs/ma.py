__author__ = 'ManuGarg'


def sma(data, period=None, attribute=None, attributes=None):
    if data is None:
        raise ValueError('input data list is None')

    len_data = len(data)
    if len_data == 0:
        raise ValueError('input data list is empty')

    if period is None or period > len_data:
        period = len_data

    if attributes is not None:
        total = {}
        avg = {}
        for attr in attributes:
            total[attr] = 0.0
            avg[attr] = 0.0

        for i in range(1, period+1):
            for attr in attributes:
                value = extract_value(data[len_data - i], attr)
                total[attr] += value

        for attr in attributes:
            avg[attr] = total[attr] / period
        return avg

    elif attribute is not None:
        total = 0.0
        for i in range(1, period+1):
            value = extract_value(data[len_data - i], attribute)
            total += value
        return total / period
    else:
        total = 0.0
        for i in range(1, period+1):
            value = data[len_data - i]
            total += value
        return total / period


def extract_value(record, attr):
    if isinstance(record, dict):
        value = record[attr]
    else:
        value = getattr(record, attr)
    return value
