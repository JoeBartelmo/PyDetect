import socket
import sys
import time
from listener import ListenerThread
from Queue import Queue
sys.path.insert(0, '../gui')
import gui

marsPort = 1337
debugLog = 1338
telemLog = 1339

killCommand = 'exit'

sys.argv.pop()

serverAddr = 'localhost'
if len(sys.argv):
    serverAddr = sys.argv[0]
print 'Using server address:', serverAddr

#Queues responsible for communicating between GUI and this socket client
guiInput = Queue()
guiOutput = Queue()

#sockets that continuously receive data from server and
#pipe to the user
telemThread = ListenerThread(None, serverAddr, telemLog, 'Telemetry Receive', displayInConsole = False)
debugThread = ListenerThread(None, serverAddr, debugLog, 'Logging Receive')

telemThread.start()
debugThread.start()

#socket that will send data to the server
sock = socket.create_connection((serverAddr, marsPort))

try:    
    # Send configuration data
    with open('config.json', 'r') as content_file:
        message = content_file.read().replace('\n','').replace(' ', '')
    sock.sendall(message)
    
    # start gui
    #gui.start(guiInput, guiOutput, server_addr)

    while True:
        command = raw_input('\n')
        sock.sendall(command)
        if command == killCommand:
            time.sleep(5)#lets all messages be displayed from listener
            sock.close()
            telemThread.stop()
            debugThread.stop()
            break
    
except KeyboardInterrupt:
    print 'closing socket'
    sock.close()

