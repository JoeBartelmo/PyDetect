import sys
sys.path.insert(0, '../mars-controller')
import socket
from validate import validate_json
import logging, logging.handlers
import run as Mars #note as long as __main__ is defined this will write a usage violation to the console
from Queue import Queue
from threading import Thread
from listener import ListenerThread

#Manipulatable Variables
marsPort = 1337
logPort = 1338

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', marsPort)
sock.bind(server_address)
sock.listen(1)
q = Queue()

rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)

try:
    while True:
        print >>sys.stderr, 'Server launched on socket 1337; waiting for client...'
        connection, client_address = sock.accept()
        try:
            print >>sys.stderr, 'connection from', client_address
            socketHandler = logging.handlers.SocketHandler('127.0.0.1', logPort)
            rootLogger.addHandler(socketHandler)
            logging.info('handshake complete')
            data = connection.recv(4096)
            print >>sys.stderr, 'received "%s"' % data
            if data is not None:
                if validate_json(data):
                    logging.info('Data verified as valid config, starting up Mars!')
                    thread = ListenerThread(q, connection)
                    thread.start()
                    #all output from mars gets pipped to the rootLogger
                    #all input from connection is received through the listender, and piped through a queue to mars
                    Mars.run(data, q)
                    #if we are here then mars' exit command was called
                    print 'Closing connection with ', client_address, ' and stopping all communication'
                    thread.stop()
                    connection.close()
        finally:
            connection.close()
finally:
    sock.close()

