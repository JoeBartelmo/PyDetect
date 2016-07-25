# PyDetect
Feature Detection

### Dependencies
  - OpenCV - http://opencv.org/downloads.html
  - Python - https://www.python.org/downloads/
  - NodeJS - https://nodejs.org/en/download/
  - VLC    - http://www.videolan.org/vlc/index.html

> In addition we could be using Cython or some other utility to convert the 
> Python to some lowerlevel programming language for better optimization;
> Unknown currently as to whether or not this will be done.

### Workflow
| Name   | Position |
|----------|:-------------:|
| Joe Bartelmo|  Dev Lead | 
| Nathan Dileas | Developer | 
| Tyler Kuhns | Tech Lead  | 
| Jeff Maggio | Tech Lead | 
| Ryan Hartzell | QA / Automation | 
    


### Version
1.0.1
=======
:Purpose:	
	this software was made for the purposes of controlling and operating the
	M.A.R.S.(Mechanized Autonomous Rail Scanner) built by RIT Hyperloop Team
	to scan & identify debris and damage in SpaceX's Hyperloop test track. This 
	python code talks with an Arduino over a Serial connection which in turn
	controls the motors on Mars. 

	In addition, this code includes a data aquistion system which compiles and 
	processes data sent from the arduino to provide the operator with real-time
	telemetry on the status of the robot.

	A multicharacter *Control Code*, typed in by a human operator, 
	determines exactly what MARS will do. 


:AUTHOR:
	Jeff Maggio
	RIT Hyperloop Imaging Team
	http://hyperloop.rit.edu/team.html

	Feel free to contact this developer at any point in time
	email: jxm9264@rit.edu | jmaggio14@gmail.com
	phone: 1-513-550-9231


:UPDATED:
	last updated: June 11, 2016

	

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



					-----------------------------------------
					|        CONTROL CODE CONVENTION        |
					-----------------------------------------
		Control codes are broken up into two formats, with each format
		controlling a different aspect of MARS. These formats are distinquished
		by an identifer placed at the beginning of the control code.

	# MOTION CONTROL
		-Placing an 'M' at the beginning of a 4 digit control code indicates 
		that the user wants to control the motion of MARS


		$ FORMAT ==> MABCD
		
		where:
			'M' is the motion identifer "M" 
			'A' is a binary operator to enable the Motor
					'-->(The motor must be enabled to move at all)
			'B' is a binary operator that defines direction (fwd, rev)
			'C' is a binary operator to engage the brake
			'D' is a decimal integer (0-9) that defines the speed
					'-->(Each integer roughly corresponds 1Mph or .5m/s)

			Examples
				M1008 --> foward at 8mph
				M1105 --> reverse at 5mph
				M0010 --> motor disabled, brake engaged (unconditional stop)
				J1108 --> Unknown identifier 'J', code is not processed

	# LED CONTROL
		-Placing an 'L' at the beginning of a 1 character control code indicates
		that the user wants to define the luminance of MARS' LEDS

		$ FORMAT ==> LX

		where:
			'L' is the LED identifier "L"
			'X' is a decimal integer (0-9) that defines the brightness on a
			linear scale.

			Examples
				L0 --> LEDs off
				L3 --> LEDs on 30percent strength
				L9 --> LEDs on full strength
				Q9 --> Unknown identifier 'Q', code is not processed


   					-----------------------------------------
					|         DATA ARRAY CONVENTION         |
					-----------------------------------------

the function 'daq()' in the Mars class compiles and processes data returned from
the arduino and generates the following telemetry array. 

This telemetry array was built to be used to be sent to the master computer 
manned by the robot operator which will then display it to the operator and 
corrolate the data with our FOD detection algorithms. This would allow us to 
observe trends in FOD detection as a function of speed, distance, time, etc. 

However, this data can also be used interpreted by the reaction and autonomous
functionality of Mars to enable features such as automatic braking, or automatic
recall if an appropriate threshold in the data is reached.

An example of this might be having the Mars robot automatically return if it
loses network connection or if it's battery reaches critical levels. 


All telemetry is logged aboard Mars for later reference/analysis


.............................  TELEMETRY ARRAY  ................................

[Clock, distance, speed, power, battery, integTime, connection, rpm, sysV, sysI
   0         1      2      3       4         5           6       7     8     9

motionCommand, ledCommand, streamCommand]
      10            11           12
...............................................................................


0) Clock: (seconds)
	Time since the Mars object was substantiated--> usually the time since the 
run() function was called

1) distance: (meters)
	Displacement from the point of origin down the tube, this value is
approximate and may be off by as much as much 30 meters or more.

2) speed (meters/second)
	Speed of Mars estimated from the rpm date provided by the motor encoder. 
Expected this value to be within .05 of actual speed, but may be off by much
more if Mars is stuck or lacks good traction.

3) power (Watts)
	Power usage of Mars. As of June 11 2016, the accuracy of this measurement 
has not been determined. However it is expected that it will be within 5%

4) Battery (Percentage)
	Battery remaining aboard Mars. As of June 11 2016, the accuracy of this 
measurement has not been determined. However it is reccomended that the operator
err on the side of caution and not use Mars below 30%.
			'--> this is calculated by integrating power and subtracting
			that value from the battery level. NOT BY DIRECT MEASUREMENT

5) Integration Time (seconds)
	The time between samples from the arduino, this value is used to calculate
the distance and battery remaining. It is provided in this array for the
purposes of error checking and ensuring data accuracy

6) Connection status (boolean)
	a boolean indicating whether or not Mars is still connected to the 
operator's computer. This can be used to trigger Mars' autonomous actions 
or simply logged to indicate to the operator 

7) RPM (rpm)
	Raw data from the motor's encoder indicating the speed of the motor before
any gearing. This is data is used to calculate linear speed and distance. It is
provided in this array for the purposes of error checking and ensuring data
accuracy

8) SysV (Volts)
	Voltage coming off the batteries. It is currently used to calculate power
usage, and estimate battery remaining. 
	This can be used as a direct measurment of battery remaining. However,
thorough testing must occur before this can accurately be estimated. This
testing has been planned, but not completed as of June 11, 2016. 


9) SysI (Amps)
	Current currently used by Mars. It is currently used to calculate power
usage, and thus battery remainging. It could also be used to trigger an over 
current warning and shutdown or restrict Mars as a safetly feature. 




FUNCTIONS

	============================================================================
	initalize()::
		checks if arduino is properly connected, flushes Serial buffers and 
		starts the runClock
				utilizes:
					NONE
				returns:
					NONE
	============================================================================
	repeat_rps()::
		continuously runs the rps() function
				utilizes:
					rps()
				returns:
					NONE
	============================================================================					
	repeat_input()::
		continuously runs the controller_input() function
				utilizes:
					controller_input()
				returns:
					NONE
	============================================================================
	connection_check()::
		continuously checks the connection with the controller's computer and 
		tells Mars to initiate autonomous mode if that connection is lost
				utilizes: 
					ping_control()
				returns:
					NONE
	============================================================================
	ping_control()::
		this function pings the controller's computer once and returns a 
		boolean value indictating whether connection is still good
				utilizes:
					NONE
				returns:
					connection status (boolean)					
	============================================================================
	daq():: 
		This function reads data from the arduino and then calculates a variety 
		of other values derived from it such as speed, power, batteryRemaining. 
				utilizes: 
					serial_readline()
					estimated_speed()
					estimated_power()
					distance_traveled()
					batteryRemaining()
				returns:
					telemetry array (list)					
	============================================================================
	make_pretty():: 
		this functions takes the dataArray from daq and returns a string with 
		all data formatted in a more human-readable manner 
				utilizes: 
					NONE
				returns:
					human-readable telemetry (string)					
	============================================================================
	serial_readline()::
		Reads the telemetry sent from the arduino
				utilizes:
					NONE
				returns:
					a single line of data sent from arduino (string)		
	============================================================================
	rps()::
		Reads, Prints and Saves the telemetry sent from the Arduino
		also displays a human-friendly format in the terminal for an operator
				utilizes:
					daq()
					make_pretty()
				returns:
					NONE		
	============================================================================
	controller_input()::
		checks if control code is valid and sends control code to the arduino
				utilizes:
					arduino_write()
					input_check()
				returns:
					NONE
	============================================================================
	arduino_write(controlCode)::
		writes the controlCode to the arduino over the Serial buffers
				utilizes:
					NONE
				returns:
					NONE					
	============================================================================
	input_check(userInput)::	
		checks the userInput to see if it follows Control Code Convention
				utilizes:
					NONE
				returns:
					whether or not user input qualifies (boolean)						
	============================================================================
	flush_buffers()::	
		flushes serial buffers
				utilizes:
					NONE
				returns:
					NONE						
	============================================================================
	default_forward()::
		simply sends a control code to the arduino that will make MARS travel
		forward at 40percent speed
				utilizes:
					NONE
				returns:
					NONE						
	============================================================================
	default_backward()::
		simply sends a control code to the arduino that will make MARS travel
		backward at 40percent speed
				utilizes:
					NONE
				returns:
					NONE						
	============================================================================
	stop()::
		simply sends a control code to the arduino that will make MARS stop 
		unconditionally
				utilizes:
					NONE
				returns:
					NONE						
	============================================================================
	time_since_start()::
		returns the time since initalization began
				utilizes:
					NONE
				returns:
					time since initalization (float)						
	============================================================================
	estimated_speed()::
		estimates the current speed of MARS based off of RPM data
				utilizes:
					NONE
				returns:
					estimated speed in m/s (float)
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
	battery_remaining(power *optional*, time *optional*)::
		if the user inputs power or time data, then this function will calculate
		how much energy remains in the batteries. otherwise ths will return the
		last calculated battery status
				utilizes:
					NONE
				returns:
					percentage of battery remaining (float)

