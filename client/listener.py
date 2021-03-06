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
from constants import *
from socket import error as socket_error
import errno

logger = logging.getLogger('mars_logging')

class ListenerThread(threading.Thread):
    '''
    Thread is responsible for receiving data from the server. 
    The data is transmitted using the logging module in python,
    this handles deserialization of the logging object and pipes
    the data into a queue for the GUI to read.
    '''
    def __init__(self, queueArr, serverAddr, port, logLevel, name = 'Thread', displayInConsole = True):
        super(ListenerThread, self).__init__()
        self._stop = threading.Event()
        self.qArr = queueArr
        self._init = threading.Event()
        self.serverAddr = serverAddr
        self.port = port
        self.name = name
        self.displayInConsole = displayInConsole
        self.logLevel = logLevel
        #ideally we want to stop repeat logs on mars side, but for short term
        #this will make client more responsive
        self.lastLogEntry = ""
        
    
    def run(self):
        logger.debug('Client side Listener Thread "'+self.name+'" waiting for connection...')
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self.serverAddr != 'localhost' and self.serverAddr != '127.0.0.1':
            listener.bind(('', self.port))
        else:
            listener.bind(('localhost', self.port))
        listener.listen(1)
        
        socketReady = select([listener], [], [], SOCKET_TIMEOUT)
        if socketReady[0]:
            listenerConnection, address = listener.accept()
            listenerConnection.setblocking(0)
            listenerConnection.settimeout(SOCKET_TIMEOUT)
            self._init.set()
            logger.warning('Client side Listener Thread "'+self.name+'" connected!')
        else:
            self.stop()
            listenerConnection = None

        while self.stopped() != True:
            isReady = select([listenerConnection],[],[],SOCKET_TIMEOUT)
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
                        if self.qArr is not None and record.msg not in self.lastLogEntry:
                            if isinstance(self.qArr, list):
                                for q in self.qArr:
                                    q.put(record)
                            else:
                                self.qArr.put(record)
                            self.lastLogEntry = record.msg
                        if self.displayInConsole:
                            logger.log(record.levelno, record.msg + ' (' + record.filename + ':' + str(record.lineno) + ')')
                except socket_error as serr:
                    if serr.errno == errno.ECONNREFUSED or serr.errno == errno.EPIPE:
                        logger.critical('Was not able to connect to "' + self.name + '" socket, closing app')
                        break
                    raise serr

        if listenerConnection is not None:
            listenerConnection.shutdown(2)
            listenerConnection.close()
        
        listener.shutdown(2)
        listener.close()

        logger.warning('Client Side Listener Thread "'+self.name+'" Stopped')
        
        self.stop()

    def isInit(self):
        return self._init.isSet()

    def stop(self):
        self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()

