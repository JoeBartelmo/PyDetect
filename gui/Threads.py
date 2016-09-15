import json
import threading
import time
from Queue import Empty

import logging
logger = logging.getLogger('mars_logging')

class VideoThread(threading.Thread):
    def __init__(self, vidcap, queue):
        super(VideoThread, self).__init__()
        self._vidcap = vidcap
        self._queue = queue
        self._stop = threading.Event()

        self.transformFunction = None

    def run(self):
        logger.debug('Starting VideoThread @ ' + str(time.time()))
        while self.stopped() is False:
            flag, frame = self._vidcap.read()

            if not flag:
                continue

            if self.transformFunction is not None:
                frame = self.transformFunction(frame)

            self._queue.put(frame)

        self.empty_queue()
        self._vidcap.release()
        logger.debug('Killing Video Thread')

    def empty_queue(self):
        while self._queue.empty() is False:
            try:
                __ = self._queue.get(False)
            except Empty:
                self._queue.task_done()
                break

    def get_ideal_images(self):
        self.ideal_pump = []

        for s in self.streams:
            if s._vidcap.isOpened():
                flag, frame = s._vidcap.read()
                if not flag:
                    continue
                ideal_keypoint = self.fast.detect(frame, None)
                self.ideal_pump.append(stealth_pumpkin(frame, ideal_keypoint))


    def stop(self):
        self._stop.set()
   
    def transform(self, func):
        self.transformFunction = func

    def stopped(self):
        return self._stop.isSet()


class TelemetryThread(threading.Thread):
    def __init__(self, telem_widget, client_queue):
        super(TelemetryThread, self).__init__()
        self._queue = client_queue
        self._widget = telem_widget
        self._stop = threading.Event()

        self.transformFunction = None

    def run(self):
        while self.stopped() is False:
            try:
                record = self._queue.get(False)
                telemetryData = json.loads(record.msg)
                self._widget.set_telemetry_data(telemetryData)
            except Empty:
                pass

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


