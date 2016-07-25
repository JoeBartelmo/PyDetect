import threading
import sys

class ListenerThread(threading.Thread):
    def __init__(self, q, socket):
        super(ListenerThread, self).__init__()
        self._stop = threading.Event()
        self.q = q
        self.socket = socket

    def run(self):
        while self.stopped() is False:
            command = self.socket.recv(20)
            if command is not None and len(command) > 0:
                print('Received' + command)
                self.q.put(command)
        print 'Listener Thread Stopped'

    def stop(self):
        self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()

