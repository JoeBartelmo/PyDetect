import logging
import time
import sys
from Arduino import Arduino
from ArduinoDevices import Motor, LED
from Jetson import Jetson
from Mars import Mars
from Stream import Stream
from Threads import InputThread, StatisticsThread
from Watchdog import Watchdog
from Valmar import Valmar

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

        #self._arduino.arduinoPowerOn()
        logging.info("Connecting arduino...")
        logging.info('Attempting to connect Arduino')
        myArduino = Arduino(config)
        time.sleep(.5)

        #Flush buffers
        myArduino.flushBuffers()

        logging.info("Starting Mars...")
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