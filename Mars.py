import serial #used to communicate with the arduino over a serial bus
import os 
import time #used for the runclock and real time integrators
import re #used primarily to split DAQ strings and generate an array of data
import math #for math
import csv #used to generate a machine log
import pyping #used to ping master controller
import logging #used to dynamically log and filter the console output

class Mars(object):

	"""
DESCRIPTION
:Name:
	Mars

:Purpose:	
	this class was made for the purposes of controlling and operating the
	M.A.R.S.(Mechanized Autonomous Rail Scanner) built by RIT Hyperloop Team
	to scan & identify debris and damage in SpaceX's Hyperloop test track. This 
	python code talks with an Arduino over a Serial connection to operate the 
	robot. A multicharacter *Control Code*, typed in by a human operator, 
	determines exactly what MARS will do. 

	In addition, this class contains functions to acquire all data sent from the
	arduino, process it and provide the operator with a variety of telemetry 
	information.


:AUTHOR:
	Jeff Maggio
	RIT Hyperloop Imaging Team
	http://hyperloop.rit.edu/team.html

	Feel free to contact me at
	email: jxm9264@rit.edu | jmaggio14@gmail.com
	phone: 1-513-550-9231

:UPDATED:
	last updated: June 3, 2016
	

:DISCLAIMER:
This source code is provided "as is" and without warranties as to performance 
or merchantability. The author and/or distributors of this source code may 
have made statements about this source code. Any such statements do not 
constitute warranties and shall not be relied on by the user in deciding 
whether to use this source code.

This source code is provided without any express or implied warranties 
whatsoever. Because of the diversity of conditions and hardware under which 
this source code may be used, no warranty of fitness for a particular purpose 
is offered. The user is advised to test the source code thoroughly before 
relying on it. The user must assume the entire risk of using the source code.

			------------------------------------------------
			|  CHECK README OR USER MANUAL FOR MORE INFO   |
			------------------------------------------------

"""
	def __init__(self, masterIP, devicePath, baudRate, timeout,\
		isLogging, logName, trackLength, configFile, enableRecall,\
		recallPercent, arduino = None, initializeOkay = None, tStart = None,\
		 currentBattery = None,	totalBattery = None, distanceTraveled = 0,\
		  displacement = 0, currentSpeed = 0, isConnected=None, \
		   lastMotionCode = None, lastLedCode = None, lastStreamCode = None):
		self._masterIP =  masterIP #IP address of the control comp
		self._arduino = arduino #used in initialize(), NoneType for now
		self._initializeOkay = initializeOkay #has initiatalization occured?
		self._devicePath = devicePath #location of control arduino on machine
		self._baudRate = baudRate #baud rate of serial connectiom, usually 9600
		self._timeout = timeout #time in sec to listen for telemetry b4 error
		self._isLogging = isLogging #boolean to deterime if telemetry is logged
		self._logName = logName #name of the log
		self._isConnected = isConnected #have we lost connection with control?
		self._currentBattery = currentBattery #current updated battery remaining
		self._totalBattery = totalBattery#original battery size
		self._distanceTraveled =  distanceTraveled # distance traveled so far
		self._displacement = displacement #the linear displacement down the Tube
		self._currentSpeed = currentSpeed # last recorded speed of MARS
		self._configFile = configFile #name of the settings file
		self._recallPercent = recallPercent #point at which Mars automatically
											##recalls itself
		self._trackLength = trackLength #length of the track, used for recall
		self._enableRecall = enableRecall #whether or not to enable recall func


		self._lastMotionCode = lastMotionCode #the last user input Motion code
		self._lastLedCode = lastLedCode #the last user input LED code
		self._lastStreamCode = lastStreamCode #the last user input Stream code


	
	def initalize(self):
		"""
	============================================================================		
	checks if arduino is properly connected, flushes Serial buffers and 
	starts the runClock.

	MARS MUST BE INITATLIZED BEFORE ANY ACTION CAN OCCUR!
			utilizes:
				NONE
			returns:
				NONE
	============================================================================
		"""			
		self.lap("beginning initialization...")
		# print "loading configs from {}".format(self._configFile)
		# self.load_configs() #loading the configurations from settings

		self.lap("checking if arduino is connected...")
		#check if arduino is connected on device path
		## exit program if connection failure
		try:
		# SELF._ARDUINO TYPE CHANGE: None-->Serial Object
			self._arduino = serial.Serial(self._devicePath,self._baudRate)

		except serial.serialutil.SerialException:
			self.lap("arduino not connected or device path wrong")
			self.lap("check MARS user manual for details")
			self.lap("unable to continue, program will now terminate")
		
			raise SystemExit

		self.lap("arduino connected")


		self.lap("flushing serial buffers...")

		self._arduino.flushInput() #flushing the serial input buffer
		self._arduino.flushOutput() #flushing the serial output buffer

		self.lap("Initialization complete")
		self._initializeOkay = True



		#BEGINNING RUN CLOCK --> tStart used to calculate runclock
		global tStart
		tStart = time.time()
		global integrationTime
		integrationTime = 0.0


		time.sleep(1)
		global tLastRead
		tLastRead = self.time_since_start()
		self.lap("")

		

	def repeat_read_print_save(self):
		"""
	============================================================================		
	repeat_read_print_save()::
		continuously runs the read_print_save() function. Which continuously
	reads, prints and saves all DAQ system data
				utilizes:
					read_print_save()
				returns:
					NONE
	============================================================================

		"""
		while True:
			self.read_print_save()


	def repeat_input(self):
	"""
	============================================================================	
	repeat_input()::
		continuously runs the controller_input() function
				utilizes:
					controller_input()
				returns:
					NONE
	============================================================================
	"""	
		while True:
			self.controller_input()


	def connection_check(self):
	"""
	============================================================================
	connection_check()::
		continuously checks the connection with the controller's computer and 
		tells Mars to initiate autonomous mode if that connection is lost
				utilizes: 
					ping_control()
				returns:
					NONE
	============================================================================
	"""
		ipToCheck = self._masterIP
		while True:
			time.sleep(5)
			connectionStatus = self.ping_control(ipToCheck)
			if connectionStatus == False:
				self._isConnected = False
				# self.autonomous(engage = True) #if connection is lost,\
											   ## then enter autonomous mode
				# print "engaging autopilot"s
			else: 
				# self.autonomous(engage = False)


	def ping_control(self, ipToCheck):
	"""
	============================================================================
	ping_control()::
		this function pings the controller's computer once and returns a 
		boolean value indictating whether connection is still good
				utilizes:
					NONE
				returns:
					connection status (boolean)					
	============================================================================
	"""
		r = pyping.ping(self._masterIP)

		if r.ret_code == 0: 
			#master is still reachable
			return True
		else:
			#master is not reachable, connection is lost
		    return False



	def daq(self):
	"""
	============================================================================
	daq():: 
		This function reads data from the arduino and then calculates a variety 
		of other values derived from it such as speed, power, batteryRemaining. 
				utilizes: 
					serial_readline()
					estimated_speed()
					estimated_power()
					displacement()
					distance_traveled()
					batteryRemaining()
				returns:
					telemetry array (list)		
	============================================================================
	"""
	#auto-initialize if initialization has not been completed
		if self._initializeOkay == False:
			self.initalize() 

		try:
			rawInput = self.serial_readline() #reading Serialdata
			rawArray = re.split(',',rawInput)
	#independent data (raw from arduino)
			rpm = rawArray[0]
			sysV = rawArray[1]
			sysI = rawArray[2]
			sysI = sysI[0:len(sysI)-4] # new line characters '\r\n' popped up 
									   ## this just gets rid of them
	#first set dependent (calculated based off of raw data)
			speed = self.estimated_speed(rpm) #speed in m/s
			power = self.estimated_power(sysV, sysI) #power in Watts

	#second set dependent (calculated based off of above set)
			distance, distanceTraveled = self.distance_traveled(speed) #in Meters
			displacement, totalDisplacement = self.displacement(speed) #in Meters 
			batteryRemaining = self.battery_remaining(power) 

	#Connection and clock data. Generated on this machine. 
			global integrationTime 
			integrationTimeRounded = round(integrationTime, 4)
			runClock = round(self.time_since_start(), 4)
			isConnected = self._isConnected


	#Last commands used for operator reference
			mCode = self._lastMotionCode
			lCode = self._lastLedCode
			sCode = self._lastStreamCode


	#compiling all data into list for ease of access
			telemetryArray = [runClock,totalDistplacement, distanceTraveled,\
			speed,power, batteryRemaining,integrationTimeRounded,isConnected,\
			rpm, sysV, sysI, mCode, lCode, sCode]

		except Exception as e:
			self.lap("unable to acquire data due to {}".format(e))
			self.lap("attemting to correct...")
			self.daq() 


		return telemetryArray

	
	def make_pretty(self, telemetryArray):
	"""
	============================================================================
	make_pretty():: 
		this functions takes the telemetryArray from daq and returns a string with 
		all data formatted in a more human-readable manner 
				utilizes: 
					NONE
				returns:
					human-readable telemetry (string)					
	============================================================================
	"""
		runClock = telemetryArray[0]
		distance = telemetryArray[1]
		speed = telemetryArray[2]
		power = telemetryArray[3]
		battery = telemetryArray[4]
		integTime = telemetryArray[5]
		connectionStatus = telemetryArray[6]
		motorRpm = telemetryArray[7]
		systemVoltage = telemetryArray[8]
		systemCurrent = telemetryArray[9]
		mCode = telemetryArray[10]
		lCode = telemetryArray[11]
		sCode = telemetryArray[12]

		minutes,seconds = divmod(runClock, 60)

		minSecString = str(int(minutes)) + ":" + str(int(seconds)) + "{  "
		distanceString = str(distance)+"meters, "
		speedString = str(speed) + "m/s, "
		powerString = str(power) + "Watts, "
		batteryString = str(battery) + "%, "
		#integration time isn't needed for operator
		if connectionStatus == True:
			connectionString = "Connected"
		else:
			connectionString = "Disconnected"

		#raw data off of Arduino
		rpmString = str(motorRpm) + "rpm, "
		voltageString = str(systemVoltage) + "V, "
		currentString = str(systemCurrent) + "A, "

		#last commands set by operator
		mCodeString = 'motion command: ' + mCode
		lCodeString = 'led command: ' + lCode
		sCodeString = 'stream command: ' + sCode


		operatorString = minSecString + distanceString + speedString + \
		powerString + batteryString + rpmString + voltageString + \
		currentString +connectionString + mCodeString + lCodeString + \
		sCodeString + '\r\n'

		return operatorString



	def serial_readline(self):
"""
	============================================================================
	serial_readline()::
		Reads the telemetry sent from the arduino
				utilizes:
					NONE
				returns:
					a single line of data sent from arduino (string)		
	============================================================================
"""
		#only attempt to read if initialization has occured
		if self._initializeOkay == False: 
			self.initalize()

		#begining a waiting clock for timeout
		waitStart = time.time()
		waitTime = time.time() - waitStart
		timeout = self._timeout

#______________________Pulling Data from Arduino_______________________________#
		#only readline if there is data in the buffer 
		## continue checking buffer only if waiting time is less than timeout
		while self._arduino.inWaiting() == 0:
			if waitTime < timeout:
				waitTime =  time.time() - waitStart
			elif waitTime >= timeout:
				self.lap("no data coming from arduino before timeout")
				self.lap("ending program, check arduino or timeout duration")
				self.lap("attempting re-initialization...")
				self.initialize()
		else:
			time.sleep(.001) #added short delay just in case data was in transit
			serialData = self._arduino.readline()#read telemetry sent by Arduino
			self._arduino.flushInput() #flushing in case there was a buildup
#______________________________________________________________________________#
			#finding integration time
			##resetting the time since last read
			global integrationTime
			global tLastRead

			integrationTime = self.time_since_start() - tLastRead
			tLastRead = self.time_since_start() 

			return serialData



	def read_print_save(self): #read_print_save: Read, Print and Save
	"""
	============================================================================
	read_print_save()::
		Reads, Prints and Saves the telemetry sent from the Arduino
		also displays a human-friendly format in the terminal for an operator
				utilizes:
					daq()
					make_pretty()
				returns:
					NONE		
	============================================================================
	"""
		daqData = self.daq()
		operatorString = self.make_pretty(daqData)

		self.lap(daqData,0)
		self.lap(operatorString,1)




	def controller_input(self):
	"""
	============================================================================
	controller_input()::
		checks if control code is valid and sends control code to the arduino
				utilizes:
					arduino_write()
					input_check()
				returns:
					NONE

	============================================================================
	"""
		#ask for control code input from user
		controlCode = raw_input("LED or motion control code: ")
		#check if control code is within parameters
		codeOkay,codeType = self.input_check(controlCode)


	#RECORDING THE LAST CONTROL CODE COMMAND --> this feeds into telemetry array
		if codeType == 'M':
			self._lastMotionCode = controlCode
		elif codeType == 'L':
			self._lastLedCode = controlCode
		elif codeType == 'S':
			self._lastStreamCode = controlCode


		if codeOkay == True:
			self.arduino_write(controlCode) #write code to arduino
			self.lap("")
			self.lap(controlCode + " inputed") #print control code for reference
			self.lap("code is valid")
			self.lap("")
		else:
			self.lap("")
			self.lap(controlCode + " inputed")
			self.lap("code is INVALID")
			self.lap("check MARS user manual for specifics on code convention")
			self.lap("")

	

	def arduino_write(self, controlCode):
	"""
	============================================================================
	arduino_write(controlCode)::
		writes the controlCode to the arduino over the Serial buffers
				utilizes:
					NONE
				returns:
					NONE					
	============================================================================
	"""	
		#only send code if initialization has occured
		if self._initializeOkay == False:
			self.initalize()

		self._arduino.write(controlCode) #send control code to arduino



	
	def input_check(self, userInput):
		"""
	============================================================================
		This function checks the controlCode input and checks if it is within
		the convention described above at the begining of the primary docstring.

		It uses a complex series of nested if-statements to check the code.

		This function could probably be remade in a more straightforward manner,
		an option might be to use dictionaries or nested lambda functions 
				'--> ie. the python equivalent of a switch statement.

		possible alternatives:
					https://code.activestate.com/recipes/410692/

	============================================================================
		"""
		codeType = None

		codeIdentifier = userInput[0]
		codeIdentifier = codeIdentifier.upper()

		#____TESTING IF THE IDENTIFER IS WITHIN PARAMETERS____#

	#---------------BEGIN LED CODE CHECK----------------------#
		if codeIdentifier == "L":
			#____testing the length of the input____#	
			if len(userInput) == 2:
				lengthOkay = True
			else:
				lengthOkay = False

			#===testing if the second value is a digit===#
			if userInput[1].isdigit() == True:
				valuesOkay = True
			else:
				valuesOkay = False
			

			#____Compiling the output____#	
			if lengthOkay == True and valuesOkay == True:
				testResult = True
				codeType = 'L'
			else:
				testResult = False
				

	#---------------BEGIN MOTOR CODE CHECK----------------------#
		elif codeIdentifier == "M":
		#____testing the length of the input____#	
			if len(userInput) == 5:
				lengthOkay = True
			else:
				return False #--> return false is the input isn't right length
		#____checking if the enable value is binary____#
			if userInput[1] == "0" or userInput[1] == "1":
				enableOkay = True
			else:
				enableOkay =  False
		#____checking if the reverse value is binary____#
			if userInput[2] == "0" or userInput[2] == "1":
				reverseOkay = True
			else:
				reverseOkay =  False
		#____checking if the brake value is binary____#
			if userInput[3] == "0" or userInput[3] == "1":
				brakeOkay = True
			else:
				brakeOkay =  False
		#____checking if the speed value is decimal____#
			speedValue = userInput[4]
			if speedValue.isdigit() == True:
				speedOkay = True
			else:
				speedOkay = False

			a = lengthOkay
			b = enableOkay
			c = reverseOkay
			d = brakeOkay
			e = speedOkay

			if a==True and b==True and c==True and d==True and e==True:
				testResult = True
				codeType = 'M'
			else:
				testResult = False

		else:
			self.lap("control code must have an identifier")
			self.lap("------------------------------------")
			self.lap("check MARS user manual for specifics")
			self.lap("------------------------------------")			
			testResult = False
#######DEBUGGING CODE ####################

		return testResult,codeType
		# return True
		

	def flush_buffers(self):
	"""
	============================================================================
	flush_buffers()::	
		flushes serial buffers
				utilizes:
					NONE
				returns:
					NONE						
	============================================================================

	"""
		"""this function just flushes the Serial buffers"""
		#only attempt to flush if initialization has occured
		if self._initializeOkay == False: 
			self.initalize()

		self.lap("flushing serial buffers...")	
		self._arduino.flushInput() #flushing the serial input buffer
		self._arduino.flushOutput() #flushing the serial output buffer



	def default_forward(self):
		"""
	============================================================================
	default_forward()::
		simply sends a control code to the arduino that will make MARS travel
		forward at 40percent speed
				utilizes:
					NONE
				returns:
					NONE						
	============================================================================

		"""
		defaultForwardCode = "M1104"
		self.arduino_write(defaultForwardCode)



	def default_backward(self):
		"""
	============================================================================
	default_backward()::
		simply sends a control code to the arduino that will make MARS travel
		backward at 40percent speed
				utilizes:
					NONE
				returns:
					NONE						
	============================================================================

		"""

		defaultBackwardCode = "M1004"
		self.arduino_write(defaultBackwardCode)



	
	def stop(self):
		"""
	============================================================================
	stop()::
		simply sends a control code to the arduino that will make MARS stop 
		unconditionally
				utilizes:
					NONE
				returns:
					NONE						
	============================================================================

		"""

		fullStopCode = "M0010"
		self.arduino_write(fullStopCode)



	def time_since_start(self):
	"""
	============================================================================
	time_since_start()::
		returns the time since initalization began. ie the runClock
				utilizes:
					NONE
				returns:
					time since initalization (float)						
	============================================================================

	"""
		global tStart
		currentTime = time.time()

		tSinceStart = currentTime - tStart
		return tSinceStart



	def estimated_speed(self, rpm):
		"""
	============================================================================		
		This function guesses how fast Mars is going based on the lastest RPM
		data from the DAQ. 

		It does not take into account any other factors or forces, as a result
		this is an ESTIMATED SPEED, not a real speed

		this conversion is will only work for the current generation of MARS and
		is a function of this equation
			speed in mph ~= rpm/221
			speed in m/s ~= (rpm/221)*0.44704

				utilizes:
					NONE
				returns:
				estimated speed in m/s (float)
	============================================================================

		"""
		rpm = float(rpm) #rpm must be a float
		estMps = (rpm/221.0)*0.44704 #estimated SPEED in M/S

		returnEstMps = round(estMps, 1)
		self._currentSpeed = returnEstMps
		return returnEstMps




	def estimated_power(self, sysVoltage, sysCurrent):
		"""
	============================================================================
	estimated_power()::
		estimates the current power usage of mars based off of voltage and 
		current data.
			P = V * I
				utilizes:
					NONE
				returns:
					estimated power usage in Watts (float)	
	============================================================================

		"""
		sysVoltage = float(sysVoltage)
		sysCurrent = float(sysCurrent)
		estPower = sysVoltage * sysCurrent

		powerReturned = round(estPower, 2)
		return powerReturned



	def battery_remaining(self,power=None, time = None):
		"""
	============================================================================
	battery_remaining(power *optional*, time *optional*)::
		if the user inputs power or time data, then this function will calculate
		how much energy remains in the batteries. otherwise ths will return the
		last calculated battery status
				utilizes:
					NONE
				returns:
					percentage of battery remaining (float)
	============================================================================
	"""
		if time == None:
			time = integrationTime 
	########^^^^^^^^FIX THIS ONCE DEBUGGING IS COMPLETE^^^^^^^^###########

		if power != None:
			joulesUsed  = float(power) * time
			whrUsed = joulesUsed/3600.0 #converting Joules to Watt*hours

			self._currentBattery = self._currentBattery - whrUsed
			#subtracting energy used from battery total

		battPercent = self._currentBattery/self._totalBattery * 100.0
		battPercentReturned = round(battPercent, 1)

		return battPercentReturned



	def distance_traveled(self, speed, time=None):
	"""
	============================================================================
	distance_traveled()::
		returns the estimated distance traveled by mars. If the user feed this 
		function a time parameter, then this will calculate the new distance
		based on the current speed and time given. Otherwise it will return the
		last calculated distance traveled by Mars.
				utilizes:
					NONE
				returns:
					distance traveled by Mars in meters (float)
	============================================================================
	"""
		if time == None:
			time = integrationTime

		intervalDistance = abs(speed) * time
		self._distanceTraveled = self._distanceTraveled + intervalDistance
		totalDistance = self._distanceTraveled
		
		intervalDistanceRounded = round(intervalDistance,1)
		totalDistanceRounded = round(totalDistance, 1)

		return intervalDistanceRounded,totalDistanceRounded




	def displacement(self, speed, time=None):
	"""
	============================================================================
	distance_traveled()::
		returns Mars' estimated displacement down the tube. If the user feeds 
		this function a time parameter, then this will calculate the new 
		distance based on the current speed and time given. Otherwise it will 
		return the last calculated displacement traveled by Mars.
				utilizes:
					NONE
				returns:
					total linear displacement of Mars in meters (float)
	============================================================================
	"""
		if time == None:
			time = integrationTime

		intervalDisplacement = speed * time
		self._displacement= self._displacement + intervalDisplacement
				# '--> updating the object attribute
		totalDisplacement = self._displacement

		intervalDisplacement = round(intervalDisplacement,1)
		totalDisplacement = round(totalDistance, 1)
		#rounding to make it more human readable--> we don't even have that much
		##acurracy to begin with
		return intervalDisplacement,totalDisplacement



	def lap(self, logData, logType = None, logLevel=None):#lap --> Log And Print
		# 0 indicates raw telemetry
		# 1 indicates human readable telemetry
		# 2 indicates a status log
		
		try:
		 #RAW TELEMETRY
			if logType == 0: 
				fileName =  'logs/'+ self._logName + '_machine_log.csv'
				with open(fileName, 'a') as rawFile:
					rawWriter = csv.writer(rawFile)
					rawWriter.writerow(logData)
			
			#HUMAN-READABLE TELEMETRY
			elif logType == 1:
				fileName = 'logs/'+ self._logName + '_operator_log.txt'
				with open(fileName,'a') as operatorFile
					operatorFile.write(logData+'\r\n') 

			#STATUS LOG
			elif logType == 2:
				fileName='logs/'+ self._logName+'_status_log.txt'
				with open(fileName,'a') as statusFile
					statusFile.write(logData+'\r\n') 
					print statusMessage

		except Exception as e:
			print "unable to log data because: \r\n {}".format(e)

	## There are automatically 3 logs saved
	### One DAQ log formatted in a more human-friendly way
	#### and another DAQ log in a machine-readable '.csv'
	##### there is also a status log, but this is saved intermittently 
	###### as part of self.lap() --> (log and print)











	# def autonomous_action(self, engage = True):
	# 	batteryRemaining = self.batteryRemaining
	# 	if engage == True:
	# 		if batteryRemaining + 5.0 >= self._recallPercent:


	# 		#checking battery percentage. Is automatic Recall needed? 







# if __name__ == "__main__":
# 	m = Mars()
# 	try:
# 		m.main()
# 	except KeyboardInterrupt:
# 		m.stop()














