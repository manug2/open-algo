from com.open.algo.model import ExecutionCostPredictor
from queue import Empty

from com.open.algo.calcs.ma import sma as ma

class FxSpreadCostEvaluator(ExecutionCostPredictor):
    def __init__(self, events, period=14, heart_beat=0.5):
        self.TYPE = 'TICK'
        self.rates = {}
        self.last_tick = None
        self.ticks = []
        self.events = events
        self.trading = True
        self.heart_beat = heart_beat
        self.period = period

    def __str__(self):
        msg = self.__class__.__name__
        return msg

    def eval_cost(self, order):
        ma_values = ma(self.ticks, period = self.period, attributes=['bid', 'ask'])
        bid_ma = ma_values['bid']
        ask_ma = ma_values['ask']
        return ask_ma - bid_ma

    def append_rate(self, tick):
        self.last_tick = tick
        self.ticks.insert(0, tick)

    def get_last_tick(self):
        return self.last_tick

    def get_last_spread(self):
        return self.last_tick.ask-self.last_tick.bid

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
                    except AttributeError:
                        print('Ignoring event without attribute [%s] : %s' % ('TYPE', event))
                        # end of while loop after collecting all events in queue
