import logging
import threading
import sys

logger = logging.getLogger('mars_logging')

class TelemetryThread(threading.Thread):
    def __init__(self, jetson):
        super(TelemetryThread, self).__init__()
        self._jetson = jetson
        self._stop = threading.Event()

    def run(self):
        while self.stopped() is False:
            self._jetson.telemetryController()
        logger.info('Telemetry thread Stopped')

    def stop(self):
        self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()

