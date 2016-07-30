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
from GpioPin import GpioPin

logger = logging.getLogger('mars_logging')

class Arduino(object):

    def __init__(self, config):
        """
        Initialize the arduino. Load the configurations, load the device path, record the time initialized.
        Try and read from the device.
        :param config: Configurations from start up
        :return:
        """
        self._config = config
        self._init = False #False until initialized
        self._timeInit = time.time()
        self._lastLED = 'None yet'
        self._lastMotor = 'None yet'
        self._arduino_pin = GpioPin(166)

        try:
            logger.info("Attempting to connect Arduino")
            self._arduinoPath = None
            for i in range(5):
                try:
                    self._arduinoPath = glob.glob('/dev/ttyACM*')[0]
                    logger.info(self._arduinoPath)
                    break
                except IndexError:
                    logger.error('Attempt ' + str(i) + ', Could not connect to arduino, attempting to reset VIA arduino pin...')
                    self.resetArduino()
                    time.sleep(3)
            if self._arduinoPath is None:
                raise serial.serialutil.SerialException()
            self._controller = serial.Serial(self._arduinoPath, self._config.constants.baud_rate)
            self._init = True
            logger.info('Arduino connected')
            time.sleep(.1)
        except serial.serialutil.SerialException:
            logger.critical("Arduino not connected: device path either wrong or arduino misconfigured")
            logger.critical("Check MARS user manual for details")
            logger.critical("Unable to continue, program will now terminate")
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
        try:
            while self._controller.inWaiting() == 0:
                if waitTime < timeout:
                    waitTime = time.time() - waitStart
                elif waitTime >= timeout:
                    logger.critical("No data coming from arduino before timeout")
                    logger.critical("Ending program, check arduino or timeout duration")
                    sys.exit()
            else:
                # added short delay just in case data was in transit
                time.sleep(.001)

                # read telemetry sent by Arduino
                serialData = self._controller.readline()

                # flushing in case there was a buildup
                self._controller.flushInput()

                return serialData
        except IOError:
            logger.critical("Arduino connection was halted; it could have been removed in transit")
            logger.critical("Forced to End Program")
            self._init = None
            sys.exit()

    def flushBuffers(self):
        """
        Function to flush arduinos serial buffers
        :return:
        """
        assert self._init, "Arduino has not been initialized"

        self._controller.flushInput()
        self._controller.flushOutput()

    def flushInput(self):
        """
        Flush exclusively the input buffer from the arduino
        :return:
        """
        assert self._init, "Arduino has not been initialized"
        self._controller.flushInput()


    def flushOutput(self):
        """
        Flush exclusively the output buffer from the arduino
        :return:
        """
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

    def resetArduino(self):
        """
        Reset arduino system command
        :return:
        """
        self._arduino_pin.toggleOff()
        time.sleep(.2)
        self._arduino_pin.toggleOn()

