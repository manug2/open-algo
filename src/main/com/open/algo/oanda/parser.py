__author__ = 'ManuGarg'

from com.open.algo.model import Heartbeat, ExceptionEvent
from com.open.algo.trading.fxEvents import *


def parse_tick(receive_time, msg):
    tick = msg["tick"]
    instrument = tick["instrument"]
    time = tick["time"]
    bid = tick["bid"]
    ask = tick["ask"]
    tev = TickEvent(instrument, time, bid, ask, receive_time)
    return tev


def parse_heartbeat(receive_time, msg):
    sent_time = msg["heartbeat"]["time"]
    hb = Heartbeat('oanda-stream', receive_time, sent_time)
    return hb


def parse_event(receive_time, msg):
    if "tick" in msg:
        return parse_tick(receive_time, msg)
    elif "heartbeat" in msg:
        return parse_heartbeat(receive_time, msg)
    else:
        raise ValueError('Unexpected message received')


def parse_execution_response(response, caller=None, orig_event=None):
        has_message = 'message' in response
        if has_message:
            error = 'error executing trade - [%s]' % response
            return ExceptionEvent(caller, error, orig_event)

        has_opened_trade = 'tradeOpened' in response
        if has_opened_trade:
            trade = response['tradeOpened']
            return ExecutedOrder(orig_event, response['price'], trade['units'])
        else:
            error = 'expecting a new trade but got [%s]' % response
            return ExceptionEvent(caller, error, orig_event)


def parse_execution_events(event):
        raise NotImplementedError('to be implemented for execution actions')
