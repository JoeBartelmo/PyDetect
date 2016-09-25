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
import struct
import pickle
import logging
from threading import Thread
import socket
import logging
from select import select
from socket import error as socket_error
import errno

logger = logging.getLogger('mars_logging')
#time at which we should think mars disconnected from us
MARS_TIMEOUT = 5


class ListenerThread(threading.Thread):
    def __init__(self, q, serverAddr, port, logLevel, errorQueue, name = 'Thread', displayInConsole = True):
        super(ListenerThread, self).__init__()
        self._stop = threading.Event()
        self.q = q
        self.serverAddr = serverAddr
        self.port = port
        self.name = name
        self.displayInConsole = displayInConsole
        self.socketTimeout = 3
        self.logLevel = logLevel
        #ideally we want to stop repeat logs on mars side, but for short term
        #this will make client more responsive
        self.lastLogEntry = ""
        
    
    def run(self):
        logger.debug('Client side Listener Thread "'+self.name+'" waiting for connection...')
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self.serverAddr != 'localhost':
            listener.bind(('', self.port))
        else:
            listener.bind(('localhost', self.port))
        listener.listen(1)

        listenerConnection, address = listener.accept()
        listenerConnection.setblocking(0)
        listenerConnection.settimeout(self.socketTimeout)

        logger.warning('Client side Listener Thread "'+self.name+'" connected!')
        while self.stopped() is False:
            isReady = select([listenerConnection],[],[],self.socketTimeout)
            if isReady[0]:
                try:
                    chunk = listenerConnection.recv(4)
                    if chunk is None or len(chunk) < 4:
                        break
                    slen = struct.unpack('>L', chunk)[0]
                    chunk = listenerConnection.recv(slen)
                    while len(chunk) < slen:
                        chunk = chunk + listenerConnection.recv(slen - len(chunk))
                    obj = pickle.loads(chunk)
                    record = logging.makeLogRecord(obj)

                    if record.levelno >= self.logLevel:
                        if self.q is not None and record.msg not in self.lastLogEntry:
                            self.q.put(record)
                            self.lastLogEntry = record.msg
                        if self.displayInConsole:
                            logger.log(record.levelno, record.msg + ' (' + record.filename + ':' + str(record.lineno) + ')')
                except socket_error as serr:
                    if serr.errno == errno.ECONNREFUSED or serr.errno == errno.EPIPE:
                        logger.critical('Was not able to connect to "' + self.name + '" socket, closing app')
                        break
                    raise serr

        listenerConnection.shutdown(2)
        listener.shutdown(2)

        listenerConnection.close()
        listener.close()
        logger.warning('Client Side Listener Thread "'+self.name+'" Stopped')
        
        self.stop()

    def stop(self):
        self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()

    self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()

