import threading
import time
import os
import socket
import logging
import struct
import base64

logger = logging.getLogger('mars_logging')
directoryToScan = '../mars/files/'

class FileRelay(threading.Thread):
    def __init__(self, serverAddr, port):
        super(FileRelay, self).__init__()
        self._stop = threading.Event()
        self._socket = socket.create_connection((serverAddr, port))

    def run(self):
        while self.stopped() is False:
            filesToSend = os.listdir(directoryToScan)
            filesToSend.remove('.gitignore')#we need gitignore to commit this folder >.>
            if len(filesToSend) > 0:
                for filename in filesToSend:
                    with open(directoryToScan + filename, 'rb') as f:
                        fileInBytes = f.read()
                    logger.info('Sending file ' + filename + ' to the client')
                    
                    intPacker = struct.Struct('I')
                    
                    value = (len(filename),)
                    self._socket.sendall(intPacker.pack(*value))
                    self._socket.sendall(filename)
                    
                    base64File = base64.b64encode(fileInBytes)
                    value = (len(base64File), )
                    self._socket.sendall(intPacker.pack(*value))
                    self._socket.sendall(base64File)

                    os.remove(directoryToScan + filename)

            time.sleep(3)
        self._socket.shutdown(2)
        self._socket.close()
        logger.info('File Relay Thread stopped')

    def stop(self):
        self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()

