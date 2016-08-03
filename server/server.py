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
server_address = ('', marsPort)
sock.bind(server_address)
sock.listen(1)
q = Queue()

def wireLogToPort(name, client, port):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    socketHandler = logging.handlers.SocketHandler(client, port)
    logger.addHandler(socketHandler)
    logger.debug('complete handshake')
    return logger

try:
    while True:
        print >>sys.stderr, 'Server launched on socket 1337; waiting for client...'
        connection, client_address = sock.accept()
        try:
            client_ip, client_port = client_address
            print >>sys.stderr, 'connection from', client_ip
            log = wireLogToPort('mars_logging', client_ip, debugLog)
            wireLogToPort('telemetry_logging', client_ip, telemLog)
            data = connection.recv(4096)
            print >>sys.stderr, 'received "%s"' % data
            if data is not None:
                if validate_json(data):
                    log.info('Data verified as valid config, starting up Mars!')
                    thread = ListenerThread(q, connection)
                    thread.start()
                    #all output from mars gets pipped to the rootLogger
                    #all input from connection is received through the listender, and piped through a queue to mars
                    Mars.run(data, q, True)
                    #if we are here then mars' exit command was called
                    print 'Closing connection with ', client_address, ' and stopping all communication'
                    thread.stop()
                    connection.close()
        finally:
            connection.close()
except KeyboardInterrupt:
    sock.close()
finally:
    sock.close()

