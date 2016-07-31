import logging

logger = logging.getLogger('mars_logging')

class LED(object):
    """
    An LED class representing the LED's attached to MARS. Currently, the only command modifies their brightness 0-9
    """

    def __init__(self):
        self._LEDcodes = ['brightness']
        self._lastCommand = 'L0'
        self._brightness = 0

    def issue(self, arduino, controlCode):
        """
        Issue an LED command. Store the data contained in the command an issue a write.
        :param arduino:
        :param controlCode:
        :return:
        """
        self._arduino = arduino
        splitCode = controlCode.split(' ')

        if len(splitCode) == 2 and 'brightness' == splitCode[0] and RepresentsInt(controlCode[1]):
            self._brightness = controlCode[1] 
            self.write()

    def write(self):
        """
        Write the last stored command to the arduino
        :return:
        """
        command = 'L' + str(self._brightness)
        self._arduino.write('L' + str(self._brightness))
        self._lastCommand = command

class Motor(object):
    """
    A class representing the motor attached to MARS. Contains all relevant directional, speed and motor data.
    """

    def __init__(self):
        self._motorCodes = ['enable brake', 'disable brake', 'enable motor', 'disable motor']
        self._speed = 0
        self._lastCommand = 'M0000'
        self._direction = 0
        self._brake = 0
        self._enabled = 0

    def issue(self, myCode, arduino):
        """
        Issue a motor command.
        :param myCode:
        :param arduino:
        :return:
        """
        self._arduino = arduino

        if myCode in ('enable motor', 'disable motor'):
            self.toggleMotor(myCode)
        elif myCode in ('enable brake', 'disable brake'):
            self.toggleBrake(myCode)


    def movement(self, myCode):
        """
        Decipher the type of movement command, store the values and call to the arduino.
        :param myCode:
        :return:
        """

        if self._enabled == 0:
            return logger.info("Motor must be enabled before you can move! Use: enable motor")
        if self._brake == 1:
            return logger.info("Brake must be disabled to move! Use: disable brak")
        
        splitCodes = myCode.split(' ')

        if len(splitCodes) == 2 and RepresentsInt(splitCodes[1]):
            self._direction = 1 if 'forward' == splitCodes[0] else 0
            self._speed = splitCodes[1]
            self.write()
        elif "brake" == splitCodes[0]:
            self.brake()
        else:
            return logger.warning("Speed must be 0-9. Direction must be forward or backward.")

    def toggleMotor(self, myCode):
        """
        Toggles the motor
        :param myCode:
        :return:
        """
        if myCode == 'enable motor':
            self._enabled = 1
        elif myCode == 'disable motor':
            self._enabled = 0

        self.write()

    def toggleBrake(self, myCode):
        """
        Toggles the brake
        :param myCode:
        :return:
        """
        if myCode == 'enable brake':
            self._brake = 1
        elif myCode == 'disable brake':
            self._brake = 0

        self.write()

    def start(self):
        """
        Default motor configurations
        :return:
        """
        self._enabled = 0
        self._direction = 0
        self._brake = 1
        self._speed = 0 

        self.write()

    def brake(self):
        """
        Hard brake setting
        :return:
        """
        self._arduino.write("M0010")
        logger.info("Arduino braking...")

    def write(self):
        """
        Write respective motor command to the arduino
        :return:
        """
        command = 'M' + str(self._enabled) + str(self._direction) + str(self._brake) + str(self._speed)
        logger.info('Writing the following command to the Arduino: ' + command)
        self._lastCommand = command
        self._arduino.write(command)

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
