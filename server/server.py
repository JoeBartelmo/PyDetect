import sys
sys.path.insert(0, '../mars')
import socket
from validate import validate_json
import logging, logging.handlers
import run as Mars #note as long as __main__ is defined this will write a usage violation to the console
from Queue import Queue
from threading import Thread
from listener import ListenerThread

#Manipulatable Variables
marsPort = 1337
debugLog = 1338
telemLog = 1339


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('127.0.0.1', marsPort)
sock.bind(server_address)
sock.listen(1)
q = Queue()

def wireLogToPort(name, port):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    socketHandler = logging.handlers.SocketHandler('127.0.0.1', port)
    logger.addHandler(socketHandler)
    logger.info('complete handshake')
    return logger

try:
    while True:
        print >>sys.stderr, 'Server launched on socket 1337; waiting for client...'
        connection, client_address = sock.accept()
        try:
            print >>sys.stderr, 'connection from', client_address
            log = wireLogToPort('mars_logging', debugLog)
            wireLogToPort('telemetry_logging', telemLog)
            data = connection.recv(4096)
            print >>sys.stderr, 'received "%s"' % data
            if data is not None:
                if validate_json(data):
                    log.info('Data verified as valid config, starting up Mars!')
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

