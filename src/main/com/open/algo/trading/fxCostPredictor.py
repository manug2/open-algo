from com.open.algo.model import ExecutionCostPredictor
from queue import Empty

from com.open.algo.calcs.ma import sma as ma

class FxSpreadCostEvaluator(ExecutionCostPredictor):
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

    def run_in_loop(self):
        while self.trading:
            # outer while loop will trigger inner while loop after 'heart_beat'
            self.logger.info('run_in_loop..')
            self.pull_process()

    def pull_process(self):
        while self.trading:
            # while loop to poll for events
            try:
                event = self.events.get(True, self.heart_beat)
            except Empty:
                break
            else:
                if event is not None:
                    try:
                        if event.TYPE == 'TICK':
                            self.append_rate(event)
                        else:
                            print('Not designed to handle event "%s"' % event)
                    except AttributeError as e:
                        print('Ignoring event without attribute [%s] : %s' % (e.args, event))
                        # end of while loop after collecting all events in queue
