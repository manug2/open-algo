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
        self.executor = None

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

    def start_all_async(self):
        starter_thread = Thread(target=self.start_all)
        logger = logging.getLogger(self.__class__.__name__)
        logger.info('starting the various tasks in started processes..')
        starter_thread.start()
        sleep(2)
        self.join_all()
        logger.info('joining starter thread for processes..')
        starter_thread.join()

    def start_all(self):
        logger = logging.getLogger(self.__class__.__name__)

        logger.info('[%s-%s] before submitting tasks in separate processes..' % (os.getppid(), os.getpid()))
        if self.started:
            raise RuntimeError('i have already started targets')
        elif len(self.process_target_map) == 0:
            raise RuntimeError('no targets to start')

        starters = {group: ThreadStarter(group, targets) for group, targets in self.process_target_map.items()}
        self.executor = concurrent.futures.ProcessPoolExecutor(max_workers=len(starters))
        self.process_futures = {self.executor.submit(starter.start): starter for group, starter in starters.items()}
        logger.info('[%s-%s] started task/groups in separate processes..' % (os.getppid(), os.getpid()))
        for f in self.process_futures:
            f.add_done_callback(self.process_completed)

    def process_completed(self, future):
        starter = self.process_futures[future]
        try:
            returnValue = future.result()
        except Exception as exc:
            logger.info('[%s-%s] process for starting [%s, %s] generated an exception: %s'
                  % (os.getppid(), os.getpid(), starter.group, starter.targets, exc))
        else:
            logger.info('[%s-%s] process for starting [%s, %s] generated an result: %s'
                        % (os.getppid(), os.getpid(), starter.group, starter.targets, returnValue))
        logger.info('[%s-%s] completed starting process for group [%s]' % (os.getppid(), os.getpid(), starter.group))

    def join_all(self):
        logger = logging.getLogger(self.__class__.__name__)
        logger.info('[%s-%s] joining all processes ..' % (os.getppid(), os.getpid()))
        ''''
        for future in self.process_futures:
            starter = self.process_futures[future]
            try:
                starter.join()
            except Exception as exc:
                logger.info('[%s-%s] error joining [%s, %s] generated an exception: %s'
                      % (os.getppid(), os.getpid(), starter.group, starter.targets, exc))
            else:
                logger.info('[%s-%s] all work for [%s, %s] finished'
                            % (os.getppid(), os.getpid(), starter.group, starter.targets))
        '''''
        self.executor.shutdown(wait=True)
        logger.info('[%s-%s] completed all processes.' % (os.getppid(), os.getpid()))


class ThreadStarter:
    def __init__(self, group, targets):
        self.group = group
        self.targets = targets
        self.started = False
        self.futures = None
        self.executor = None

    def start(self):
        logger = logging.getLogger(self.__class__.__name__)
        logger.info('[%s-%s] before submitting tasks in separate threads..' % (os.getppid(), os.getpid()))
        if self.started:
            raise RuntimeError('i have already started targets')

        for t in self.targets:
            logger.info('[%s-%s] starting [%s] in group [%s]' % (os.getppid(), os.getpid(), t, self.group))

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(self.targets))
        self.futures = {self.executor.submit(target_method, target_args):
                           (target_method, target_args) for target_method, target_args in self.targets}

        logger.info('[%s-%s] tasks started in separate threads.' % (os.getppid(), os.getpid()))
        for f in self.futures:
            f.add_done_callback(self.task_completed)

    def task_completed(self, future):
        (target_method, target_args) = self.futures[future]
        try:
            returnValue = future.result()
        except Exception as exc:
            logger.error('[%s-%s] [%s, %s] generated an exception: %s'
                        % (os.getppid(), os.getpid(), target_method, target_args, exc))
        else:
            logger.info('[%s-%s] [%s, %s] generated return value : %s'
                        % (os.getppid(), os.getpid(), target_method, target_args, returnValue))

    def join(self):
        logger = logging.getLogger(self.__class__.__name__)
        logger.info('[%s-%s] joining of threads in group [%s]..' % (os.getppid(), os.getpid(), self.group))
        self.executor.shutdown(wait=True)
        logger.info('[%s-%s] completed execution of threaded tasks in group [%s]'
                    % (os.getppid(), os.getpid(), self.group))
