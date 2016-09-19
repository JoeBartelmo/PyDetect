'''
ark9719
6/17/2016
'''
import re
import time
import logging
from Queue import Empty
import sys

logger = logging.getLogger('mars_logging')

class Mars(object):
    """
    Mars is in control of pulling data from the arduino and generating relevant telemetry telemetry. This includes
    stats on time, battery, distance, power, and more.
    """

    def __init__(self, arduino, config, LED, Motor, pinHash, watchdogQueue, marsOnlineQueue):
        self._arduino = arduino
        self._LED = LED
        self._Motor = Motor
        self._pinHash = pinHash

        self._config = config
        self._integTime = time.time()
        self._currentBattery = self._config.constants.total_battery
        self._recallOverride = False
        self._watchdogQueue = watchdogQueue
        self._marsOnlineQueue = marsOnlineQueue

        telemetry = {}
        self._telemetry = telemetry
        telemetry.setdefault('TotalDistance', 0)
        telemetry.setdefault('IntervalDistance', 0)
        telemetry.setdefault('IntervalDisplacement', 0)
        telemetry.setdefault('TotalDisplacement', 0)
        telemetry.setdefault('BatteryRemaining', self._config.user_input.current_battery)

    def generateTelemetry(self):
        """
        Through raw data and the work of helper functions, this method populates a dictionary stored attribute of Mars,
        telemetry, with telemetry data.
        :param integTime:
        :return:
        """
        
        if self._marsOnlineQueue is not None:
            self._marsOnlineQueue.put(1)

        serialData = None
        if self._arduino._init == True:
            serialData = self._arduino.serial_readline()
        #returns none on error as well
        if serialData is None:
            #logger.warning('Could not retrieve data from arduino')
            return None
        else:
            serialData = serialData.strip().replace('\0','')
        rawArray = re.split(",", serialData)

        while(len(rawArray) < 4):
            serialData = self._arduino.serial_readline().rstrip()
            rawArray = re.split(",", serialData)
        #Assign integ time for use of helper functions
        copy = self._integTime
        currentTime = time.time()
        self._integTime = currentTime - copy

        logger.debug("Integration time:" + str(round(self._integTime, 4)) + ':\t'  + str(rawArray))
        self._telemetry['RunClock'] = round(time.time() - self._arduino._timeInit, 4)
        self._telemetry['Ping'] = self.checkConnection()

        rpm = rawArray[0]
        self._telemetry['RPM'] = float(rpm)
        sysV = rawArray[1]
        self._telemetry['SystemVoltage'] = float(sysV)
        sysI = rawArray[2]
        self._telemetry['SystemCurrent'] = float(sysI)
        sensorDistance = rawArray[3]
        self._telemetry['SensorDistance'] = sensorDistance

        speed = self.estimatedSpeed() #speed in m/s
        self._telemetry['Speed'] = speed
        power = self.estimatedPower(sysV, sysI) #power in Watts
        self._telemetry['Power'] = power


        intDistance, totDistanceTraveled = self.distanceTraveled() #in Meters
        intDistance, totDistanceTraveled = self.distanceTraveled() #in Meters
        self._telemetry['IntervalDistance'] = intDistance
        self._telemetry['TotalDistance'] = totDistanceTraveled

        displacement, totalDisplacement = self.displacement() #in Meters
        self._telemetry['IntervalDisplacement'] = displacement
        self._telemetry['TotalDisplacement'] = totalDisplacement
        self._telemetry['BatteryRemaining'] = self.batteryRemaining(power)

        #pulling in last commands
        self._telemetry['SetSpeed'] = int(self._Motor._lastCommand[-1:]) * self._config.conversions.code_to_rpm
        self._telemetry['LEDBrightness'] = self._LED._lastCommand.replace('L','')

        #pulling in the state of relays
        self._telemetry['MotorCircuit'] = self._pinHash['motorRelay']._state
        self._telemetry['LedCircuit'] =  self._pinHash['ledRelay']._state
        self._telemetry['LaserCircuit'] = self._pinHash['laserRelay']._state
        return self._telemetry

    def estimatedSpeed(self):
        """
        This function guesses how fast Mars is going based on the lastest RPM
        data from the DAQ.

        It does not take into account any other factors or forces, as a result
        this is an ESTIMATED SPEED, not a real speed

        this conversion is will only work for the current generation of MARS and
        is a function of this equation
            speed in mph ~= rpm/221
            speed in m/s ~= (rpm/221)*0.44704

        :param rpm:
        :return:
        """

        rpm = float(self._telemetry['RPM']) #rpm must be a float
        rpmToSpeed = self._config.conversions.rpm_to_speed
        estMps = rpm*rpmToSpeed #estimated SPEED in M/S

        returnEstMps = round(estMps, 1)
        self._telemetry['Speed'] = returnEstMps
        return self._telemetry['Speed']

    def estimatedPower(self, sysVoltage, sysCurrent):
        """
        estimates the current power usage of mars based off of voltage and current data.
            P = V * I
        :param sysVoltage:
        :param sysCurrent:
        :return:
        """
        sysVoltage = float(self._telemetry['SystemVoltage'])
        sysCurrent = float(self._telemetry['SystemCurrent'])
        estPower = sysVoltage * sysCurrent

        powerReturned = round(estPower, 2)
        return powerReturned

    def distanceTraveled(self, time=None):
        """
        returns the estimated distance traveled by mars. If the user feed this function a time parameter, then this will
        calculate the new distance based on the current speed and time given. Otherwise it will return the last
        calculated distance traveled by Mars.
        :param speed:
        :param time:
        :return:
        """
        if time == None:
            time = self._integTime

        intervalDistance = abs(self._telemetry['Speed']) * time
        travAdded = self._telemetry['TotalDistance'] + intervalDistance
        self._telemetry['TotalDistance'] = travAdded
        #totalDistance = self._telemetry['distanceTraveled']

        intervalDistanceRounded = round(intervalDistance,1)
        totalDistanceRounded = round(self._telemetry['TotalDistance'], 1)

        return intervalDistanceRounded,totalDistanceRounded

    def displacement(self, time=None):
        """

        :param speed:
        :param time:
        :return:
        """
        if time == None:
            time = self._integTime

        intervalDisplacement = self._telemetry['Speed'] * time
        self._telemetry['IntervalDisplacement'] = self._telemetry['IntervalDisplacement'] + intervalDisplacement
            # '--> updating the object attribute
        totalDisplacement = self._telemetry['TotalDisplacement'] + intervalDisplacement

        intervalDisplacement = round(intervalDisplacement,1) #Rounding for readability
        totalDisplacement = round(totalDisplacement, 1)

        return intervalDisplacement,totalDisplacement



    def batteryRemaining(self,power=None, time = None):
        """
        battery_remaining(power *optional*, time *optional*)::
        if the user inputs power or time data, then this function will calculate how much energy remains in the
        batteries. otherwise ths will return the last calculated battery status
        :param power:
        :param time:
        :return:
        """

        if time == None:
            time = self._integTime
        ########^^^^^^^^FIX THIS ONCE DEBUGGING IS COMPLETE^^^^^^^^###########

        if power != None:

            #print(power)
            #print(time)
            joulesUsed  = float(power) * time
            #print(joulesUsed)
            whrUsed = joulesUsed/3600.0 #converting Joules to Watt*hours
            #print(whrUsed)

            self._currentBattery = float(self._currentBattery) - whrUsed
            #subtracting energy used from battery total

        battPercent = float(self._currentBattery) / float(self._config.constants.total_battery) * 100.0
        battPercentReturned = round(battPercent, 1)

        return battPercentReturned

    def checkConnection(self):
        '''
        If Mars is launched via server, this will check connection and return either 1 or 0.
        Otherwise always returns 1
        '''
        #if there is no watchdog queue, then we do not have a client connection, we're local testing
        if self._watchdogQueue is None:
            return 1
        try:
            return self._watchdogQueue.get(timeout=self._config.watchdog.display_log_timeout)
        except Empty:
            return 0

