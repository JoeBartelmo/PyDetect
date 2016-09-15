import socket
import sys
import time
from fileListener import FileListenerThread
from listener import ListenerThread
import logging
from Queue import Queue
sys.path.insert(0, '../gui')
from ColorLogger import initializeLogger 
import gui
from clientPing import PingThread
from marsClientException import MarsClientException

MARS_PORT      = 1337
DEBUG_PORT     = 1338
TELEMETRY_PORT = 1339
FILE_PORT      = 1340
PING_PORT      = 1341

MARS_KILL_COMMAND = 'exit'

sys.argv.pop(0)

#grabbing server address from arguments
serverAddr = 'localhost'
if len(sys.argv) == 1:
    serverAddr = sys.argv[0]
logger = initializeLogger('./', logging.DEBUG, 'mars_logging', sout = True, colors = True)

#Queues responsible for communicating between GUI and this socket client
guiTelemetryInput = Queue()
guiLoggingInput = Queue()
guiOutput = Queue() 

#thread responsibel for handling telemetry from mars
telemThread = ListenerThread(guiTelemetryInput, serverAddr, TELEMETRY_PORT, 'Telemetry Receive', displayInConsole = False)
#thread responsible for handling mars logging
debugThread = ListenerThread(guiLoggingInput, serverAddr, DEBUG_PORT, 'Logging Receive')
#thread responsible for handling files sent from mars
fileListenerThread = FileListenerThread(serverAddr, FILE_PORT)
#socket that will send data to the server
commandSocket = socket.create_connection((serverAddr, MARS_PORT))
#socket that will maintain ping to server
pingThread = PingThread(serverAddr, PING_PORT)
pingThread.start()
#defines whether or not we have closed threads already
closedThreads = False

def closeAllThreads():
    global closedThreads
    if closedThreads == False:
        print 'Closing ping thread...'
        pingThread.stop()
        pingThread.join()
        print 'Closing Telemetry Thread...'
        telemThread.stop()
        telemThread.join()
        print 'Closing Mars log thread...'
        debugThread.stop()
        debugThread.join()
        print 'Closing Fie Listener thread...'
        fileListenerThread.stop()
        fileListenerThread.join()
        print 'Closing command socket...'
        commandSocket.close()

try:    
    # Send configuration data
    with open('config.json', 'r') as content_file:
        message = content_file.read().replace('\n','').replace(' ', '')
    commandSocket.sendall(message)

    telemThread.start()
    debugThread.start()
    fileListenerThread.start()
    # start gui
    #gui.start(guiOutput, guiLoggingInput, guiTelemetryInput,serverAddr)
    
    while True:
        command = raw_input('\n')
        commandSocket.sendall(command)
        if command == killCommand:
            time.sleep(2)#lets all messages be displayed from listener
            break
    
except KeyboardInterrupt:
    closeAllThreads()
except MarsClientException as ex:
    closeAllThreads()
    raise ex
finally:
    closeAllThreads()
