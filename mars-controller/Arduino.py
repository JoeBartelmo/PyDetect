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

        print self._arduinoPath
        self._timeInit = time.time()
        self._lastLED = 'None yet'
        self._lastMotor = 'None yet'


        try:
            print("Attempting to connect Arduino")
            self._controller = serial.Serial(self._arduinoPath, self._config.constants.baud_rate)
            self._init = True
            logging.info('Arduino connected')
            print("Arduino connected.")
            time.sleep(.1)
        except serial.serialutil.SerialException:
            logging.info("Arduino didn't connect.")
            print("arduino not connected or device path wrong")
            print("check MARS user manual for details")
            print("unable to continue, program will now terminate")
            sys.exit()

    def serial_readline(self):
        """
        This method manages pulling the raw data off the arduino.
        :return:
        """
        if (self._init == False):
            print("Arduino has not been initialized!")

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
        if(self._init):
            self._controller.flushInput()
            self._controller.flushOutput()
        else:
            print("Arduino has not been initialized!")

    def flushInput(self):
        if(self._init):
            self._controller.flushInput()
        else:
            print("Arduino has not been initialized!")

    def flushOutput(self):
        if(self._init):
            self._controller.flushOutput()
        else:
            print("Arduino has not been initialized!")

    def write(self, controlCode):
        """
        Writes the control code to the arduino over the serial buffers
        :param controlCode:
        :return:
        """
        if (self._init):
            self._controller.write(controlCode) #send control code over
        else:
            print("Arduino has not been initialized!")


    def inWaiting(self):
        """
        Return waiting time
        :return:
        """
        return self._controller.inWaiting()

