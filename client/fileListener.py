import threading
import struct
import pickle
import logging
from threading import Thread
import socket
import logging
from ColorLogger import initializeLogger 
from select import select
import struct
import errno
from marsClientException import MarsClientException
from socket import error as socket_error

logger = logging.getLogger('mars_logging') 

class FileListenerThread(threading.Thread):
    def __init__(self, serverAddr, port):
        super(FileListenerThread, self).__init__()
        self._stop = threading.Event()
        self.serverAddr = serverAddr
        self.port = port
        self.socketTimeout = 3
    
    def run(self):
        logger.debug('Client side FileListener Thread waiting for connectionn...')
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

        logger.warning('Client side "File Listener" Thread connected!')
        clientException = None
        
        while self.stopped() is False:
            isReady = select([listenerConnection],[],[],self.socketTimeout)
            if isReady[0]:
                try:
                    fileNameLength = self.readIntFromSocket(listenerConnection)
                    fileName = listenerConnection.recv(fileNameLength)

                    logger.info('Downloading file [' + fileName + ']')

                    fileLength = self.readIntFromSocket(listenerConnection)
                    fileBase64Str = ''
                    while len(fileBase64Str) < fileLength:
                        bytesToRead = 64
                        if fileLength - len(fileBase64Str) < bytesToRead:
                            bytesToRead = fileLength - len(fileBase64Str)
                        fileBase64Str += listenerConnection.recv(bytesToRead)

                    with open(fileName, 'wb') as f:
                        f.write(fileBase64Str.decode('base64'))
                except socket_error as serr:
                    if serr.errno == errno.ECONNREFUSED or serr.errno == errno.EPIPE:
                        logger.critical('Was not able to connect to File Listener socket, closing app')
                        clientException = MarsClientException('Could not connect to port' + str(self.port))
                        break
                    raise serr
                    
        
        listenerConnection.shutdown(2)
        listener.shutdown(2)
        listenerConnection.close()
        listener.close()
        logger.warning('Client Side "File Listener" Thread Stopped')
        if clientException is not None:
            raise clientException
    
    def readIntFromSocket(self, listenerConnection):
        return int(struct.unpack('I', listenerConnection.recv(4))[0])
    
    def stop(self):
        self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()

