import logging
import time
import sys
from Arduino import Arduino
from ArduinoDevices import Motor, LED
from Jetson import Jetson
from Mars import Mars
from Stream import Stream
from Watchdog import Watchdog
from Valmar import Valmar

logger = logging.getLogger('mars_logging')

class System(object):

    def __init__(self, config, timestamp, q = None):

        #Init devices

        self._devices = self.initDevices(config)

        #Prepare stream
        self._devices['Stream'] = Stream(config, timestamp)

        logger.info("Connecting Jetson")
        self._jetson = Jetson(self._devices, config, timestamp, q)
        time.sleep(.5)


        logger.info("All devices connected")
        logger.info("System initialized.")

        if q is None:
            answer = raw_input("Would you like to start? Y/n: ")
            if answer.lower() == 'n' or answer.lower() == 'no':
                self._jetson.exit()
            else:
                self._jetson.start()
        else:
            self._jetson.start()

    def initDevices(self, config):
        """
        Prepare the arduino, the LED, the motor, and the composite mars object with corresponding VALMAR and devicehash
        for jetson.
        :param config:
        :return:
        """

        #self._arduino.arduinoPowerOn()
        logger.info("Connecting arduino...")
        myArduino = Arduino(config)
        time.sleep(.5)

        #Flush buffers
        myArduino.flushBuffers()

        logger.info("Starting Mars...")
        myLED = LED()
        myMotor = Motor()
        myMars = Mars(myArduino, config, myLED, myMotor)
        time.sleep(.5)


        myValmar = Valmar(config, myMars)

        devices = {
                    'Motor': myMotor,
                    'LED': myLED,
                    'Mars': myMars,
                    'Arduino': myArduino,
                    'Valmar': myValmar,
        }
        return devices
