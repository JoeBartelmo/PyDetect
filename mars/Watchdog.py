import logging
import time
from GpioPin import GpioPin
import subprocess

class Watchdog(object):
    def __init__(self, config, arduino, mars, pinHash):
        self._config = config
        self._arduino = arduino
        self._mars = mars

        self._levels = self._config.watchdog
        self._enableWatchdog = self._levels.enable_watchdog
        self._displayLogTimeout = self._levels.display_log_timeout

        self._shouldBrake = 0
        self._loggingTime = 0

        self._shouldDisplay = {"underVoltage":True,"overVoltage":True,"batteryPercentage":True,"overCurrent":True}
        self._electricStatistics = {'underVoltageLevel': 0, 'overVoltageLevel': 0, 'overCurrentLevel': 0,
                                    'batteryPercentageLevel': 0}
        self._pinHash = pinHash


    def systemShutdown(self):
        logging.info("initiating safe shutdown")
        ### add functionality to cut power to motor controller
        logging.info("shutting downn this computer")
        logging.info("this connection will be lost")
        subprocess.call(['sudo poweroff'], shell=True)

    def watch(self, statistics):
        self.sniff(statistics)

        if self._enableWatchdog == True:
            waitTime = time.time() - self._loggingTime
            if waitTime > self._displayLogTimeout:
                self._shouldDisplay = self._shouldDisplay.fromkeys(self._shouldDisplay.iterkeys(), True)
                self._loggingTime = time.time()
            self.bark()
        return self._electricStatistics

    def sniff(self, statistics):

        sysV = statistics['SystemVoltage']
        sysI = statistics['SystemCurrent']
        frontDistance = statistics['FrontDistance']
        backDistance = statistics['BackDistance']
        logging.info(sysV)
        logging.info(sysI)
        self.sniffOverCurrent(sysI)
        self.sniffOverVoltage(sysV)
        self.sniffUnderVoltage(sysV)
        self.sniffDistance(frontDistance, backDistance)

    def bark(self):
        self.barkAtOverVoltage()
        self.barkAtUnderVoltage()
        self.barkAtOverCurrent()
        self.barkAtBattPercent()
        if all(value == 0 for value in self._electricStatistics.values()) == True:
            self._pinHash['warningLED'].toggleOff() # turning off warning LED if all values == 0

    def sniffOverVoltage(self, sysV):
        # testing for overVoltage
        if sysV > self._levels.over_voltage_critical:
            self._electricStatistics['overVoltageLevel'] = 3  # overVoltage is at critical level
        elif sysV > self._levels.over_voltage_warning and sysV < self._levels.over_voltage_critical:
            self._electricStatistics['overVoltageLevel'] = 2  # overVoltage is at warning level
        elif sysV > self._levels.over_voltage_alert and sysV < self._levels.over_voltage_warning:
            self._electricStatistics['overVoltageLevel'] = 1  # overVoltage is at alert level
        elif sysV < self._levels.over_voltage_alert:
            self._electricStatistics['overVoltageLevel'] = 0

    def sniffUnderVoltage(self, sysV):
        # testing for underVoltage
        if sysV < self._levels.under_voltage_critical:
            self._electricStatistics['underVoltageLevel'] = 3  # underVoltage is at critical level
        elif sysV < self._levels.under_voltage_warning and sysV > self._levels.under_voltage_critical:
            self._electricStatistics['underVoltageLevel'] = 2  # underVoltage is at warning level
        elif sysV < self._levels.under_voltage_alert and sysV > self._levels.under_voltage_warning:
            self._electricStatistics['underVoltageLevel'] = 1  # underVoltage is at alert level
        elif sysV > self._levels.under_voltage_alert:
            self._electricStatistics['underVoltageLevel'] = 0

    def sniffOverCurrent(self, sysI):
        # testing for overCurrent
        if sysI > self._levels.over_current_critical:
            self._electricStatistics['overCurrentLevel'] = 3  # overCurrent is at critical level
        elif sysI > self._levels.over_current_warning and sysI < self._levels.over_current_critical:
            self._electricStatistics['overCurrentLevel'] = 2  # overCurrent is at warning level
        elif sysI > self._levels.over_current_alert and sysI < self._levels.over_current_warning:
            self._electricStatistics['overCurrentLevel'] = 1  # overCurrent is at alert level
        elif sysI < self._levels.over_current_alert:
            self._electricStatistics['overCurrentLevel'] = 0

    def sniffBatteryPercentage(self, batt):
        # testing for batteryPercentage
        if batt < self._levels.batt_percent_critical:
            self._electricStatistics['batteryPercentageLevel'] = 3  # batteryPercentage is at critical level
        elif batt < self._levels.batt_percent_warning and batt > self._levels.batt_percent_critical:
            self._electricStatistics['batteryPercentageLevel'] = 2  # batteryPercentage is at warning level
        elif batt < self._levels.batt_percent_alert and batt > self._levels.batt_percent_warning:
            self._electricStatistics['batteryPercentageLevel'] = 1  # batteryPercentage is at alert level
        elif batt > self._levels.batt_percent_alert:
            self._electricStatistics['batteryPercentageLevel'] = 0

    def sniffDistance(self, frontDistance, backDistance):
        distanceList = [frontDistance, backDistance]
        if frontDistance == 'out of range' and backDistance == 'out of range':
            self._shouldBrake = 0
        else:
            distanceList = filter(lambda a: a != 'out of range', distanceList)
            if min(distanceList) < self._levels.braking_distance:
                self._shouldBrake = 1



    def barkAtBattPercent(self):
        value = self._electricStatistics['batteryPercentageLevel']
        display = self._shouldDisplay["batteryPercentage"]

        if value in (1, 2, 3):
            self._pinHash['batteryLED'].toggleOn()
            if display == True:
                logging.critical("battery level at warning level" + str(value))

        if value == 3:
           logging.critical("recommend initiating recall")

        elif value == 2:
            logging.critical("recommend ending run soon")

        elif value == 1:
            logging.warning("battery level at warning level 1")


    def barkAtOverCurrent(self):
        value = self._electricStatistics['overCurrentLevel']
        display = self._shouldDisplay["overCurrent"]

        if value in (1, 2, 3):
            self._pinHash['warningLED'].toggleOn()
            if display == True:
                logging.critical("overCurrent at warning level " + str(value))

        if value == 2:
            logging.critical("current draw is much higher than expected")

        elif value == 3:
            logging.critical("too much current detected! Recommend SHUTDOWN")

    def barkAtUnderVoltage(self):
        value = self._electricStatistics['underVoltageLevel']
        if value in (1, 2, 3):
            self._pinHash['warningLED'].toggleOn()
            self._pinHash['batteryLED'].toggleOn()
            if self._shouldDisplay["underVoltage"] == True:
                logging.critical("underVoltage warning at level " + str(value))
                self._shouldDisplay['underVoltage'] = False

        if value == 3:
            logging.critical("initiating emergency shutdown")
            self.systemShutdown()

        elif value == 2:
            logging.critical('battery may be near death!')

        elif value == 1:
            logging.warning("battery may be close to dying, please check")




    def barkAtOverVoltage(self):
        value = self._electricStatistics['overVoltageLevel']
        # OVERVOLTAGE
        if value == 3:
            self._pinHash['warningLED'].toggleOn()
            self._pinHash['motorRelay'].toggleOff()
            self._pinHash['ledRelay'].toggleOff()
            self._pinHash['laserRelay'].toggleOff()
            self._pinHash['relay4'].toggleOff()

            if self._shouldDisplay['overVoltage'] == True:
                logging.critical("overVoltage warning at level 3")
                logging.critical("motor, LEDs, and laser circuits turned off")
                logging.critical("recommend disabling watchdog and recalling mars")
        elif value == 2:
            self.recall()
            self._pinHash['warningLED'].toggleOn()
            if self._shouldDisplay['overVoltage'] == True:
                logging.critical("overVoltage at warning level 2")
                logging.critical("recommend enabling a recall")
        elif value == 1:
            self._pinHash['warningLED'].toggleOn()
            if self._shouldDisplay['overVoltage'] == True:
                logging.warning("overVoltage at warning level 1")
                logging.warning("recommend checking power supply")


    def recall(self):
        # tell mars to head backwards toward operator
        self._arduino.write(self._levels.recall_code)
        logging.critical("recall initiated")
        logging.critical("type 'disable watchdog' to resume control")


    def disable(self):
        if self._enableWatchdog == False:
            logging.warning("watchdog is already disabled")
        else:
            self._enableWatchdog = True
            logging.critical("watchdog disabled")


    def enable(self):
        if self._enableWatchdog == True:
            logging.warning("watchdog is already enabled")
        else:
            self._enableWatchdog = True
            logging.critical("watchdog enabled")

