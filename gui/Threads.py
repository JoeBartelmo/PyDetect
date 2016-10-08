# Copyright (c) 2016, Jeffrey Maggio and Joseph Bartelmo
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial 
# portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import json
import threading
import time
from Queue import Empty
from openCvTimeoutHandler import *
import logging
logger = logging.getLogger('mars_logging')

class VideoThread(threading.Thread):
    def __init__(self, name, rtspLocation, queue):
        super(VideoThread, self).__init__()
        self._vidcap = None
        self._openCvCapture = OpenCvCapture(name, rtspLocation)
        self._openCvCapture.start()
        self._queue = queue
        self._stop = threading.Event()
        self._name = name

        self.transformFunction = None

    def run(self):
        #wait until timeout has been met before we attempt to connect
        #to a camera that may or may not exist
        logger.info('Attempting to start Vidcap on ' + self._name)
        while (self._openCvCapture.is_alive()):
            time.sleep(0.01)
        
        if self._openCvCapture.isConnected():
            self._vidcap = self._openCvCapture.getVideoCapture()
            logger.debug('Starting VideoThread @ ' + str(time.time()))
            while self.stopped() is False:
                flag, frame = self._vidcap.read()

                if not flag:
                    continue
                
                self._queue.put(frame)

            self._vidcap.release()
            self._openCvCapture.disconnect()
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
            if s._vidcap is not None and s._vidcap.isOpened():
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


