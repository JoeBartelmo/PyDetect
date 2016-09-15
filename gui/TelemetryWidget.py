import json
import Tkinter as tk
from Queue import Queue, Empty
import sys

from Threads import TelemetryThread

class TelemetryWidget(tk.Frame):
    """
    Shows structured output from valmar.

    Args:
        parent: parent window
        client_queue_in: get info from the client
    """
    def __init__(self, parent, client_queue_in):
        tk.Frame.__init__(self, parent, bd=2, relief='groove')
        self.parent = parent

        #contains all pretty views
        self.translationKeys = self.load_keys('../gui/telemetryTranslation.json')
        self.labels = {}
        self.values = {}
        self.telemetry_data = {}

        #instantiate ui
        self.set_telemetry_ui()

        #start grabbing data
        self.telem_queue = client_queue_in
        self.tthread = TelemetryThread(self, client_queue_in)
        self.update_telemetry_loop()

    def set_telemetry_ui(self, json_object = None):
        """ Initialize visual elements of widget. """
        for key, val in self.translationKeys.iteritems():
            # label
            if val['display']:
                if key not in self.labels:
                    #update label row
                    self.labels[key] = tk.Label(self, text=val['friendly_name'], padx=5, pady=5, bd=2, justify='left', relief='ridge', width=18)
                    self.labels[key].grid(row=val['display_order'], column=0, sticky='w')
                    #update value column
                    self.values[key] = tk.Label(self, padx=5, pady=5, width=18, anchor='w')
                    self.values[key].grid(row=val['display_order'],column=1, sticky='w')
                    self.telemetry_data[key] = ''
                
        self.update()
       
    def set_telemetry_data(self, telemetryData):
        self.telemetry_data = telemetryData

    def update_telemetry_loop(self):
        for key, val in self.translationKeys.iteritems():
            if val['display']:
                #print 'Telemetry Data:'
                #print self.telemetry_data
                self.values[key]
                self.values[key]['text'] = self.telemetry_data[key]
        self.after(500, self.update_telemetry_loop)
 
    def quit_(self):
        """ Customized quit function to allow for safe closure of processes. """
        self.tthread.stop()
        if self.tthread.is_alive():
            self.tthread.join()
        self.destroy()
    
    def load_keys(self, config_file):
        with open(config_file) as f:
            configuration = \
                json.load(f)#.replace('\n', '').replace(' ', '').replace('\r', '')
        return configuration

if __name__=='__main__':
    from Queue import Queue
    root = tk.Tk()
    t = TelemetryWidget(root, Queue())
    t.grid()
    root.update()
    print t.winfo_height(), t.winfo_width()
    root.mainloop()
    sys.exit()
