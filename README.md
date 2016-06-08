DESCRIPTION
:Name:
	Mars

:Purpose:	
	this class was made for the purposes of controlling and operating the
	M.A.R.S.(Mechanized Autonomous Rail Scanner) built by RIT Hyperloop Team
	to scan & identify debris and damage in SpaceX's Hyperloop test track. This 
	python code talks with an Arduino over a Serial connection to operate the 
	robot. A multidigit *Control Code*, typed in by a human operator, determines 
	exactly what MARS will do. 

	In addition, this class contains functions to acquire all data sent from the
	arduino, process it and provide the operator with a variety of telemetry 
	information.


:AUTHOR:
	Jeff Maggio
	RIT Hyperloop Imaging Team
	http://hyperloop.rit.edu/

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


________________________________________________________________________________
	CONTROL CODE CONVENTION
		Control codes are broken up into two formats, with each format
		controlling a different aspect of MARS. These formats are distinquished
		by an identifer placed at the beginning of the control code.

	:::MOTION CONTROL:::
		Placing an 'M' at the beginning of a 4 digit control code indicates to
		this software that the user wants to control the motion of MARS

		$FORMAT = 'MABCD'

		where:
			'A' is a binary operator to enable the Motor
					'-->(The motor must be enabled to move at all)
			'B' is a binary operator that defines direction (fwd, rev)
			'C' is a binary operator to engage the brake
			'D' is a decimal integer (0-9) that defines the speed
					'-->(Each integer roughly corresponds 1Mph or .5m/s)

			Examples
				"M1008" --> foward at 8mph
				"M1105" --> reverse at 5mph
				"M0010" --> motor disabled, brake engaged
				"J1108" --> Wrong identifier 'J', code is not processed

	:::LED CONTROL:::
		Placing an 'L' at the beginning of a 4 digit control code indicates to
		this software that the user wants to control the luminance of MARS' LEDS

		$FORMAT$ = 'LX'

		where:
			'X' is a decimal integer (0-9) that defines the brightness on a
			linear scale.
________________________________________________________________________________
	

FUNCTIONS

	main()::  
********ONLY FUNCTION THAT NEEDS TO RUN NEEDED WHEN OPERATING M.A.R.S.**********
		runs the initiatalization procedure
		sets up multiple threads to allow simultaneous DAQ, input and reactions
				utilizes:
					initialize()
					repeat_rps()
					repeat_input()
					connection_check()
				returns:
					NONE
	============================================================================
	initalize()::
		checks if arduino is properly connected, flushes Serial buffers and 
		starts the clock
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
		current data
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

--------------------------------------------------------------------------------