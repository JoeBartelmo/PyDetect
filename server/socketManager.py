import time
import threading
import sys
from select import select
import logging, logging.handlers
from listener import ListenerThread
from fileForwarder import FileRelay
from select import error

DEBUG_LOG_PORT     = 1338
TELEMETRY_LOG_PORT = 1339
FILE_FORWARD_PORT  = 1340

class SocketManager(threading.Thread):
    '''
    Responsible for turning sockets off when connection is
    lossed, then re-enabling them when socket connection is
    re-established
    '''
    def __init__(self, q, connectionQueue, onlineQueue, client_ip, connection, listener):
        super(SocketManager, self).__init__()
        self.q = q
        self.client_ip = client_ip
        self.connection = connection
        self.connectionQueue = connectionQueue
        self.onlineQueue = onlineQueue
        self.zombieThread = None
        self.debugLog = self.wireLogToPort('mars_logging', self.client_ip, DEBUG_LOG_PORT)
        self.telemetryLog = self.wireLogToPort('telemetry_logging', self.client_ip, TELEMETRY_LOG_PORT)
        self.fileRelay = FileRelay(self.client_ip, FILE_FORWARD_PORT)
        self.listener = listener

    def run(self):
        self.fileRelay.start()

        if self.zombieThread is not None:
            self.zombieThread.stop()
            self.zombieThread.join()
            self.zombieThread = None

        time.sleep(5)
        while True:
            #check client still connected
            if self.listener.stopped():
                print 'Client has lossed Connection'
                self.zombieThread = ZombieThread(connectionQueue)
                self.zombieThread.start() 
            #check that mars is still running
            if self.onlineQueue.get(timeout=2) == 0:
                print 'Mars has stopped running'
                break
            time.sleep(.03)
        #stop all threads on given client
        if not self.listener.stopped():
            self.listener.stop()
        self.fileRelay.stop()
        print 'All sockets have been disconnected...'
        #remove previous socketHandlers
        self.debugLog.handlers = [h for h in self.debugLog.handlers if not isinstance(h, logging.handlers.SocketHandler)]
        self.telemetryLog.handlers = [h for h in self.telemetryLog.handlers if not isinstance(h, logging.handlers.SocketHandler)]
        print 'No longer logging to given socket'
  
    def wireLogToPort(self, name, client, port):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        socketHandler = logging.handlers.SocketHandler(client, port)
        logger.addHandler(socketHandler)
        logger.debug('complete handshake')
        return logger

class ZombieThread(threading.Thread):
    '''
    Launched when client connection dies to tell mars that there's no connection
    '''
    def __init__(self, connectionQueue, onlineQueue):
        super(ZombieThread, self).__init__()
        self._stop = threading.Event()
        self.connectionQueue = connectionQueue
        self.onlineQueue = onlineQueue

    def run(self):
        while self.stopped() is False:
            self.connectionQueue.put(0)
            #check that mars is still running
            if self.onlineQueue.get(timeout=5) == 0:
                print 'Mars has stopped running'
                break;
            time.sleep(.03)

    def stop(self):
        self._stop.set()
    
    def stopped(self):
        return self._stop.isSet()

