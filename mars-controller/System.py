import logging
import time
import sys
from Arduino import Arduino
from ArduinoDevices import Motor, LED
from Jetson import Jetson
from Mars import Mars
from Stream import Stream
from Threads import InputThread, TelemetryThread
from Watchdog import Watchdog
from Valmar import Valmar
from GpioPin import GpioPin

class System(object):

    def __init__(self, config, timestamp, q = None):

        #Init devices
        self._devices = self.initDevices(config)

        #Prepare stream
        self._devices['Stream'] = Stream(config, timestamp)

        logging.info("Connecting Jetson")
        self._jetson = Jetson(self._devices, config, timestamp, q)
        time.sleep(.5)


        logging.info("All devices connected")
        logging.info("System initialized.")

        if q is None:
            answer = raw_input("Would you like to start? Y/N: ")
        else:
            logging.info('Would you like to start? Y/N')
            answer = q.get()
        if answer.lower() in ('y', 'yes'):
            print ("The system will start. ")
            self._jetson.start()
        if answer.lower() in ('n', 'no'):
            print ("Manual mode starting")
            self._jetson.manual()


    def initDevices(self, config):
        """
        Prepare the arduino, the LED, the motor, and the composite mars object with corresponding VALMAR and devicehash
        for jetson.
        :param config:
        :return:
        """

        #self._arduino.arduinoPowerOn()
        logging.info("Connecting arduino...")
        logging.info('Attempting to connect Arduino')
        myArduino = Arduino(config)
        time.sleep(.5)

        #Flush buffers
        myArduino.flushBuffers()

        logging.info("Starting Mars...")
        myPinHash = {'resetArduino': GpioPin(57),
                         'connectionLED': GpioPin(163),
                         'warningLED': GpioPin(164),
                         'batteryLED': GpioPin(165),
                         'motorRelay': GpioPin(166),
                         'ledRelay': GpioPin(160),
                         'laserRelay': GpioPin(161),
                         'relay4': GpioPin(162)
                         }
        myLED = LED()
        myMotor = Motor()
        myMars = Mars(myArduino, config, myLED, myMotor, myPinHash)
        time.sleep(.5)
        myValmar = Valmar(config, myMars)


        devices = {
                    'Motor': myMotor,
                    'LED': myLED,
                    'Mars': myMars,
                    'Arduino': myArduino,
                    'Valmar': myValmar,
                    'pinHash': myPinHash
        }
        return devices