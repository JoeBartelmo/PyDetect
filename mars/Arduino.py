'''
ark9719
6/17/2016
'''
import serial
import time
import logging
import subprocess
import sys
import glob

class Arduino(object):

    def __init__(self, config):
        self._config = config
        self._init = False #False until initialized
        self._arduinoPath = glob.glob('/dev/ttyACM*')[0]

        logging.info(self._arduinoPath)
        self._timeInit = time.time()
        self._lastLED = 'None yet'
        self._lastMotor = 'None yet'


        try:
            logging.info("Attempting to connect Arduino")
            self._controller = serial.Serial(self._arduinoPath, self._config.constants.baud_rate)
            self._init = True
            logging.info('Arduino connected')
            time.sleep(.1)
        except serial.serialutil.SerialException:
            logging.info("Arduino didn't connect.")
            logging.info("arduino not connected or device path wrong")
            logging.info("check MARS user manual for details")
            logging.info("unable to continue, program will now terminate")
            sys.exit()

    def serial_readline(self):
        """
        This method manages pulling the raw data off the arduino.
        :return:
        """

        assert self._init, "Arduino has not been initialized"

        waitStart = time.time()
        waitTime = time.time() - waitStart
        timeout = self._config.constants.timeout

        while self._controller.inWaiting() == 0:
            if waitTime < timeout:
                waitTime = time.time() - waitStart
            elif waitTime >= timeout:
                logging.info("no data coming from arduino before timeout")
                logging.info("ending program, check arduino or timeout duration")
                sys.exit()
        else:

            # added short delay just in case data was in transit
            time.sleep(.001)

            # read telemetry sent by Arduino
            serialData = self._controller.readline()

            # flushing in case there was a buildup
            self._controller.flushInput()

            return serialData

    def flushBuffers(self):
        """
        Function to flush arduinos serial buffers
        :return:
        """
        assert self._init, "Arduino has not been initialized"

        self._controller.flushInput()
        self._controller.flushOutput()


    def flushInput(self):

        assert self._init, "Arduino has not been initialized"
        self._controller.flushInput()


    def flushOutput(self):
        assert self._init, "Arduino has not been initialized"
        self._controller.flushOutput()

    def write(self, controlCode):
        """
        Writes the control code to the arduino over the serial buffers
        :param controlCode:
        :return:
        """

        assert self._init, "Arduino has not been initialized"
        self._controller.write(controlCode) #send control code over



    def inWaiting(self):
        """
        Return waiting time
        :return:
        """
        return self._controller.inWaiting()

