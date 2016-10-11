# Copyright (c) 2016, Jeffrey Maggio and Joseph Bartelmo
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial 
# portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''
ark9719
6/17/2016
'''
import logging
import sys
import time
import os.path
import json
from collections import namedtuple
from System import System
sys.path.insert(0, '../shared')
from ColorLogger import initializeLogger 

marsLoggerName = 'mars_logging'
telemetryLoggerName = 'telemetry_logging'

#Assumes that the server handeled validation
def parseConfig(json_string):
    config = json.loads(json_string, object_hook=lambda configObject: namedtuple('X', configObject.keys())(*configObject.values()))
    return config

def initOutput(config, q = None, debugMode = False):
    """
    Create the output/timestamp directory for the files generated by this run (log/telemetry)
    :param config:
    :return:
    """
    t = time.localtime()
    timestamp = time.strftime('%b-%d-%Y_%H%M%S', t)
    logdir = config.logging.output_path + '/output/' + config.user_input.log_name + '-'+ timestamp + '/'
    if not os.path.exists(logdir):
        os.makedirs(logdir)

    # create debug file handler and set level to debug
    logLevel = logging.INFO
    if debugMode is True:
        logLevel = logging.DEBUG
    logger = initializeLogger(logdir, logLevel, marsLoggerName, sout = True, colors = True)
    telemetryLogger = initializeLogger(logdir, logging.INFO, telemetryLoggerName)

    if (os.path.isfile(logdir + config.user_input.log_name + '_machine_log.csv')):
        logger.debug("The telemetry output file you specified in the configuration file already exists.")
        logger.debug("The statistics from the previous reads will be overwritten if you don't specify a new file.")
        logger.debug("Do you wish to continue?")
        if(q is not None):
            answer = q.get()
        else:
            answer = raw_input("y/n:")
        if answer.lower() in ('n', 'no'):
            logger.debug("The program will terminate ")
            sys.exit()

    return timestamp


def run(json_string, q = None, watchDogQueue = None, marsRunningQueue = None, debugMode = False, ipAddress = None):
    config = parseConfig(json_string)

    timestamp = initOutput(config, q, debugMode)

    System(config, timestamp, q, watchDogQueue, marsRunningQueue, ipAddress)

def parseObject(jsonObject):
    with open(jsonObject) as f:
        json_string = "".join(line.strip() for line in f)

    return json_string


def displayUsage():
    '''
    Prints userfriendly usage of run.py
    '''
    print('Incorrect arguments, please specify a json string or object with which to load configuration')
    print('\tUsage:\trun.py [json_string|filename.json]')
    print('\t\t-d: Debug mode')

if __name__=='__main__':
    sys.argv.pop(0)#run.py
    
    debugEnabled = False
    #TODO: Use python cli module eventually
    if len(sys.argv) > 1 and sys.argv[1] == '-d':
        debugEnabled = True
    elif len(sys.argv) > 1 or len(sys.argv) == 0:
        displayUsage()
        sys.exit(1)
    json_config = sys.argv[0]

    if json_config.lower().endswith('.json'):
        with open(json_config) as f:
            configs = f.read().splitlines()
        configString =""
        for i in configs:
            configString = configString + i
        json_string = configString.replace(" ", "")
    else:
        json_string = ''.join(sys.argv)
    
    run(json_string, None, None, None, debugEnabled, None)

