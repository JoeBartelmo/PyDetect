import numpy as np
from matplotlib import pyplot as pyp
from matplotlib.backends.backend_pdf import PdfPages
import os
import fnmatch
import logging

class GraphUtility(object):

    def get_all_outputs(self):
        if not os.path.exists('output'):
            logging.warning('output folder does not exist, cannot get outputs')
            return []
        mtime = lambda f: os.stat(os.path.join('output', f)).st_mtime
        return list(sorted(os.listdir('output'), key=mtime))

    def generate_pdf(self, inputFolder = None):
        if inputFolder is None:
            if len(self.get_all_outputs()) is 0:
                return
            inputFolder = self.get_all_outputs()[0]
        inputFolder = 'output/' + inputFolder

        for f in os.listdir(inputFolder):
            if fnmatch.fnmatch(f, '*.csv'):
                filename = inputFolder + '/' + f
        
        if filename is None:
            log.warning('Could not find a *.csv file in ' + inputFolder)
            return
        
        with PdfPages('telemetry_graphs.pdf') as pdf:

            out = pdf.infodict()
            out['Title'] = 'Telemetry data graphs'
            out['Author'] = 'RIT Hyperloop'
            out['Subject'] = 'Graphs of MARS telemetry data'

            invals = np.genfromtxt(filename, names=True, delimiter=',')

            def plot_data(x, y, x_label, y_label, title):
                x=invals[x]
                y=invals[y]
                pyp.plot(x, y)
                pyp.xlabel(x_label) 
                pyp.ylabel(y_label) 
                pyp.title(title)
                pdf.savefig()
                pyp.clf()
            plot_data('TotalDistance', 'BatteryRemaining', 'Total Distance', 'Battery Remaining', 'Remaining Battery versus distance traveled')
            plot_data('BatteryRemaining', 'SystemVoltage', 'Battery Remaining', 'System Voltage', 'System voltage versus remaining battery')
            plot_data('RunClock', 'TotalDisplacement', 'Run Clock', 'Total Displacement', 'Total Displacement versus time elapsed')
            plot_data('RunClock', 'Speed', 'Run Clock', 'Speed', 'Speed versus time elapsed')
            plot_data('RunClock', 'BatteryRemaining', 'Run Clock', 'Battery Remaining', 'Remaining Battery versus time elapsed')
    
            pyp.close()