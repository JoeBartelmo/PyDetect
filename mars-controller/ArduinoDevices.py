import logging


class LED(object):

    def __init__(self):
        self._LEDcodes = ['brightness']
        self._lastCommand = 'L0'
        self._brightness = 0



    def issue(self, arduino, controlCode):
        self._arduino = arduino

        if "brightness" in controlCode:
            if RepresentsInt(controlCode[11]):
                self._brightness = controlCode[11]
                self.write()

    def write(self):
        command = 'L' + str(self._brightness)
        self._arduino.write('L' + str(self._brightness))
        self._lastCommand = command


class Motor(object):

    def __init__(self):
        self._motorCodes = ['enable brake', 'disable brake', 'enable motor', 'disable motor']
        self._speed = 0
        self._lastCommand = 'M0000'
        self._direction = 0
        self._brake = 0
        self._enabled = 0

    def issue(self, myCode, arduino):
        self._arduino = arduino

        if myCode in ('enable motor', 'disable motor'):
            self.toggleMotor(myCode)
        elif myCode in ('enable brake', 'disable brake'):
            self.toggleBrake(myCode)


    def movement(self, myCode):

        if self._enabled == 0:
            return logging.info("Motor must be enabled before you can move! Use: enable motor")
        if self._brake == 1:
            return logging.info("Brake must be disabled to move! Use: disable break")

        if "forward" in myCode:
            if RepresentsInt(myCode[8]):
                self._direction = 1
                self._speed = myCode[8]
                self.write()
        elif "backward" in myCode:
            if RepresentsInt(myCode[8]):
                self._direction = 0
                self._speed = myCode[9]
                self.write()
        elif "brake" in myCode:
            self.brake()
        else:
            return logging.info("Speed must be 0-9. Direction must be forward or backward.")




    def toggleMotor(self, myCode):
        if myCode == 'enable motor':
            self._enabled = 1
        elif myCode == 'disable motor':
            self._enabled = 0

        self.write()

    def toggleBrake(self, myCode):
        if myCode == 'enable brake':
            self._brake = 1
        elif myCode == 'disable brake':
            self._brake = 0

        self.write()

    def start(self):
        self._speed = 4
        self._direction = 1
        self._enabled = 1
        self._brake = 0

        self.write()

    def brake(self):
        self._arduino.write("M0010")
        logging.info("Arduino braking...")


    def write(self):
        command = 'M' + str(self._enabled) + str(self._direction) + str(self._brake) + str(self._speed)
        logging.info(command)
        self._lastCommand = command
        self._arduino.write(command)




def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
