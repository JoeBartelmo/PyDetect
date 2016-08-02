import threading
import sys
from select import select

class ListenerThread(threading.Thread):
    def __init__(self, q, socket):
        super(ListenerThread, self).__init__()
        self._stop = threading.Event()
        self.q = q
        self.socketTimeout = 3#seconds
        self.socket = socket
        self.socket.setblocking(0)
        self.socket.settimeout(self.socketTimeout)

    def run(self):
        while self.stopped() is False:
            isReady = select([self.socket],[],[],self.socketTimeout)
            if isReady[0]:
                command = self.socket.recv(64)
                if command is not None and len(command) > 0:
                    print('Received: ' + command)
                    self.q.put(command)
        print 'Listener Thread Stopped'

    def stop(self):
        self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()

