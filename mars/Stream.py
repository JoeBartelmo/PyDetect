import logging
import subprocess

class Stream (object):

    def __init__(self, config, timestamp):
        self._streamCodes = ['low res stream', 'high res stream']
        self._config = config
        self._bitrate = 'None yet'
        self._resolution = 'None yet'
        self._timestamp = timestamp
        self._init = False
        self._indexPath = self._config.logging.index_path
        self._logPath = self._config.logging.output_path + 'output/' + self._config.user_input.log_name + '-' + self._timestamp + '/video'


    def refresh(self):
        """
        Refresh the stream via bash using the updated parameters
        :return:
        """
        if (self._init):
            self.close()
        logging.info('re-initializing steam with new inputs')
        newCall = 'nohup' + ' node '+ self._indexPath + ' -w '  + self._resolution[0] + ' -h ' + self._resolution[1] + ' -b ' \
                  + str(self._bitrate) + ' -f ' + self._logPath + ' &'
        logging.info(newCall)

        subprocess.call([newCall], shell=True)


    def issue(self, myCode):
        """
        Update the bitrate and resolution given the code from terminal and then refresh the stream
        :param myCode:
        :return:
        """
        rawBit = raw_input("What bitrate? (1-9)")
        if RepresentsInt(rawBit) and rawBit > 1 and rawBit < 10:
            self._bitrate = int(rawBit) * 1000 #converting Mb/s to Kb/s

        #update res 640x480
        if myCode == 'low res stream':

            logging.info('re-initializing steam with new inputs')
            self._resolution = ['640', '480']

        #update res 1280x960
        elif myCode == 'high res stream':

            logging.info('re-initializing steam with new inputs')
            self._resolution = ['1280', '960']

        #Refresh stream
        self.refresh()
        self._lastCommand = myCode


    def open(self):
        """
        Open stream with default parameters
        :return:
        """
        self._resolution = ['640', '480']
        self._bitrate = 4000
        self.refresh()
        self._init = True

    def close(self):
        """
        Close the stream
        :return:
        """
        if (self._init):
            logging.info('closing stream')
            subprocess.call(["node " + self._indexPath + " --close"], shell=True)
            self._init = False
        else:
            print("Stream not running")
            logging.info("Stream not running")

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
