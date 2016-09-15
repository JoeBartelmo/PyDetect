import sys
import socket
from validate import validate_json
from Queue import Queue
from Queue import Empty
from socketManager import SocketManager
from listener import ListenerThread
from marsHandler import MarsThread

#Manipulatable Variables
MARS_PORT = 1337
PING_PORT = 1341

#socket to receive commands from client
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('', MARS_PORT)
sock.bind(server_address)
sock.listen(1)

#Socket to maintain ping from client
pingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('', PING_PORT)
pingSocket.bind(server_address)
pingSocket.listen(1)

#this is the queue used for the client to communicate to the server,
#which pipes data to mars
commandQueue = Queue()
#this is the queue that notifies mars that the client is connected
connectionQueue = Queue()
#this is the queue that mars uses to notify the server that it's online
onlineQueue = Queue()

def startMars(configuration): 
    handler = MarsThread(configuration, commandQueue, connectionQueue, onlineQueue, True)
    handler.start()

try:
    while True:
        print >>sys.stderr, 'Server launched on socket 1337; waiting for client...'
        connection, client_address = sock.accept()
        pingConnection, client_ip = pingSocket.accept()

        client_ip, client_port = client_address
        print >>sys.stderr, 'connection from', client_ip
        
        #no matter what The client will always send a json config data
        data = connection.recv(4096)
        print >>sys.stderr, 'received "%s"' % data

        listener = ListenerThread(commandQueue, connectionQueue, connection, pingConnection)
        listener.start()
        
        if data is not None:
            if validate_json(data):
                client = SocketManager(commandQueue, connectionQueue, onlineQueue, client_ip, connection, listener) 
                client.start()
                try:
                    online = onlineQueue.get(timeout=2)
                    if online == 0:
                        startMars(data)
                except Empty:
                    startMars(data)
except KeyboardInterrupt:
    sock.close()
finally:
    sock.close()
