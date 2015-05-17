from com.open.algo.model import ExecutionCostPredictor

from com.open.algo.calcs.ma import sma as ma
from com.open.algo.utils import EventHandler


class FxSpreadCostEvaluator(ExecutionCostPredictor, EventHandler):

    def __init__(self, events, period=14, heart_beat=0.5, decimals=5):
        self.TYPE = 'TICK'
        self.rates = {}
        self.last_tick = None
        self.spreads = {}
        self.events = events
        self.trading = True
        self.heart_beat = heart_beat
        self.period = period
        self.decimals = decimals

    def __str__(self):
        msg = self.__class__.__name__
        return msg

    def eval_cost(self, order):
        return round(ma(self.spreads[order.instrument], period=self.period), self.decimals)

    def append_rate(self, tick):
        self.last_tick = tick
        if tick.instrument not in self.spreads:
            self.spreads[tick.instrument] = []

        spreads_for_instrument = self.spreads[tick.instrument]
        spreads_for_instrument.insert(0, round(tick.ask-tick.bid, self.decimals))

    def get_last_tick(self):
        return self.last_tick

    def get_last_spread(self, instrument):
        return self.spreads[instrument][0]

    def process(self, event):
        self.append_rate(event)

    def start(self):
        super().start()

    def stop(self):
        super().stop()
