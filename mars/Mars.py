'''
ark9719
6/17/2016
'''
import re
import time
import logging
import sys

logger = logging.getLogger('mars_logging')

class Mars(object):
    """
    Mars is in control of pulling data from the arduino and generating relevant telemetry statistics. This includes
    stats on time, battery, distance, power, and more.
    """

    def __init__(self, arduino, config, LED, Motor):
        self._arduino = arduino
        self._LED = LED
        self._Motor = Motor


        self._config = config
        self._integTime = time.time()
        self._currentBattery = self._config.constants.total_battery
        self._recallOverride = False

        statistics = {}
        self._statistics = statistics
        statistics.setdefault('TotalDistance', 0)
        statistics.setdefault('IntervalDistance', 0)
        statistics.setdefault('IntervalDisplacement', 0)
        statistics.setdefault('TotalDisplacement', 0)
        statistics.setdefault('BatteryRemaining', self._config.user_input.current_battery)

    def generateStatistics(self):
        """
        Through raw data and the work of helper functions, this method populates a dictionary stored attribute of Mars,
        statistics, with telemetry data.
        :param integTime:
        :return:
        """

        serialData = None
        if self._arduino._init == True:
            serialData = self._arduino.serial_readline()
        #returns none on error as well
        if serialData is None:
            logger.warning('Could not retrieve data from arduino')
            return None
        else:
            serialData = serialData.rstrip()
        rawArray = re.split(",", serialData)

        while(len(rawArray) < 5):
            serialData = self._arduino.serial_readline().rstrip()
            rawArray = re.split(",", serialData)
        #Assign integ time for use of helper functions
        copy = self._integTime
        currenttime = time.time()
        self._integTime = currenttime - copy

        logger.debug("Integ time:" + str(round(self._integTime, 4)) + ':\t'  + str(rawArray))
        self._statistics['RunClock'] = round(time.time() - self._arduino._timeInit, 4)

        rpm = rawArray[0]
        self._statistics['RPM'] = float(rpm)
        sysV = rawArray[1]
        self._statistics['SystemVoltage'] = float(sysV)
        sysI = rawArray[2]
        self._statistics['SystemCurrent'] = float(sysI)
        frontDistance = rawArray[3]
        self._statistics['FrontDistance'] = frontDistance

        backDistance = rawArray[4]
        if backDistance != 'out of range':
            backDistance = backDistance[0:len(sysI)-4]
        self._statistics['BackDistance'] = backDistance

        speed = self.estimatedSpeed() #speed in m/s
        self._statistics['Speed'] = speed
        power = self.estimatedPower(sysV, sysI) #power in Watts
        self._statistics['Power'] = power


        intDistance, totDistanceTraveled = self.distanceTraveled() #in Meters
        self._statistics['IntervalDistance'] = intDistance
        self._statistics['TotalDistance'] = totDistanceTraveled

        displacement, totalDisplacement = self.displacement() #in Meters
        self._statistics['IntervalDisplacement'] = displacement
        self._statistics['TotalDisplacement'] = totalDisplacement

        batteryRemaining = self.batteryRemaining(power)
        self._statistics['BatteryRemaining'] = batteryRemaining

        #pulling in last commands
        self._statistics['setSpeed'] = int(self._Motor._lastCommand[-1:]) * self._config.conversions.code_to_rpm
        self._statistics['LEDBrightness'] = self._LED._lastCommand

        return self._statistics

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

        rpm = float(self._statistics['RPM']) #rpm must be a float
        rpmToSpeed = self._config.conversions.rpm_to_speed
        estMps = rpm*rpmToSpeed #estimated SPEED in M/S

        returnEstMps = round(estMps, 1)
        self._statistics['Speed'] = returnEstMps
        return self._statistics['Speed']

    def estimatedPower(self, sysVoltage, sysCurrent):
        """
        estimates the current power usage of mars based off of voltage and current data.
            P = V * I
        :param sysVoltage:
        :param sysCurrent:
        :return:
        """
        sysVoltage = float(self._statistics['SystemVoltage'])
        sysCurrent = float(self._statistics['SystemCurrent'])
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

        intervalDistance = abs(self._statistics['Speed']) * time
        travAdded = self._statistics['TotalDistance'] + intervalDistance
        self._statistics['TotalDistance'] = travAdded
        #totalDistance = self._statistics['distanceTraveled']

        intervalDistanceRounded = round(intervalDistance,1)
        totalDistanceRounded = round(self._statistics['TotalDistance'], 1)

        return intervalDistanceRounded,totalDistanceRounded

    def displacement(self, time=None):
        """

        :param speed:
        :param time:
        :return:
        """
        if time == None:
            time = self._integTime

        intervalDisplacement = self._statistics['Speed'] * time
        self._statistics['IntervalDisplacement'] = self._statistics['IntervalDisplacement'] + intervalDisplacement
            # '--> updating the object attribute
        totalDisplacement = self._statistics['TotalDisplacement'] + intervalDisplacement

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

