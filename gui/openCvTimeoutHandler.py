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

import threading
import logging
from threading import Thread
import logging
from select import select
from socket import error as socket_error
import cv2
import time

logger = logging.getLogger('mars_logging')

class _openCvCapture(threading.Thread):
    '''
    This is a private thread that's intent is to launch the videoCapture

    OpenCV has no way of handling a timeout for rtsp connections
    On occassion, our system will attempt to connect to a port that
    has not yet launched it's stream, in this event, we want to steamroll
    over this and ignore. By default it attempts to connect for 10 seconds
    from what I can figure, but we don't want to hold up the client that long
    '''
    def __init__(self, name, rtspLocation):
        super(_openCvCapture, self).__init__()
        self.connectEvent = threading.Event()
        self.rtspLocation = rtspLocation
        self.videoCapture = cv2.VideoCapture()

    def run(self):
        logger.info('Attempting to connect to ' + self.name + ' at ' + self.rtspLocation)
        self.videoCapture.open(self.rtspLocation)
        if self.videoCapture.isOpened():
            self.connectEvent.set()

    def getVideoCapture(self):
        return self.videoCapture
   
    def isConnected(self):
        return self.connectEvent.isSet()

    def disconnect(self):
        if self.videoCapture.isOpened():
            self.videoCapture.release()
        self.connectEvent.clear()

class OpenCvCapture(threading.Thread):
    '''
    This Thread launches an _openCvCapture Thread and controls the timeout
    '''
    def __init__(self, name, rtspLocation,timeout = 1.5):
        super(OpenCvCapture, self).__init__()
        self.captureThread = _openCvCapture(name, rtspLocation)
        self.timeout = timeout
    
    def run(self):
        if self.isConnected():
            logger.error('Attempted to connect to ' + self.name + ' while videoCapture stream already open')
        else:
            self.captureThread.start()
            startTime = time.time()
            while time.time() - startTime  < self.timeout and not self.isConnected():
                time.sleep(0.1)

            if self.isConnected():
                logger.info('Succesfully connected to ' + self.name)
            else:
                logger.error('Could not connect to RTSP stream ' + self.name + ' within ' + str(self.timeout) + ' seconds')

    def getVideoCapture(self):
        return self.captureThread.getVideoCapture()
 
    def isConnected(self):
        return self.captureThread.isConnected()

    def disconnect(self):
        self.captureThread.disconnect()
