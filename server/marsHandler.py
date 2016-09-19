import threading
import sys
import logging
from select import select
sys.path.insert(0, '../mars')
import run as Mars #note as long as __main__ is defined this will write a usage violation to the console

MARS_EXIT_COMMAND = 'exit'

class MarsThread(threading.Thread):
    '''
    The idea here is that the client will connect
    And we want to keep mars chugging when the client losses connection.
    We want to easily reconnnect, so we stick with queues here, mars won't stop
    until mars is explicitly stopped or watchdog stop is triggered
    '''
    def __init__(self, configuration, marsCommandQueue, marsConnectionQueue, marsOnlineQueue, debugEnabled = False):
        super(MarsThread, self).__init__()
        self._stop = threading.Event()

        self.config = configuration
        self.marsCommandQueue = marsCommandQueue
        self.marsConnectionQueue = marsConnectionQueue
        self.marsOnlineQueue = marsOnlineQueue
        self.debugEnabled = debugEnabled

    def run(self):
        Mars.run(self.config, self.marsCommandQueue, self.marsConnectionQueue, self.marsOnlineQueue, self.debugEnabled)
        '''
        Here we are on death. Usually Because mars quit, we would expect all logging to stop,
        but it persists because we still have the server up.
        To prevent logging handlers from just getting indefinitely larger, we remove them all on quit of mars
        '''
        debugLog = logging.getLogger('mars_logging')
        telemetryLog = logging.getLogger('telemetry_logging')
        debugLog.handlers = []
        telemetryLog.handlers = []
    def stop(self):
        self.marsCommandQueue.put(MARS_EXIT_COMMAND)
