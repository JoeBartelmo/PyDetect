import threading
import logging
import socket
from select import select
import datetime
import calendar
import time
import struct

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
        logger.debug('Launching client ping thread...')
        sock = socket.create_connection((self.serverAddr, self.port))
        sock.settimeout(SOCKET_TIMEOUT)

        while not self.stopped():
            readyState = select([],[sock,],[], SOCKET_TIMEOUT)
            if readyState[1]:
                datetime = self.microtime()
                print 'sending timeof ', datetime
                sock.sendall(FLOAT_PACKER.pack(datetime))
            else:
                print 'Client could not ping server'
                self.stop()
            time.sleep(PING_RATE)

        sock.close()
        logger.debug('Ping thread stopped')

    def microtime(self):
        unixtime = datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
        return unixtime.days*24*60*60 + unixtime.seconds + unixtime.microseconds/1000000.0

    def stop(self):
        self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()

