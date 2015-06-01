from com.open.algo.model import Heartbeat
from com.open.algo.trading.fxEvents import TickEvent

__author__ = 'ManuGarg'


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