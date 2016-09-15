import time
import threading
import sys
from select import select
import logging, logging.handlers
from listener import ListenerThread
from fileForwarder import FileRelay
from select import error
from Queue import Empty

DEBUG_LOG_PORT     = 1338
TELEMETRY_LOG_PORT = 1339
FILE_FORWARD_PORT  = 1340
#timeout in seconds for which we think mars exploded or stopped working
#for reference: mars updates every .4-.5 seconds
MARS_TIMEOUT = 2

class SocketManager(threading.Thread):
    '''
    Responsible for turning sockets off when connection is
    lossed, then re-enabling them when socket connection is
    re-established

    Explicit: When mars dies, so does this thread
              When client dies, this thread lives until mars dies
              There is no stop() here on purpose for the above conditions
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
        '''
        Launches the fileForwarding thread.
        Kills zombie thread if present
        while true
            Verifies that the listener (client communication) is connected
                if stopped: start zombiethread to keep mars alive
                if not: verify mars is alive
        close listener
        close fileforwarder
        remove socket connections from logging instances
        '''
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
                self.zombieThread = ZombieThread(self.connectionQueue, self.onlineQueue)
                self.zombieThread.start() 
                break
            #check that mars is still running
            try:
                if self.onlineQueue.get(timeout=MARS_TIMEOUT) == 0:
                    print 'Mars has stopped running'
                    break
            except Empty:
                print 'Mars has stopped running unexpectedly'
                break
            time.sleep(.03)
        #stop all threads on given client
        if not self.listener.stopped():
            self.listener.stop()
        self.listener.join()
        self.fileRelay.stop()
        self.fileRelay.join()
        print 'All sockets have been disconnected...'
        #remove previous socketHandlers
        self.debugLog.handlers = [h for h in self.debugLog.handlers if not isinstance(h, logging.handlers.SocketHandler)]
        self.telemetryLog.handlers = [h for h in self.telemetryLog.handlers if not isinstance(h, logging.handlers.SocketHandler)]
        print 'No longer logging to given socket'
  
    def wireLogToPort(self, name, client, port):
        '''
        Attaches a sockethandler to logger with name of name
        and logs to a given client on a prespecified port
        '''
        logger = logging.getLogger(name)
        socketHandler = logging.handlers.SocketHandler(client, port)
        logger.addHandler(socketHandler)
        logger.debug('complete handshake')
        return logger

    def joinZombie(self):
        if self.zombieThread is not None:
            self.zombieThread.stop()
            self.zombieThread.join()
            self.zombieThread = None

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
        '''
        Continuously sends -1 to mars to tell it that there is no client
        If nothing is received from mars in a given timeout time, we assume
        mars is dead and kill connection 
        '''
        while self.stopped() is False:
            self.connectionQueue.put(-1)
            #check that mars is still running
            try:
                if self.onlineQueue.get(timeout=MARS_TIMEOUT) == 0:
                    print 'Mars has stopped running'
                    break
            except Empty:
                print 'Mars has stopped running unexpectedly'
                break
            time.sleep(.03)

    def stop(self):
        self._stop.set()
    
    def stopped(self):
        return self._stop.isSet()

