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

logger = logging.getLogger('mars_logging')

PING_RATE = .5
SOCKET_TIMEOUT = 5
FLOAT_PACKER = struct.Struct('f')

class SenderThread(threading.Thread):
    '''
    This thread is responsible for updating mars every PING_RATE seconds with
    client datetime for server connection verification. In addition, it is responsible
    for sending the commands from the client Queue
    '''
    def __init__(self, serverAddr, port, commandQueue, connection):
        super(SenderThread, self).__init__()
        self._stop = threading.Event()
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
        logger.debug('Launching client ping thread on port ' + str(self.port))
        sock = socket.create_connection((self.serverAddr, self.port))

        while self.stopped() == False:
            try:
                readyState = select([],[sock,],[], SOCKET_TIMEOUT)
                if readyState[1]:
                    datetime = self.microtime()
                    sock.sendall(FLOAT_PACKER.pack(datetime))
                else:
                    print 'Client could not ping server'
                    self.stop()
                time.sleep(PING_RATE)
            except socket_error as serr:
                if serr.errno == errno.ECONNREFUSED or serr.errno == errno.EPIPE:
                    logger.critical('Was not able to connect to Ping socket, closing app')
                    break
                raise serr

            if not self.commandQueue.empty():
                command = self.commandQueue.get()
                logger.info('Sending Command "' + command  + '" to the server')
                self.connection.sendall(command)

        sock.close()
        logger.debug('Sender thread stopped')
        self.stop()

    def microtime(self):
        unixtime = datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
        return unixtime.days*24*60*60 + unixtime.seconds + unixtime.microseconds/1000000.0

    def stop(self):
        self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()

