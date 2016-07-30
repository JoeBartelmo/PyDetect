import logging
import os
"""

Usable GPIO pins are as follows

160,161,162,163,164,165,166,57

#EMBED ANY REFERENCE TO THIS IN A TRY STATEMENT
##ValueError will be generated if there is an invalid gpioPin



#MUST MODIFY WATCHDOG TO MONITOR AND CHANGE INDICATORS 

create 8 pin objects:

	reset pin (166)
	connection LED (163)
	warning LED (164)
	batt LED (165)
	relay 1 (57)
	relay 2 (160)
	relay 3 (161)
	relay 4 (162)


"""



gpio_list = [57,160,161,162,163,164,165,166]

class GpioPin(object):

    def __init__(self, gpioPin, direction = 'out'):
        self._state = 0
        self._direction = direction

        if gpioPin in gpio_list:
            self._gpioPin = gpioPin
            #self.setup()
            self.toggleOn()
        else:
            logging.warning("GPIO PIN SETUP FAILED\r\nGPIO pin {} does not exist".format(str(gpioPin)))
            logging.warning("GPIO pin must be one of the following {}".format(str(gpio_list)))
            raise ValueError("invalid GPIO pin number")


    def setup(self):
        #exporting the GPIO pin so it can be accessed
        with open('/sys/class/gpio/export','w') as export_file:
            if not os.path.exists('/sys/class/gpio/export/gpio' + str(self._gpioPin)):
                export_file.write(str(self._gpioPin))
        #setting the pin direction
        with open('/sys/class/gpio/gpio{}/direction'.format(str(self._gpioPin)),'w') as direction_file:
            direction_file.write(self._direction)


    def changeState(self,state):
        if self._direction == "out":
            with open('/sys/class/gpio/gpio{}/value'.format(str(self._gpioPin)),'w') as value_file:
                value_file.write(str(state))
        else:
            raise ValueError("pin must be an output to change it's state")

        self._state = state

    def toggleOn(self):
        if self._direction == "out":
            with open('/sys/class/gpio/gpio{}/value'.format(str(self._gpioPin)),'w') as value_file:
                value_file.write(str(0))
        else:
            raise ValueError("pin must be an output to change it's state")

    def toggleOff(self):
        if self._direction == "out":
            with open('/sys/class/gpio/gpio{}/value'.format(str(self._gpioPin)),'w') as value_file:
                value_file.write(str(1))
        else:
            raise ValueError("pin must be an output to change it's state")





