'''
ark9719
6/17/2016
'''

from GpioPin import GpioPin
from Watchdog import Watchdog
from Threads import StatisticsThread
from Valmar import Valmar
from GraphUtility import GraphUtility
import logging
import csv
import sys
import time
import json
import subprocess
import base64

logger = logging.getLogger('mars_logging')
telemetryLogger = logging.getLogger('telemetry_logging')

class Jetson(object):
    """
    Jetson controls input from the controller, and manages the data sent back from the
    arduino/mars
    """

    def __init__(self, devices, config, timestamp, q = None):
        self._devices = devices

        self._pinHash = self.initPins()
        self._devices['Watchdog'] = Watchdog(config, self._devices['Arduino'], self._devices['Mars'], self._pinHash)
        self.initDevices()
        self._statsT = StatisticsThread(self)
        self.initCommands()

        self._exit = False
        self._timestamp = timestamp
        self._config = config
        self._header = False
        self._q = q
        self.graphUtil = GraphUtility(config)

    def initDevices(self):
        """
        Make every device in the device hash accessible via Jetson
        :return:
        """
        self._arduino = self._devices['Arduino']
        self._stream = self._devices['Stream']
        self._mars = self._devices['Mars']
        self._motor = self._devices['Motor']
        self._motor._arduino = self._arduino
        self._led = self._devices['LED']
        self._led._arduino = self._arduino
        self._watchdog = self._devices['Watchdog']
        self._valmar = self._devices['Valmar']

    def initPins(self):
        """
        Create 8 pin objects
        """
        pinHash = { 'connectionLED': GpioPin(166),
                    'warningLED': GpioPin(164),
                    'batteryLED': GpioPin(165),
                    'motorRelay': GpioPin(163),
                    'ledRelay': GpioPin(162),
                    'laserRelay': GpioPin(161),
                    'relay4': GpioPin(160)
                 }

        return pinHash

    def initCommands(self):
        """
        Initialize a list of valid system commands
        :return:
        """
        self._sysCommands = {'system shutdown': self.systemShutdown,
                                'system restart': self.systemRestart,
                                'recall': self._watchdog.recall,
                                'stream open': self._stream.open,
                                'stream close': self._stream.close,
                                'reset arduino': self._arduino.resetArduino,
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
        
        return controlCode

    def recieveInput(self, controlCode):
        """
        Decipher the type of input. Motor, LED, Stream or System
        :param controlCode:
        :return: Return specialized command object
        """
        logger.info("Control code: " + controlCode)

        if controlCode in self._motor._motorCodes:
            return self._motor.issue(controlCode, self._arduino)
        elif "forward" in controlCode or "backward" in controlCode or "brake" in controlCode:
            print 'motor operand'
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
            return logger.warning("Invalid control code. Check documentation for command syntax.")

    def inputLoop(self):
        """
        Runs a loop over the safeInput function, checks self._exit to determine
        whether or not it should hop out of the loop
        """
        while self._exit == False:
            self.safeInput()

    def statisticsController(self):
        """
        The controller for generating(Reading) data, checking it for errors and saving it.
        :return:
        """

        statistics = self._mars.generateStatistics()

        if statistics is not None:
            #inject statistics updates
            statistics.update(self._valmar.updateTelemetry())
            statistics.update(self._watchdog.watch(statistics))
            telemetryLogger.info(self.displayStatistics(self._mars._statistics))
            self.saveStats(self._mars._statistics)

            #Set the integ time to the time of the last read for calculations
            self._mars._integTime = time.time()
        else:
            i = 0
            while self._arduino._init is False and i < 5:
                time.sleep(5)
                i += 1


    def displayStatistics(self, data):
        """
        Transforms the data into a more readable output for logger
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
        self._filename = self._config.logging.output_path + '/output/' + self._config.user_input.log_name + '-' + self._timestamp + '/' + self._config.user_input.log_name + '_machine_log.csv'
        #If the header to the file isn't written, write it.
        try:
            with open(self._filename, 'a') as rawFile:
                #If the header to the file isn't written, write it.
                if (not self._header):
                    rawWriter = csv.DictWriter(rawFile, data.keys())
                    rawWriter.writeheader()
                    self._header = True

                rawWriter = csv.DictWriter(rawFile, data.keys())
                rawWriter.writerow(data)

        except Exception as e:
            logger.warning("unable to log data because: \r\n {}".format(e))

    def manageThreads(self, toggle):
            """
            This method manages the two threads that will run for the duration of the program. One scanning for input,
            the other generating, displaying, and saving data.
            :return:
            """
            if (toggle == 'start'):
                logger.info("Attempting to start threads")

                try:
                    self._statsT.start()
                except Exception as e:
                    logger.error("error starting threads ({})".format(e))
            elif (toggle == 'stop'):
                logger.info("Attempting to stop threads")

                try:
                    self._statsT.stop()
                except Exception as e:
                    logger.error("error stopping threads ({})".format(e))


    def systemRestart(self):
        """
        Restart the entire system, arduino included
        :return:
        """
        logger.warning("initiating safe restart")
        logger.warning ("shutting down arduino")
        self._arduino.powerOff()
        ### add functionality to cut power to motor controller
        logger.warning("restarting this computer")
        logger.warning("this connection will be lost")
        time.sleep(1)
        subprocess.call(['sudo reboot'], shell=True)


    def systemShutdown(self):
        """
        Shutdown the system
        :return:
        """
        logger.info("initiating safe shutdown")
        ### add functionality to cut power to motor controller
        logger.info("shutting downn this computer")
        logger.info("this connection will be lost")
        subprocess.call(['sudo poweroff'], shell=True)

    def start(self):
        """
        Start command for the program. Start all the relays, the motor, stream, and threads
        :return:
        """
        self._pinHash['motorRelay'].toggleOff()
        logger.info("Motor relay started")
        self._pinHash['ledRelay'].toggleOff()
        logger.info("LED relay started")
        self._pinHash['laserRelay'].toggleOff()
        logger.info("Laser relay started")

        logger.info("Starting motor...")
        self._motor.start()

        logger.info("Starting stream...")
        self._stream.open()

        logger.info("Starting threads...")
        self.manageThreads('start')
        
        logger.info('Setting up input receiver (main thread)...')
        self.inputLoop()
            
    def exit(self):
        """
        Exit command for stopping the program.
        :return:
        """
        logger.info("Stopping threads")
        self.manageThreads('stop')

        logger.info("Braking motor...")
        self._motor.brake()

        logger.info("Closing stream...")
        self._sysCommands['stream close']()

        logger.info(("Turning off LEDs..."))
        self._led.issue(self._arduino, "brightness 0")

        self._pinHash['motorRelay'].toggleOff()
        logger.info("Motor Circuit turned off")
        self._pinHash['ledRelay'].toggleOff()
        logger.info("LED Circuit turned off")
        self._pinHash['laserRelay'].toggleOff()
        logger.info("Laser Circuit turned off")

        self._exit = True


    def hibernate(self):
        """
        TODO: Hibernate function for Jetson
        :return:
        """
        self._pinHash['motorRelay'].toggleOff()
        logger.info("Motor relay ended")
        self._pinHash['ledRelay'].toggleOff()
        logger.info("LED relay ended")
        self._pinHash['laserRelay'].toggleOff()
        logger.info("Laser relay ended")
        self._stream.close()


    def graph(self, graphCommand):
        #This is kinda hacky, but we want to keep mars independant of the server
        #usually we would want to initiate a tcp-ip stream and send our pdf over
        #packets. To do this we would need to have mars have some 'knowledge' of 
        #the server. As I said, that's not preferred.

        #My solution is to base64 encode the file, and send it via the logger
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
            logger.info('<<<_file_record_>>>' + nameLength + '_' + fileIn + base64.b64encode(f.read()))

    def listLogs(self):
        logger.info(self.graphUtil.get_all_outputs())
 
