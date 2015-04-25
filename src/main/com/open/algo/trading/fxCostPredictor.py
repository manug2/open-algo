from com.open.algo.model import ExecutionCostPredictor
from queue import Empty


class FxSpreadCostEvaluator(ExecutionCostPredictor):
    def __init__(self, events, heart_beat=0.5):
        self.TYPE = 'TICK'
        self.rates = {}
        self.last_tick = None
        self.ticks = {}
        self.events = events
        self.trading = True
        self.heart_beat = heart_beat

    def __str__(self):
        msg = self.__class__.__name__
        return msg

    def eval_cost(self, order):
        raise NotImplementedError('should implement "%s()" method' % 'eval_cost')

    def append_rate(self, tick):
        self.last_tick = tick

    def get_last_tick(self):
        return self.last_tick

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
