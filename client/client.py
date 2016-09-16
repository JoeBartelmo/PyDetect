import socket
import sys
import time
from fileListener import FileListenerThread
from listener import ListenerThread
import logging
from Queue import Queue
from ColorLogger import initializeLogger 
sys.path.insert(0, '../gui')
import gui
from sender import SenderThread

#ports we use for communication between client and server
MARS_PORT      = 1337
DEBUG_PORT     = 1338
TELEMETRY_PORT = 1339
FILE_PORT      = 1340
PING_PORT      = 1341
#command to shutdown mars
MARS_KILL_COMMAND = 'exit'
#time in seconds to verify we weren't able to connect
TIME_TO_VERIFY_ESTABLISHED_CONNECTION = 4

#defines whether or not we have closed threads already
closedThreads = False
def closeAllThreads():
    '''
    Cleans up all open sockets and threads on client
    '''
    global closedThreads
    if closedThreads == False:
        if senderThread.stopped() == False:
            print 'Closing Sender thread...'
            senderThread.stop()
            senderThread.join()
        if telemThread.stopped() == False:
            print 'Closing Telemetry Thread...'
            telemThread.stop()
            telemThread.join()
        if debugThread.is_alive():
            print 'Closing Mars log thread...'
            debugThread.stop()
            debugThread.join()
        if fileListenerThread.stopped() == False:
            print 'Closing File Listener thread...'
            fileListenerThread.stop()
            fileListenerThread.join()
        print 'Closing command socket...'
        commandSocket.close()

def displayUsage(unknownObj = None):
    '''
    Prints userfriendly usage of client.py
    '''
    if unknownObj is not None:
        print('Unknown parameter, ' + str(unknownObj) + '\n')
    print('Incorrect arguments, please specify a json string or object with which to load configuration')
    print('\tUsage:\tclient.py [Server IP|Server Domain]')
    print('\t\t-d: Debug mode')
    print('\t\t-c: CLI (No GUI) mode')

if __name__ == '__main__':
    filename = sys.argv.pop(0)#client.py
    
    logMode = logging.INFO 
    cliMode = False    
    serverAddr = None

    #TODO: Install CLI and use that instead
    if len(sys.argv) < 1 or len(sys.argv) > 3:
        displayUsage()
        sys.exit(1)
    else:
        serverAddr = sys.argv.pop(0)
        while(len(sys.argv)):
            mode = sys.argv.pop(0)
            if mode == '-d':
                logMode = logging.DEBUG
            elif mode == '-c':
                cliMode = True
            else:
                displayUsage(mode)
                sys.exit(1)
    sys.argv.append(filename)#tkinter wants the filename to be there

    #grabbing server address from arguments
    logger = initializeLogger('./', logMode, 'mars_logging', sout = True, colors = True)
    logger.info('Using server address:' + serverAddr)

    #Queues responsible for communicating between GUI and this socket client
    guiTelemetryInput = Queue()
    guiLoggingInput = Queue()
    guiOutput = Queue()

    #thread responsibel for handling telemetry from mars
    telemThread = ListenerThread(guiTelemetryInput, serverAddr, TELEMETRY_PORT, logMode, 'Telemetry Receive', displayInConsole = False)
    #thread responsible for handling mars logging
    debugThread = ListenerThread(guiLoggingInput, serverAddr, DEBUG_PORT, logMode, 'Logging Receive')
    #thread responsible for handling files sent from mars
    fileListenerThread = FileListenerThread(serverAddr, FILE_PORT)
    #socket that will send data to the server
    commandSocket = socket.create_connection((serverAddr, MARS_PORT))
    #socket that will maintain ping to server and send commands to server
    senderThread = SenderThread(serverAddr, PING_PORT, guiOutput, commandSocket)
    senderThread.start()
    try:    
        # Send configuration data
        with open('config.json', 'r') as content_file:
            message = content_file.read().replace('\n','').replace(' ', '')
        commandSocket.sendall(message)

        telemThread.start()
        debugThread.start()
        fileListenerThread.start()
       
        #Verify we have succesfully connected
        for index in range(0, TIME_TO_VERIFY_ESTABLISHED_CONNECTION):
            if telemThread.stopped() or debugThread.stopped() or fileListenerThread.stopped() \
                or senderThread.stopped():
                closeAllThreads()
                sys.exit(1)
            time.sleep(1)
     
        # start gui
        if cliMode:
            while True:
                command = raw_input('Type Your Command:')
                guiOutput.put(command)
                if command == MARS_KILL_COMMAND:
                    break 
        else:
            gui.start(guiOutput, guiLoggingInput, guiTelemetryInput, serverAddr)
        
    except KeyboardInterrupt:
        closeAllThreads()
    finally:
        closeAllThreads()
else:
    displayUsage()

