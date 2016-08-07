import threading
import struct
import pickle
import logging
from threading import Thread
import socket
import logging
from select import select

logger = logging.getLogger('mars_logging')

class ListenerThread(threading.Thread):
    def __init__(self, q, serverAddr, port, name = 'Thread', displayInConsole = True):
        super(ListenerThread, self).__init__()
        self._stop = threading.Event()
        self.q = q
        self.serverAddr = serverAddr
        self.port = port
        self.name = name
        self.displayInConsole = displayInConsole
        self.socketTimeout = 3
    
    def run(self):
        logger.debug('Client side Listener Thread "'+self.name+'" waiting for connection...')
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.serverAddr != 'localhost':
            listener.bind(('', self.port))
        else:
            listener.bind(('localhost', self.port))
        listener.listen(1)

        listenerConnection, address = listener.accept()
        listenerConnection.setblocking(0)
        listenerConnection.settimeout(self.socketTimeout)

        logger.debug('Client side Listener Thread "'+self.name+'" connected!')
        while self.stopped() is False:
            isReady = select([listenerConnection],[],[],self.socketTimeout)
            if isReady[0]:
                chunk = listenerConnection.recv(4)
                if len(chunk) < 4:
                    break
                slen = struct.unpack('>L', chunk)[0]
                chunk = listenerConnection.recv(slen)
                while len(chunk) < slen:
                    chunk = chunk + listenerConnection.recv(slen - len(chunk))
                obj = pickle.loads(chunk)
                record = logging.makeLogRecord(obj)

                if self.q is not None:
                    self.q.put(record)
                if self.displayInConsole:
                    logger.log(record.levelno, record.msg + ' (' + record.filename + ':' + str(record.lineno) + ')')

        listenerConnection.close()
        listener.close()
        logger.debug('Client Side Listener Thread "'+self.name+'" Stopped')

    def stop(self):
        self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()

