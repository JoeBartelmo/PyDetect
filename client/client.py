import socket
import sys
import time
from listener import ListenerThread
from Queue import Queue

marsPort = 1337
logPort = 1338

killCommand = 'exit'

##
## Create TCP/IP sockets, order specified cannot be changed.
##

#socket that receives data from server
telemetry = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
telemetry.bind(('localhost', logPort))
telemetry.listen(1)

#socket that will send data to the server
sock = socket.create_connection(('localhost', marsPort))

#accepts receiving socket
telemetryConnection, server_address = telemetry.accept()

#Queues responsible for communicating between GUI and this socket client
guiInput = Queue()
guiOutput = Queue()


try:    
    # Send configuration data
    with open('config.json', 'r') as content_file:
        message = content_file.read().replace('\n','').replace(' ', '')
    sock.sendall(message)
    #launch thread that continuouly receieves data from server
    thread = ListenerThread(None, telemetryConnection)
    thread.start()
    while True:
        command = raw_input()
        sock.sendall(command)
        if command == killCommand:
            time.sleep(5)#lets all messages be displayed from listener
            sock.close()
            thread.stop()
            telemetryConnection.close()
            break
    
except KeyboardInterrupt:
    print 'closing socket'
    sock.close()

