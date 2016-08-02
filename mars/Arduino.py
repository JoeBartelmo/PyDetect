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
        self._init = False 
        self._timeInit = time.time()
        self._lastLED = 'None yet'
        self._lastMotor = 'None yet'
        self._arduino_pin = GpioPin(57)
        self._arduinoPath = None

        try:
            logger.info("Attempting to connect Arduino")
            if self.attemptConnection() == False:
                self.resetArduino()
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
                logger.error("No data coming from arduino before timeout")
                break;
        
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

    def resetArduino(self, timeout = 15):
        """
        Reset arduino system command
        :return:
        """
        self._init = False
        logger.info('Resetting the Arduino...')
        self._arduino_pin.toggleOn()
        self._arduino_pin.toggleOff()

        time.sleep(timeout)#give os time to refresh
        #attempt to restablish connection
        for index in range(timeout):
            if self.attemptConnection():
                break
            logger.warning('Attempt ' + str(index+1) + ', Could not connect to arduino, attempting to reset VIA arduino pin (10second wait)...')
            time.sleep(1)
        assert self._init, "Arduino Connection Lossed"

    def attemptConnection(self):
        try:
            arduinoPath = glob.glob('/dev/ttyACM*')[0]
            logger.info('Arduino path declared at:' + arduinoPath)
            self._arduinoPath = arduinoPath
            self._controller = serial.Serial(self._arduinoPath, self._config.constants.baud_rate)
            self._init = True
        except (IndexError, serial.serialutil.SerialException):
            self._init = False
        return self._init

    def _wrapFunctionRetryOnFail(self, function, onFail = None, attempts = 1, arg = None):
        """
        This is a wrapper for a given function that will surround
        the function in a try..catch IOError, and attempt to rerun the function once,
        Additionally it adds an 'assertArduinoConnetion' prior to running the function
        """
        if self._init == True:
            for index in range(attempts):
                try:
                    #self.assertArduinoConnection()
                    if arg is not None:
                        result = function(arg)
                    else:
                        result = function()
                    return result
                except (IOError, serial.serialutil.SerialException):
                    logger.warning('Caught a serialexception to arduino, passing through')
                    pass
                except Exception, err:     
                    #IOErrors are thrown by the serial controller, but they do not have the class IOError
                    #err = sys.exc_info()[0]
                    if hasattr(err, '__module__') == False or err.__module__ != 'termios':
                        logger.warning('Unknown Error raised: ' + str(vars(err)));
                        raise err
            if onFail != None:
                return onFail()
            elif self._init == False:
                logger.error('Arduino Connection is not established')
        else:
            logger.warning('Attempted to access arduino during connection reset...')

