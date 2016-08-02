import json
import re

class Valmar():

    def __init__(self, config, mars):
        self._config = config
        self._commandPath = self._config.valmar.command_path
        self._telemetryPath = self._config.valmar.telemetry_path

        self._commands = {}
        self._telemetry = {}
        self._mars = mars


    def modifyCommandParameter(self, parameter, value):
        with open(self._commandPath),'r' as commandFile:
            self._commands = json.load(commandFile)
            self._commands[parameter] = value

        with open(self._commandPath, 'w') as commandFile:
            commandFile.write(json.dumps(self._commands))


    def updateTelemetry(self):
        with open(self._telemetryPath, 'r') as telemFile:
            self._telemetry = json.load(telemFile)
        return self._telemetry

