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
import socket
from select import select
import datetime
import calendar
import time
import struct
import errno
from socket import error as socket_error
from constants import *
from Queue import Empty

logger = logging.getLogger('mars_logging')

class SenderThread(threading.Thread):
    '''
    This thread is responsible for updating mars every PING_RATE seconds with
    client datetime for server connection verification. In addition, it is responsible
    for sending the commands from the client Queue
    '''
    def __init__(self, serverAddr, port, commandQueue, connection):
        super(SenderThread, self).__init__()
        self._stop = threading.Event()
        self._init = threading.Event()
        self.serverAddr = serverAddr
        self.port = port
        self.commandQueue = commandQueue
        self.connection = connection
    
    def run(self):
        '''
        1) Send ping over to socket
            On fail -> we must be disconnected, raise exception which falls back to client.py

        2) Check to see if there's anything on our Command Queue, if there is, send it.
        '''
        logger.warning('Launching client ping thread on port ' + str(self.port))
        sock = socket.create_connection((self.serverAddr, self.port))

        while self.stopped() != True:
            try:
                readyState = select([],[sock,],[], SOCKET_TIMEOUT)
                if readyState[1]:
                    datetime = self.microtime()
                    sock.sendall(FLOAT_PACKER.pack(datetime))
                else:
                    logger.error('Client could not ping server')
                    self.stop()
                if not self.isInit():
                    self._init.set()
                time.sleep(PING_RATE)
            except socket_error as serr:
                if serr.errno == errno.ECONNREFUSED or serr.errno == errno.EPIPE:
                    logger.critical('Was not able to connect to Ping socket, closing app')
                    break
                raise serr

            if not self.commandQueue.empty():
                try:
                    command = self.commandQueue.get(False)
                    logger.info('Sending Command "' + command  + '" to the server')
                    self.connection.sendall(command)
                except Empty:
                    pass

        sock.close()
        self.stop()
        logger.warning('Sender thread stopped')

    def microtime(self):
        unixtime = datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
        return unixtime.days*24*60*60 + unixtime.seconds + unixtime.microseconds/1000000.0

    def isInit(self):
        return self._init.isSet()

    def stop(self):
        self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()

