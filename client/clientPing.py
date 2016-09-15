import threading
import logging
import socket
from select import select
import datetime
import calendar
import time
import struct
from marsClientException import MarsClientException
import errno
from socket import error as socket_error

logger = logging.getLogger('mars_logging')

PING_RATE = .5
SOCKET_TIMEOUT = 5
FLOAT_PACKER = struct.Struct('f')

class PingThread(threading.Thread):
    def __init__(self, serverAddr, port):
        super(PingThread, self).__init__()
        self._stop = threading.Event()
        self.serverAddr = serverAddr
        self.port = port
    
    def run(self):
        logger.debug('Launching client ping thread on port ' + str(self.port))
        sock = socket.create_connection((self.serverAddr, self.port))

        clientException = None

        while self.stopped() == False:
            try:
                readyState = select([],[sock,],[], SOCKET_TIMEOUT)
                if readyState[1]:
                    datetime = self.microtime()
                    print 'sending timeof ', datetime
                    sock.sendall(FLOAT_PACKER.pack(datetime))
                else:
                    print 'Client could not ping server'
                    self.stop()
                time.sleep(PING_RATE)
            except socket_error as serr:
                if serr.errno == errno.ECONNREFUSED or serr.errno == errno.EPIPE:
                    logger.critical('Was not able to connect to Ping socket, closing app')
                    clientException = MarsClientException('Was not able to connect to socket ' + str(self.port))
                    break
                raise serr

        sock.close()
        logger.debug('Ping thread stopped')
        self.stop()

    def microtime(self):
        unixtime = datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
        return unixtime.days*24*60*60 + unixtime.seconds + unixtime.microseconds/1000000.0

    def stop(self):
        self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()

