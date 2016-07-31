'''
ark9719
6/17/2016
'''
import sys
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
        self._arduino_pin = GpioPin(57)
        self._arduinoPath = None

        try:
            logger.info("Attempting to connect Arduino")
            self.assertArduinoConnection()
        except AssertionError:
            logger.critical("Arduino not connected: device path either wrong or arduino misconfigured")
            logger.critical("Check MARS user manual for details")
            logger.critical("Unable to continue, program will now terminate")
            sys.exit()

    def serial_readline(self):
        """
        This method manages pulling the raw data off the arduino.
        :return:
        """
        
        waitStart = time.time()
        waitTime = time.time() - waitStart
        timeout = self._config.constants.timeout
        
        while self.inWaiting() == 0:
            if waitTime < timeout:
                waitTime = time.time() - waitStart
            elif waitTime >= timeout:
                logger.critical("No data coming from arduino before timeout")
        
        # added short delay just in case data was in transit
        time.sleep(.001)

        # read telemetry sent by Arduino
        serialData = self._wrapFunctionRetryOnFail(self._controller.readline)
        # flushing in case there was a buildup
        self.flushInput()
        return serialData

    def flushBuffers(self):
        """
        Function to flush arduinos serial buffers
        :return:
        """
        self._controller.flushInput()
        self._controller.flushOutput()

    def flushInput(self):
        """
        Flush exclusively the input buffer from the arduino
        :return:
        """
        self._wrapFunctionRetryOnFail(self._controller.flushInput)


    def flushOutput(self):
        """
        Flush exclusively the output buffer from the arduino
        :return:
        """
        self._wrapFunctionRetryOnFail(self._controller.flushOutput)

    def write(self, controlCode):
        """
        Writes the control code to the arduino over the serial buffers
        :param controlCode:
        :return:
        """
        self._wrapFunctionRetryOnFail(self._controller.write, arg = controlCode)

    def inWaiting(self):
        """
        Return waiting time
        :return:
        """
        return self._wrapFunctionRetryOnFail(self._controller.inWaiting)

    def resetArduino(self):
        """
        Reset arduino system command
        :return:
        """
        logger.info('Resetting the Arduino...')
        self._arduino_pin.toggleOff()
        time.sleep(1)
        self._arduino_pin.toggleOn()

    def assertArduinoConnection(self):
        """
        Validates that the arduino is connected.
        In the event that the arduino is no longer
        connected, 5 retry attempts will occur to attempt
        a rekindling. 

        On fail: assertion error
        On success: void
        """ 
        for i in range(5):
            try:
                arduinoPath = glob.glob('/dev/ttyACM*')[0]
                if self._arduinoPath != arduinoPath:
                    logger.info('Arduino path declared at:' + arduinoPath)
                    self._arduinoPath = arduinoPath
                    self._controller = serial.Serial(self._arduinoPath, self._config.constants.baud_rate)
                self._init = True
                break
            except IndexError:
                self._init = False
                logger.warning('Attempt ' + str(i) + ', Could not connect to arduino, attempting to reset VIA arduino pin...')
                self.resetArduino()
                time.sleep(3)
        
        assert self._init, "Arduino has not been initialized"

    def _wrapFunctionRetryOnFail(self, function, onFail = None, attempts = 1, arg = None):
        """
        This is a wrapper for a given function that will surround
        the function in a try..catch IOError, and attempt to rerun the function once,
        Additionally it adds an 'assertArduinoConnetion' prior to running the function
        """
        if self._init:
            for i in range(attempts):
                try:
                    self.assertArduinoConnection()
                    if arg is not None:
                        result = function(arg)
                    else:
                        result = function()
                    return result
                except (IOError, serial.serialutil.SerialException):
                    pass
                except Exception, err:     
                    #IOErrors are thrown by the serial controller, but they do not have the class IOError
                    #err = sys.exc_info()[0]
                    if err.__module__ != 'termios':
                        logger.warning('Unknown Error raised: ' + str(vars(err)));
                        raise err
            if onFail != None:
                return onFail()
        else:
            logger.error('Arduino Connection is not established')

