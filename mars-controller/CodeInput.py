'''
ark9719
6/17/2016
'''
import logging

class ConcreteMotorInput(object):
    """
    ConcreteMotorInput is a concrete implementation of the CodeInput base class used to check validity
    on Motor control input strings.

    FORMAT ==> MABCD
    'M' is the motion identifer "M"
    'A' is a binary operator to enable the Motor (motor must be enabled to move at all)
    'B' is a binary operator that defines direction (fwd, rev)
    'C' is a binary operator to engage the brake
    'D' is a decimal integer (0-9) that defines the speed(Each integer roughly corresponds 1Mph or .5m/s)
    """
    def __init__(self, code, arduino):

        self._code = code
        self._type = 'M'
        self._arduino = arduino



    def valid(self):

        #Check for binary inputs at positions A, B, C
        for c in self._code[1:4]:
            if int(c) not in (0, 1):
                logging.warning("Bad motor input entered")
                print("The second, third, or fourth integer in your code is not binary (0-1)")
                return False

        #Check for correct length
        if (len(self._code) != 5):
            logging.warning("Bad motor input entered")
            print("Incorrect code length, 1 character and 4 digits please.")
            return False

        #Check if D is integer
        if(not RepresentsInt(self._code[4])):
            logging.warning("Bad motor input entered")
            print("The last character in the code must be an integer.")
            return False

        return True

    def issue(self):
        self._arduino.write(self._code)
        self._arduino._lastMotor = self
        logging.info("Motor code written to Arduino.")





class ConcreteLEDInput():
    """
    ConcreteLEDInput is a concrete implementation of the CodeInput Base class used to check validity
    on LED control input strings.

    FORMAT ==> 'LX'
    L identifies LED, X is an integer (0-9) defining brightness
    """
    def __init__(self, code, arduino):
        self._code = code
        self._arduino = arduino
        self._type = 'L'

    def valid(self):

        #Check for code length and the second character to be int
        if (len(self._code) == 2 and RepresentsInt(self._code[1]) ):
            return True
        else:
            logging.warning("Bad LED input entered")
            print("Code was not length two or the second character was not an integer")
            return False

    def issue(self):
        self._arduino.write(self._code)
        self._arduino._lastLED = self
        logging.info("LED code written to Arduino.")

class ConcreteStreamInput():
    """
    ConcreteStreamInput is a class for codes intended to dynamically change stream settings

     FORMAT ==> SAB
    'S' is the stream code identifier
    'A' is the resolution changer [ 0 (640x480) or 1 (1280 x 960)]
    'B' is the bitrate integer (1-9)
    """

    def __init__(self, code, stream):
        self._code = code
        self._type = 'S'
        self._bitrate = code[2]
        self._stream = stream

    def valid(self):

        #Check code length
        if(len(self._code) != 3 ):
            logging.warning("Bad stream input entered")
            print("Code must be 3 characters long.")
            return False

        #Check first character for 0, 1
        if not RepresentsInt(self._code[1]) and not (self._code[1] in (0, 1, 2)):
            logging.warning("Bad stream input entered")
            print("Second character must be  0, 1, or 2.")
            return False

        #Check if 3rd character is int
        if not RepresentsInt(self._code[2]):
            logging.warning("Bad stream input entered")
            print("Third character must be integer (1-9).")
            return False

        if (int(self._code[2] == 0)):
            logging.warning("Bad stream input entered")
            print("Third character must be atleast 1")
            return False

        return True

    def issue(self):
        self._stream.issue(self)



class ConcreteSystemInput():
    """
    Specialized system commands - shutdown, restart, etc
    """

    def __init__(self, code, jetson, arduino, mars, sysCommands):
        self._code = code
        self._jetson = jetson
        self._arduino = arduino
        self._mars = mars
        self._sysCommands = sysCommands

    def valid(self):
        if self._code.lower() in (self._sysCommands):
            return True
        elif self._code in ('forward', 'backward'):
            return True
        else:
            return False

    def issue(self):
        """
        Forward, backward, or in the dictionary
        :return:
        """
        if self._code.lower() == 'forward':
            speed = raw_input("How fast?")
            self._arduino.write("M110" + speed)
            return
        elif self._code.lower() == 'backward':
            speed = raw_input("How fast?")
            self._arduino.write("M100" + speed)
            return
        elif self._code.lower() in self._sysCommands:
            self._sysCommands[self._code]()
            return
        else:
            logging.info("Unrecognizable code.")




def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

"""
def testing():
    mCodes = ['M0001', 'M0102', 'M000234', 'M000Q']
    lCodes = ['L1', 'LA', 'L123']
    sCodes = ['S123', 'SAB', 'S12345', 'S1A', 'SA1' ]

    for code in sCodes:
        testCode = ConcreteStreamInput(code)

        print(code + ' evaluates to : ')
        print(testCode.valid())
        print("-----------")



testing()
"""