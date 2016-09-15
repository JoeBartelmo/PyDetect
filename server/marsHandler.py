import threading
import sys
from select import select
sys.path.insert(0, '../mars')
import run as Mars #note as long as __main__ is defined this will write a usage violation to the console

class MarsThread(threading.Thread):
    '''
    This is an unstopable thread. The idea here is that the client will connect
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

