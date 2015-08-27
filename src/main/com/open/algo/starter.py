__author__ = 'maverick'
import logging
import concurrent.futures
import os

logger = logging.getLogger('')


class ProcessStarter:
    def __init__(self):
        self.process_starter_map = {}
        self.started = False
        self.process_futures = None
        self.executor = None

    def add_target(self, target_method, process_group='default'):
        if self.started:
            raise RuntimeError('cannot accept new target as already started others')

        if process_group not in self.process_starter_map:
            self.process_starter_map[process_group] = ThreadStarter(group=process_group)
        self.process_starter_map[process_group].add_target(target_method)
        return self

    def start(self):
        logger = logging.getLogger(self.__class__.__name__)

        logger.info('[%s-%s] before submitting tasks in separate processes..' % (os.getppid(), os.getpid()))
        if self.started:
            raise RuntimeError('i have already started targets')
        elif len(self.process_starter_map) == 0:
            raise RuntimeError('no targets to start')

        self.executor = concurrent.futures.ProcessPoolExecutor(max_workers=len(self.process_starter_map))
        self.process_futures = {self.executor.submit(starter.start): starter
                                for group, starter in self.process_starter_map.items()}
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

    def join(self):
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

from threading import Lock


class ThreadStarter:
    def __init__(self, group='default'):
        self.group = group
        self.targets = []
        self.started = False
        self.futures = None
        self.executor = None
        self.join_count = 0

    def add_target(self, target_method, process_group=None):
        if self.started:
            raise RuntimeError('cannot accept new target as already started others')

        if target_method in self.targets:
            raise ValueError('target [%s] already added with args [%s]' % target_method)
        else:
            self.targets.append(target_method)
        return self

    def start(self):
        logger = logging.getLogger(self.__class__.__name__)
        logger.info('[%s-%s] before submitting tasks in separate threads..' % (os.getppid(), os.getpid()))
        if self.started:
            raise RuntimeError('i have already started targets')

        self.started = True
        for t in self.targets:
            logger.info('[%s-%s] starting [%s] in group [%s]' % (os.getppid(), os.getpid(), t, self.group))

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(self.targets))
        self.futures = {self.executor.submit(target_method): target_method for target_method in self.targets}

        logger.info('[%s-%s] tasks started in separate threads.' % (os.getppid(), os.getpid()))

    def task_completed(self, future):
        target_method = self.futures[future]
        try:
            returnValue = future.result()
        except Exception as exc:
            logger.error('[%s-%s] [%s] generated an exception: %s'
                        % (os.getppid(), os.getpid(), target_method, exc))
        else:
            logger.info('[%s-%s] [%s] generated return value : %s'
                        % (os.getppid(), os.getpid(), target_method, returnValue))
        with Lock():
            self.join_count += 1

    def join(self, timeout=None):
        logger = logging.getLogger(self.__class__.__name__)
        logger.info('[%s-%s] joining of threads in group [%s]..' % (os.getppid(), os.getpid(), self.group))

        try:
            for future in concurrent.futures.as_completed(self.futures, timeout=timeout):
                self.task_completed(future)
        except:
            import sys
            logger.error('error waiting for various targets to complete [%s]' % sys.exc_info()[0])
            for future in self.futures:
                logger.info('Completion status is [%s], for task [%s]' % (future.done(), self.futures[future]))

        if self.join_count == len(self.futures):
            self.executor.shutdown(wait=False)
        else:

            logger.info('[%s-%s] execution of threaded tasks in group [%s] is NOT complete. waiting..'
                    % (os.getppid(), os.getpid(), self.group))
            self.executor.shutdown(wait=True)

        logger.info('[%s-%s] completed execution of threaded tasks in group [%s]'
                    % (os.getppid(), os.getpid(), self.group))
