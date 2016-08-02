import threading
import struct
import pickle
import logging
from threading import Thread
import socket
import logging
from ColorLogger import initializeLogger 
from select import select

logger = initializeLogger('./', logging.DEBUG, 'mars_logging', sout = True, colors = True)

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
        logger.debug('Clietn side Listener Thread "'+self.name+'" waiting for connection...')
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.bind((self.serverAddr, self.port))
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

                #If our record is prefixed with <<<_file_record_>>>
                #we're gonna write a file with the base64 decoded content
                if '<<<_file_record_>>>' in record.msg:
                    self.decode_file_and_write(record.msg)
                else:
                    if self.q is not None:
                        self.q.put(record)
                    if self.displayInConsole:
                        logger.log(record.levelno, record.msg + ' (' + record.filename + ':' + str(record.lineno) + ')')

        listenerConnection.close()
        listener.close()
        logger.debug('Client Side Listener Thread "'+self.name+'" Stopped')

    def decode_file_and_write(self, data):
        #remove magic
        data = data[19:]
        #name length
        delimiterOffset = data.find('_')
        nameLength = int(data[:delimiterOffset]) + 1
        #remove name length descriptor
        data = data[delimiterOffset:]
        #get filename and remove filename from data
        filename = data[:nameLength]
        data = data[nameLength:]

        with open(filename, 'wb') as f:
            f.write(data.decode('base64'))

    def stop(self):
        self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()

