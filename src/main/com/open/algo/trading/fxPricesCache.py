__author__ = 'ManuGarg'


from com.open.algo.model import MarketRateCache
import logging
from queue import Empty

class FxPricesCache(MarketRateCache):

    def __init__(self, heartbeat=0.5, events=None, name=None):
        self.rates = {}
        self.rates_tuples = {}
        self.started = False
        self.events = events
        if name is None:
            self.logger = logging.getLogger(self.__class__.__name__)
        else:
            self.logger = logging.getLogger('%s-%s', (self.__class__.__name__, name))
        self.heartbeat = heartbeat

    def set_rate(self, tick):
        assert tick is not None
        assert tick.instrument is not None
        assert tick.bid is not None
        assert tick.ask is not None

        if tick.instrument not in self.rates:
            self.rates[tick.instrument] = {}
        self.rates[tick.instrument]['bid'] = tick.bid
        self.rates[tick.instrument]['ask'] = tick.ask

        self.rates_tuples[tick.instrument] = (tick.bid, tick.ask)

    def get_rate(self, instrument):
        assert instrument is not None
        rates = self.rates[instrument]
        return rates

    def get_rate_tuple(self, instrument):
        assert instrument is not None
        rates = self.rates_tuples[instrument]
        return rates

    def start(self):
        """
        Carries out an infinite while loop.
        Polls events queue update rates
        The loop will then block for "heartbeat" to seek new events.
        """
        self.logger.info('starting..')
        self.started = True
        self.run_in_loop()

    def run_in_loop(self):
        while self.started:
            # outer while loop will trigger inner while loop after 'heartbeat'
            self.logger.info('run_in_loop..')
            self.pull_process()

    # end of outer while loop after stopping

    def pull_process(self):
        while self.started:
            # while loop to poll for events
            try:
                event = self.events.get(True, self.heartbeat)
            except Empty:
                break
            else:
                if self.logger is not None:
                    self.logger.debug('got event')
                if event is not None:
                    try:
                        if event.TYPE == 'TICK':
                            self.set_rate(event)
                        elif self.logger.isEnabledFor(logging.DEBUG):
                            self.logger.debug('Not designed to handle event "%s"' % event)
                    except AttributeError:
                        self.logger.warn('Ignoring event without attribute [%s] : %s' % ('TYPE', event))
                        # end of while loop after collecting all events in queue

    def stop(self):
        self.logger.info("stopping..")
        self.started = False
        # End of stop()