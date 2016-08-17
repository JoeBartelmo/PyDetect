import logging
import time
import subprocess

logger = logging.getLogger('mars_logger')

class Watchdog(object):
    def __init__(self, config, arduino, mars, pinHash):
        self._config = config
        self._arduino = arduino
        self._mars = mars

        self._levels = self._config.watchdog
        self._enableWatchdog = self._levels.enable_watchdog
        self._displayLogTimeout = self._levels.display_log_timeout
        self._connectionDownTime = 0
        self._lastConnection = time.time()

        self._shouldBrake = 0
        self._loggerTime = 0

        self._shouldDisplay = {"underVoltage":True,
                               "overVoltage":True,
                               "batteryPercentage":True,
                               "overCurrent":True
                               }
        self._electricStats = {'underVoltageLevel': 0,
                                    'overVoltageLevel': 0,
                                    'overCurrentLevel': 0,
                                    'batteryPercentageLevel': 0
                                    }
        self._pinHash = pinHash


    def systemShutdown(self):
        logger.info("initiating safe shutdown")
        ### add functionality to cut power to motor controller
        logger.info("shutting downn this computer")
        logger.info("this connection will be lost")
        self._pinHash['motorRelay'].toggleOff()
        self._pinHash['laserRelay'].toggleOff()
        self._pinHash['ledRelay'].toggleOff()       
        subprocess.call(['sudo poweroff'], shell=True)

    def watch(self, telemetry):
        self.sniff(telemetry)

        if self._enableWatchdog == True:
            waitTime = time.time() - self._loggerTime
            if waitTime > self._displayLogTimeout:
                self._shouldDisplay = self._shouldDisplay.fromkeys(self._shouldDisplay.iterkeys(), True)
                self._loggerTime = time.time()
            self.bark()
        return self._electricStats

    def sniff(self, telemetry):

        sysV = telemetry['SystemVoltage']
        sysI = telemetry['SystemCurrent']
        sensorDistance = telemetry['SensorDistance']
        connectionStatus = telemetry['ConnectionStatus']
        self.sniffOverCurrent(sysI)
        self.sniffOverVoltage(sysV)
        self.sniffUnderVoltage(sysV)
        self.sniffDistance(sensorDistance)
        self.sniffConnection(connectionStatus)

    def bark(self):
        self.barkAtOverVoltage()
        self.barkAtUnderVoltage()
        self.barkAtOverCurrent()
        self.barkAtBattPercent()
        if all(value == 0 for value in self._electricStats.values()) == True:
            self._pinHash['warningLED'].toggleOff() # turning off warning LED if all values == 0

    def sniffOverVoltage(self, sysV):
        # testing for overVoltage
        if sysV > self._levels.over_voltage_critical:
            self._electricStats['overVoltageLevel'] = 3  # overVoltage is at critical level
        elif sysV > self._levels.over_voltage_warning and sysV < self._levels.over_voltage_critical:
            self._electricStats['overVoltageLevel'] = 2  # overVoltage is at warning level
        elif sysV > self._levels.over_voltage_alert and sysV < self._levels.over_voltage_warning:
            self._electricStats['overVoltageLevel'] = 1  # overVoltage is at alert level
        elif sysV < self._levels.over_voltage_alert:
            self._electricStats['overVoltageLevel'] = 0

    def sniffUnderVoltage(self, sysV):
        # testing for underVoltage
        if sysV < self._levels.under_voltage_critical:
            self._electricStats['underVoltageLevel'] = 3  # underVoltage is at critical level
        elif sysV < self._levels.under_voltage_warning and sysV > self._levels.under_voltage_critical:
            self._electricStats['underVoltageLevel'] = 2  # underVoltage is at warning level
        elif sysV < self._levels.under_voltage_alert and sysV > self._levels.under_voltage_warning:
            self._electricStats['underVoltageLevel'] = 1  # underVoltage is at alert level
        elif sysV > self._levels.under_voltage_alert:
            self._electricStats['underVoltageLevel'] = 0

    def sniffOverCurrent(self, sysI):
        # testing for overCurrent
        if sysI > self._levels.over_current_critical:
            self._electricStats['overCurrentLevel'] = 3  # overCurrent is at critical level
        elif sysI > self._levels.over_current_warning and sysI < self._levels.over_current_critical:
            self._electricStats['overCurrentLevel'] = 2  # overCurrent is at warning level
        elif sysI > self._levels.over_current_alert and sysI < self._levels.over_current_warning:
            self._electricStats['overCurrentLevel'] = 1  # overCurrent is at alert level
        elif sysI < self._levels.over_current_alert:
            self._electricStats['overCurrentLevel'] = 0

    def sniffBatteryPercentage(self, batt):
        # testing for batteryPercentage
        if batt < self._levels.batt_percent_critical:
            self._electricStats['batteryPercentageLevel'] = 3  # batteryPercentage is at critical level
        elif batt < self._levels.batt_percent_warning and batt > self._levels.batt_percent_critical:
            self._electricStats['batteryPercentageLevel'] = 2  # batteryPercentage is at warning level
        elif batt < self._levels.batt_percent_alert and batt > self._levels.batt_percent_warning:
            self._electricStats['batteryPercentageLevel'] = 1  # batteryPercentage is at alert level
        elif batt > self._levels.batt_percent_alert:
            self._electricStats['batteryPercentageLevel'] = 0

    def sniffDistance(self, sensorDistance):
        if sensorDistance.replace('\r', '').replace('\n', '') == 'out of range':
            self._shouldBrake = 0
        else:
            if sensorDistance < self._levels.braking_distance:
                self._shouldBrake = 1

    def sniffConnection(self, connectionStatus):
        if connectionStatus == 1:
            self._connectionDownTime = 0
            self._lastConnection = time.time()
        else:
            self._connectionDownTime = time.time() - self._lastConnection


    def barkAtBattPercent(self):
        value = self._electricStats['batteryPercentageLevel']
        display = self._shouldDisplay["batteryPercentage"]

        if value in (1, 2, 3):
            self._pinHash['batteryLED'].toggleOn()
            if display == True:
                logger.critical("battery level at warning level" + str(value))

        if value == 3:
           logger.critical("recommend initiating recall")

        elif value == 2:
            logger.critical("recommend ending run soon")

        elif value == 1:
            logger.warning("battery level at warning level 1")


    def barkAtOverCurrent(self):
        value = self._electricStats['overCurrentLevel']
        display = self._shouldDisplay["overCurrent"]

        if value in (1, 2, 3):
            self._pinHash['warningLED'].toggleOn()
            if display == True:
                logger.critical("overCurrent at warning level " + str(value))

        if value == 2:
            logger.critical("current draw is much higher than expected")

        elif value == 3:
            logger.critical("too much current detected! Recommend SHUTDOWN")

    def barkAtUnderVoltage(self):
        value = self._electricStats['underVoltageLevel']
        if value in (1, 2, 3):
            self._pinHash['warningLED'].toggleOn()
            self._pinHash['batteryLED'].toggleOn()
            if self._shouldDisplay["underVoltage"] == True:
                logger.critical("underVoltage warning at level " + str(value))
                self._shouldDisplay['underVoltage'] = False

        if value == 3:
            logger.critical("initiating emergency shutdown")
            self.systemShutdown()

        elif value == 2:
            logger.critical('battery may be near death!')
            logger.critical('initating recall!')
            self.recall()

        elif value == 1:
            logger.warning("battery may be close to dying, please check")




    def barkAtOverVoltage(self):
        value = self._electricStats['overVoltageLevel']
        # OVERVOLTAGE
        if value == 3:
            self._pinHash['warningLED'].toggleOn()
            self._pinHash['motorRelay'].toggleOff()
            self._pinHash['ledRelay'].toggleOff()
            self._pinHash['laserRelay'].toggleOff()
            self._pinHash['relay4'].toggleOff()

            if self._shouldDisplay['overVoltage'] == True:
                logger.critical("overVoltage warning at level 3")
                logger.critical("motor, LEDs, and laser circuits turned off")
                logger.critical("recommend disabling watchdog and recalling mars")
        elif value == 2:
            self.recall()
            self._pinHash['warningLED'].toggleOn()
            if self._shouldDisplay['overVoltage'] == True:
                logger.critical("overVoltage at warning level 2")
                logger.critical("recommend enabling a recall")
        elif value == 1:
            self._pinHash['warningLED'].toggleOn()
            if self._shouldDisplay['overVoltage'] == True:
                logger.warning("overVoltage at warning level 1")
                logger.warning("recommend checking power supply")

    def barkAtConnection(self):
        if self._connectionDownTime >= self._levels.connection_timeout:
            self.recall()

    def recall(self):
        # tell mars to head backwards toward operator
        self._arduino.write(self._levels.recall_code)
        logger.critical("recall initiated")
        logger.critical("type 'watchdog off' to resume control")

    def disable(self):
        if self._enableWatchdog == False:
            logger.warning("watchdog is already disabled")
        else:
            self._enableWatchdog = True
            logger.critical("watchdog disabled")

    def enable(self):
        if self._enableWatchdog == True:
            logger.warning("watchdog is already enabled")
        else:
            self._enableWatchdog = True
            logger.critical("watchdog enabled")

