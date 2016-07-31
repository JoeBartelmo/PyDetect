import logging
import threading
import sys

logger = logging.getLogger('mars_logging')

class StatisticsThread(threading.Thread):
    def __init__(self, jetson):
        super(StatisticsThread, self).__init__()
        self._jetson = jetson
        self._stop = threading.Event()

    def run(self):
        while self.stopped() is False:
            self._jetson.statisticsController()
        logger.info('Statistics thread Stopped')

    def stop(self):
        self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()

