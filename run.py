import threading
import ConfigParser #used to read the 'settings.cfg' config file

from Mars import Mars


def run(configFile):
	configs = load_configs(configFile)

	devicePath = configs[0]
	masterIP = configs[1]
	currentBattery = configs[2]
	totalBattery = configs[3]
	recallPercent = configs[4]
	enableRecall = configs[5]
	shouldLog = configs[6]
	logName = configs[7]
	baudRate = configs[8]
	timeout = configs[9]
	trackLength = configs[10]

	m = Mars(masterIP = masterIP, devicePath = devicePath, baudRate = baudRate,\
		timeout = timeout, isLogging = shouldLog, logName = logName,\
		trackLength = trackLength, configFile = configFile, \
		currentBattery =currentBattery, totalBattery = totalBattery,\
		recallPercent = recallPercent, enableRecall = enableRecall, \
		  \
		)

	#run initalize function
	## program should quit if arduino isn't connected
	m.initalize()

##----- SETTING UP MULTIPLE THREADS HERE ------##

	dataThread = threading.Thread(target = m.repeat_read_print_save)
	inputThread =  threading.Thread(target = m.repeat_input)
	# pingingThread = threading.Thread(target = m.connection_check)

	try:
		dataThread.start() #read_print_save() thread
		inputThread.start() #repeat_input() thread
		# pingingThread.start() #connection_check() thread
	except Exception as e:
		print "error starting Multithreading ({})".format(e)
		print "program will terminate"
		raise SystemExit



def load_configs(configFile):
		try:
			 #THE NAME OF THE CONFIGURATION FILE
			configParser = ConfigParser.RawConfigParser()
			configParser.read(configFile)
			print ""

	### LOADING VARAIABLES FROM CONFIGURATION SETTINGS FILE ###
		#communications section
			devicePath = configParser.get('communications', 'arduinoPath')
			masterIP = configParser.get('communications', 'masterIP')
			print "arduino path = " + devicePath
			print "master ip address = " + masterIP
		#battery section
			currentBattery = configParser.getfloat('battery',\
				'currentBattery')
			totalBattery = configParser.getfloat('DO_NOT_CHANGE', \
				'totalBattery')

			print "{} percent battery remaining"\
			.format(str(100*currentBattery/totalBattery))


		#autonoumous_action Section
			recallPercent = configParser.getfloat('autonomous_action',\
				'recallPercent')
			enableRecall= configParser.getboolean('autonomous_action',\
				'enableRecall')
			print "recall percentage = {}".format(recallPercent)
			if enableRecall == True:
				print "recall enabled"
			elif enableRecall == False:
				print "recall disabled"
		#logging section
			shouldLog = configParser.getboolean('logging', 'shouldLog')
			logName = configParser.get('logging','logName')
			if shouldLog == True:
				print "logging enabled"
			elif shouldLog == False:
				print "logging disabled"
		#DO_NOT_CHANGE section
			baudRate = configParser.getint('DO_NOT_CHANGE', 'baudRate')
			timeout = configParser.getint('DO_NOT_CHANGE', 'timeout')
			trackLength = configParser.getfloat('DO_NOT_CHANGE', \
				'trackLength')
			print "baudRate = {}".format(baudRate)
			print "timeout time = {}".format(timeout)
			print "trackLength = {}".format(trackLength)


			settingsArray = [devicePath, masterIP,currentBattery,totalBattery,\
			recallPercent, enableRecall, shouldLog, logName, baudRate, timeout,\
			trackLength]

			print ""
			print "all settings loaded"
			return settingsArray

		except Exception as e:
			print ""
			print "error loading configs from 'settings.cfg' ({})".format(e)
			print ""
			print "check README or MARS manual for details on config settings"
			print 
			print "program will now terminate"
			print ""
			raise SystemExit

if __name__ == "__main__":
	run('settings.cfg')