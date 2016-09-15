import threading
import sys
from select import select
import socket
import calendar
import datetime
import time
import struct

SOCKET_TIMEOUT = 0.01
MAX_TIMEOUTS = 1
FLOAT_UNPACKER = struct.Struct('f')

class ListenerThread(threading.Thread):
    '''
    Receives commands from client, notifies mars whether or not client is connected.
    q: Command queue to pipe to mars
    connectionQueue: watchdog queue 1 for connected 0 for not.
    socket: The current socket that the clietn is connected thru
    pingSocket: Socket to test client connection over
    '''
    def __init__(self, q, connectionQueue, socket, pingSocket):
        super(ListenerThread, self).__init__()
        self._stop = threading.Event()
        self.q = q
        self.connectionQueue = connectionQueue

        #configure both sockets to be non-blocking
        self.socket = socket
        self.socket.setblocking(0)
        self.socket.settimeout(SOCKET_TIMEOUT)

        self.pingSocket = pingSocket
        self.pingSocket.setblocking(0)
        self.pingSocket.settimeout(SOCKET_TIMEOUT)

    def run(self):
        timeWithoutCommand = 0 
        timeouts = 0
        currentPing = 0

        while self.stopped() == False:
            #grab manditory ping from client
            ping = select([self.pingSocket], [], [], SOCKET_TIMEOUT)
            if ping[0]:
                data = self.pingSocket.recv(FLOAT_UNPACKER.size)
                #unpackedDatetime = FLOAT_UNPACKER.unpack(data)[0]
                #I keep running into issues with actual date time >.>
                print 'Ping of ', timeouts * 2 
                currentPing = timeouts * 2 
                timeouts = 0
            elif timeouts >= MAX_TIMEOUTS:
                print 'Lossed connection to client'
                self.connectionQueue.put(-1)
                break
            else:
                timeouts += SOCKET_TIMEOUT
            self.connectionQueue.put(currentPing)

            #grab command from client if any
            hasCommand = select([self.socket], [], [], SOCKET_TIMEOUT)
            if hasCommand[0]:
                print 'receieved something !!'
                command = self.socket.recv(64)
                if command is not None and len(command) > 0:
                    print('Received: ' + command)
                    self.q.put(command)
        print 'Listener Thread Stopped'
        #close the receiving command socket
        self.socket.shutdown(2)
        self.socket.close()
        #close the ping socket
        self.pingSocket.shutdown(2)
        self.pingSocket.close()

    def stop(self):
        self._stop.set()
  
    def microtime(self):
        '''
        The client sends current posix timestamp, ideally we want to subtract that from
        current posix timestamp (both utc), but we're having issues and to complete this
        project timely i'm going to ignore for now
        -Joe
        '''
        unixtime = datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
        return unixtime.days*24*60*60 + unixtime.seconds + unixtime.microseconds/1000000.0

    def stopped(self):
        return self._stop.isSet()
