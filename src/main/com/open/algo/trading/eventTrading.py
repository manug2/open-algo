import queue
import time
import threading

from com.open.algo.model import TradeBot
import logging


class ListenAndTradeBot(TradeBot):
    def __init__(self, heartbeat, event_queue, prices, strategy, executor, name=None):
        self.heartbeat = heartbeat
        self.events = event_queue
        self.prices = prices
        self.strategy = strategy
        self.executor = executor
        self.trading = False
        if name == None:
            self.logger = logging.getLogger(self.__class__.__name__)
        else:
            self.logger = logging.getLogger('%s-%s', (self.__class__.__name__, name))

    def trade(self):
        """
        Carries out an infinite while loop.
        Polls events queue and directs each event to either
        the strategy evaluater or execution handler.
        The loop will then pause for "heartbeat" seconds and continue.
        """
        self.logger.info('starting..')
        self.trading = True
        self.runInLoop()

    def runInLoop(self):
        while self.trading == True:
            # outer while loop will trigger inner while loop after 'hearbeat'
            self.logger.info('runInLoop..')
            self.pullAndProcess()

    # end of outer while loop after stopping

    def pullAndProcess(self):
        while self.trading == True:
            # while loop to poll for events
            try:
                event = self.events.get(True, self.heartbeat)
            except queue.Empty:
                break
            else:
                if self.logger != None:
                    self.logger.debug('got event')
                if event is not None:
                    try:
                        if event.TYPE == 'TICK':
                            self.strategy.calculate_signals(event)
                        elif event.TYPE == 'ORDER':
                            self.logger.debug('Executing order!')
                            self.executor.execute_order(event)
                        else:
                            self.logger.debug('Not designed to handle event "%s"' % event)
                    except AttributeError:
                        self.logger.warn('Ignoring event without attribute [%s] : %s' % ('TYPE', event))
                        # end of while loop after collecting all events in queue


    def stop(self):
        self.logger.info("stopping..")
        if self.executor != None:
            self.executor.stop()

        self.trading = False

        if self.prices != None:
            self.prices.stop()

        #End of stop()

