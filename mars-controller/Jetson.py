'''
ark9719
6/17/2016
'''

from CodeInput import ConcreteLEDInput, ConcreteStreamInput, ConcreteMotorInput, ConcreteSystemInput
from GpioPin import GpioPin
from Watchdog import Watchdog
from Threads import InputThread, StatisticsThread
from Valmar import Valmar
from GraphUtility import GraphUtility
import logging
import csv
import sys
import time
import json
import subprocess
import base64

class Jetson(object):
    """
    Jetson controls input from the controller, and manages the data sent back from the
    arduino/mars
    """

    def __init__(self, devices, config, timestamp, q = None):

        self._devices = devices
        self.initDevices()
        self.initThreads()

        self._pinHash = self.initPins()
        self.initCommands()

        self._timestamp = timestamp
        self._config = config
        self._header = False
        self._q = q
        self.graphUtil = GraphUtility(config)

    def initDevices(self):
        self._arduino = self._devices['Arduino']
        self._stream = self._devices['Stream']
        self._mars = self._devices['Mars']
        self._motor = self._devices['Motor']
        self._motor._arduino = self._arduino
        self._led = self._devices['LED']
        self._led._arduino = self._arduino
        self._watchdog = self._devices['WatchDog']
        self._valmar = self._devices['Valmar']

    def initPins(self):
        """
        Create 8 pin objects
        """

        pinHash = {'resetArduino': GpioPin(166),
                    'connectionLED': GpioPin(163),
                    'warningLED': GpioPin(164),
                    'batteryLED': GpioPin(165),
                    'motorRelay': GpioPin(57),
                    'ledRelay': GpioPin(160),
                    'laserRelay': GpioPin(161),
                    'relay4': GpioPin(162)
                 }

        return pinHash

    def initCommands(self):
        self._sysCommands = {'system shutdown': self.systemShutdown,
                                'system restart': self.systemRestart,
                                'recall': self._watchdog.recall,
                                'stream open': self._stream.open,
                                'stream close': self._stream.close,
                                'reset arduino': self.resetArduino,
                                'motors off': self._pinHash['motorRelay'].toggleOn ,
                                'lasers off': self._pinHash['laserRelay'].toggleOn,
                                'led off': self._pinHash['ledRelay'].toggleOn,
                                'start statistics': self._statsT.start,
                                'hibernate': self.hibernate,
                                'start': self.start,
                                'exit': self.exit,
                                'list logs': self.listLogs
                             }


    def safeInput(self):
        """
        Continuesly scans for controller input first identifying the type of command then checking validity
        before writing to the arduino and storing the last command.
        :return:
        """

        #Prompt for input
        if self._q is None:
            controlCode = raw_input("LED, motion, stream, or control code: \n")
        else:
            controlCode = self._q.get()
        myCodeInput = self.recieveInput(controlCode)



    def recieveInput(self, controlCode):
        """
        Decipher the type of input. Motor, LED, Stream or System
        :param controlCode:
        :return: Return specialized command object
        """
        print("Control code: " + controlCode)

        if controlCode in self._motor._motorCodes:
            return self._motor.issue(controlCode, self._arduino)
        elif "forward" in controlCode or "backward" in controlCode or "brake" in controlCode:
            return self._motor.movement(controlCode)
        elif "brightness" in controlCode:
            return self._led.issue(self._arduino, controlCode)
        elif controlCode in self._stream._streamCodes:
            return self._stream.issue(controlCode)
        elif controlCode in self._sysCommands:
            self._sysCommands[controlCode]()
        elif 'graph' in controlCode:
            self.graph(controlCode)
        else:
            return logging.info("Invalid control code. Check documentation for command syntax.")



    def statisticsController(self):
        """
        The loop for gathering, displaying, and saving data.
        :return:
        """

        logging.debug("Generating Statistics...")
        statistics = self._mars.generateStatistics()

        #inject statistics updates
        statistics.update(self._valmar.updateTelemetry())
        statistics.update(self._watchdog.watch(statistics))
        logging.debug("Displaying Statistics...")
        logging.info(self.displayStatistics(self._mars._statistics))
        logging.debug("Saving statistics...")
        self.saveStats(self._mars._statistics)

        #Set the integ time to the time of the last read for calculations
        self._mars._integTime = time.time()


    def displayStatistics(self, data):
        """
        Takes the data created by Mars and prints it, human readable.
        :param data:
        :return:
        """
        return json.dumps(data) 


    def saveStats(self, data):
        """
        This is the method in control of saving data generated by Mars onto the harddisk.
        :param data:
        :return:
        """
        #If the header to the file isn't written, write it.
        if (not self._header ):
            fileName = self._config.logging.output_path + '/output/' + self._config.logging.log_name + '-' + self._timestamp + '/' + self._config.logging.log_name + '_machine_log.csv'
            with open(fileName, 'a') as rawFile:
                rawWriter = csv.DictWriter(rawFile, data.keys())
                rawWriter.writeheader()
            self._header = True

        try:
            fileName = self._config.logging.output_path + '/output/' + self._config.logging.log_name + '-' + self._timestamp + '/' + self._config.logging.log_name + '_machine_log.csv'
            with open(fileName, 'a') as rawFile:
                rawWriter = csv.DictWriter(rawFile, data.keys())
                rawWriter.writerow(data)

        except Exception as e:
            logging.info("unable to log data because: \r\n {}".format(e))

    def initThreads(self):
        self._inputT = InputThread(self)
        self._statsT = StatisticsThread(self)

    def manageThreads(self, toggle):
            """
            This method starts the two threads that will run for the duration of the program. One scanning for input,
            the other generating, displaying, and saving data.
            :return:
            """

            if (toggle == 'start'):
                logging.info("Attempting to start threads")

                try:

                    self._inputT.start()
                    self._statsT.start()
                except Exception as e:
                    logging.WARNING("error starting threads ({})".format(e))
                    logging.WARNING("program will terminate")
                    sys.exit()
            elif (toggle == 'stop'):
                logging.info("Attempting to stop threads")

                try:
                    self._inputT.stop()
                    self._statsT.stop()
                except Exception as e:
                    logging.WARNING("error stopping threads ({})".format(e))
                    logging.WARNING("program will terminate")
                    sys.exit()


    def systemRestart(self):
        logging.info("initiating safe restart")
        logging.info("shutting down arduino")
        self._arduino.powerOff()
        ### add functionality to cut power to motor controller
        logging.info("restarting this computer")
        logging.info("this connection will be lost")
        time.sleep(1)
        subprocess.call(['sudo reboot'], shell=True)


    def systemShutdown(self):
        logging.info("initiating safe shutdown")
        ### add functionality to cut power to motor controller
        logging.info("shutting downn this computer")
        logging.info("this connection will be lost")
        subprocess.call(['sudo poweroff'], shell=True)

    def start(self):
        self._pinHash['motorRelay'].changeState(0)
        logging.info("Motor relay started")
        self._pinHash['ledRelay'].changeState(0)
        logging.info("LED relay started")
        self._pinHash['laserRelay'].changeState(0)
        logging.info("Laser relay started")

        logging.info("Starting motor...")
        self._motor.start()

        logging.info("Starting stream...")
        self._stream.open()

        logging.info("Starting threads...")
        self.manageThreads('start')

    def manual(self):
        self._inputT.start()

    def exit(self):

        logging.info("Stopping threads")
        self.manageThreads('stop')

        logging.info("Braking motor...")
        self._motor.brake()

        logging.info("Closing stream...")
        self._sysCommands['stream close']()

        logging.info(("Turning off LEDs..."))
        self._led.issue(self._arduino, "brightness 0")

        self._pinHash['motorRelay'].changeState(1)
        logging.info("Motor relay stopped")
        self._pinHash['ledRelay'].changeState(1)
        logging.info("LED relay stopped")
        self._pinHash['laserRelay'].changeState(1)
        logging.info("Laser relay stopped")

        self.manageThreads('stop')

        sys.exit()


    def hibernate(self):
        self._pinHash['motorRelay'].changeState(1)
        logging.info("Motor relay ended")
        self._pinHash['ledRelay'].changeState(1)
        logging.info("LED relay ended")
        self._pinHash['laserRelay'].changeState(1)
        logging.info("Laser relay ended")
        self._stream.close()

    def turnOnComponent(self,indentifier):
        self._pinHash[indentifier].changeState(0) #inverted Logic: 0 --> On

    def turnOffComponent(self,indentifier):
        self._pinHash[indentifier].changeState(1) #inverted Logic: 1 --> Off

    def resetArduino(self):
        self.turnOffComponent("resetArduino")
        time.sleep(.2)
        self.turnOnComponent("resetArduino")

    def graph(self, graphCommand):
        #This is kinda hacky, but we want to keep mars independant of the server
        #usually we would want to initiate a tcp-ip stream and send our pdf over
        #packets. To do this we would need to have mars have some 'knowledge' of 
        #the server. As I said, that's not preferred.

        #My solution is to base64 encode the file, and send it via the logging
        #this simplifies the entire process, and keeps us from coupling
        graphCommand = graphCommand.split(' ')
        if len(graphCommand) > 1:
            self.graphUtil.generate_pdf(graphCommand[1])
        else:
            self.graphUtil.generate_pdf()
        self.logFile('telemetry_graphs.pdf')

    #Sends with structure: magic namelength delimiter name filedata
    #magicheader: <<<_file_record_>>>
    #namelength: integer
    #delimiter: _
    #filedata: the local file read in as base64
    def logFile(self, fileIn):    
        with open(fileIn, 'rb') as f:
            nameLength = str(len(fileIn))
            logging.info('<<<_file_record_>>>' + nameLength + '_' + fileIn + base64.b64encode(f.read()))

    def listLogs(self):
        logging.info(self.graphUtil.get_all_outputs())
 
