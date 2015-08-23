__author__ = 'maverick'
import logging
import concurrent.futures
import os
from threading import Thread
from time import sleep

logger = logging.getLogger('')


class ProcessStarter:
    def __init__(self):
        self.process_target_map = {}
        self.started = False
        self.starters = None
        self.process_futures = None

    def add_target(self, target_method, process_group='default', args=()):
        if self.started:
            raise RuntimeError('cannot accept new target as already started others')

        if process_group not in self.process_target_map:
            self.process_target_map[process_group] = []
        prev_targets = self.process_target_map[process_group]

        if (target_method, args) in prev_targets:
            raise ValueError('target [%s] already added with args [%s]' % (target_method, args))
        else:
            prev_targets.append((target_method, args))

        return self

    def start_all(self):
        starter_thread = Thread(target=self.start_all_internal)
        logger = logging.getLogger(self.__class__.__name__)
        logger.info('starting the various tasks in started processes..')
        starter_thread.start()
        sleep(2)
        self.join_all()
        logger.info('joining starter thread for processes..')
        starter_thread.join()

    def start_all_internal(self):
        logger = logging.getLogger(self.__class__.__name__)

        logger.info('[%s-%s] before submitting tasks in separate processes..' % (os.getppid(), os.getpid()))
        if self.started:
            raise RuntimeError('i have already started targets')
        elif len(self.process_target_map) == 0:
            raise RuntimeError('no targets to start')

        self.starters = {group: ThreadStarter(group, targets) for group, targets in self.process_target_map.items()}

        with concurrent.futures.ProcessPoolExecutor(max_workers=len(self.starters)) as executor:
            self.process_futures = {executor.submit(starter.start): starter for group, starter in self.starters.items()}

        #logger.info('[%s-%s] started task/groups in separate processes..' % (os.getppid(), os.getpid()))

    def join_all(self):
        logger = logging.getLogger(self.__class__.__name__)
        logger.info('[%s-%s] joining tasks in separate processes..' % (os.getppid(), os.getpid()))

        for future in concurrent.futures.as_completed(self.process_futures):
            starter = self.process_futures[future]
            try:
                returnValue = future.result()
            except Exception as exc:
                logger.info('[%s-%s] process for executing [%s, %s] generated an exception: %s'
                      % (os.getppid(), os.getpid(), starter.group, starter.targets, exc))
            else:
                logger.info('[%s-%s] process for executing [%s, %s] generated an result: %s'
                            % (os.getppid(), os.getpid(), starter.group, starter.targets, returnValue))

            logger.info('[%s-%s] completed execution of group [%s]' % (os.getppid(), os.getpid(), starter.group))
        logger.info('[%s-%s] completed all task/groups in all processes.' % (os.getppid(), os.getpid()))


class ThreadStarter:
    def __init__(self, group, targets):
        self.group = group
        self.targets = targets
        self.started = False
        self.futures = None

    def start(self):
        starter_thread = Thread(target=self.start_internal)
        logger = logging.getLogger(self.__class__.__name__)
        logger.info('starting the various tasks in started thread for group [%s]..' % self.group)
        starter_thread.start()
        sleep(1)
        self.join()
        logger.info('joining started thread for group [%s]..' % self.group)
        starter_thread.join()

    def start_internal(self):
        logger = logging.getLogger(self.__class__.__name__)
        logger.info('[%s-%s] before submitting tasks in separate threads..' % (os.getppid(), os.getpid()))
        if self.started:
            raise RuntimeError('i have already started targets')

        for t in self.targets:
            logger.info('[%s-%s] starting [%s] in group [%s]' % (os.getppid(), os.getpid(), t, self.group))

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.targets)) as executor:
            self.futures = {executor.submit(target_method, target_args):
                           (target_method, target_args) for target_method, target_args in self.targets}

        #logger.info('[%s-%s] tasks in separate threads.' % (os.getppid(), os.getpid()))

    def join(self):
        logger = logging.getLogger(self.__class__.__name__)
        logger.info('[%s-%s] joining of threads in group [%s]..' % (os.getppid(), os.getpid(), self.group))

        for future in concurrent.futures.as_completed(self.futures):
            (target_method, target_args) = self.futures[future]
            try:
                returnValue = future.result()
            except Exception as exc:
                logger.error('[%s-%s] [%s, %s] generated an exception: %s'
                            % (os.getppid(), os.getpid(), target_method, target_args, exc))
            else:
                logger.info('[%s-%s] [%s, %s] generated return value : %s'
                            % (os.getppid(), os.getpid(), target_method, target_args, returnValue))

        logger.info('[%s-%s] completed execution of threaded tasks in group [%s]'
                    % (os.getppid(), os.getpid(), self.group))
