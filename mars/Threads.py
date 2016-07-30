import threading
import sys

class InputThread(threading.Thread):
    def __init__(self, jetson):
        super(InputThread, self).__init__()
        self._jetson = jetson
        self._stop = threading.Event()

    def run(self):
        while self.stopped() is False:
            self._jetson.safeInput()
        print 'Input thread Stopped'

    def stop(self):
        self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()

class StatisticsThread(threading.Thread):
    def __init__(self, jetson):
        super(StatisticsThread, self).__init__()
        self._jetson = jetson
        self._stop = threading.Event()

    def run(self):
        while self.stopped() is False:
            self._jetson.statisticsController()
        print 'Statistics Thread Stopped'

    def stop(self):
        self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()

