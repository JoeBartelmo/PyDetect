import Tkinter as tk
from multiprocessing import Process, Queue
import sys

class TelemetryWidget(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, bd=2, relief='groove')
        self.parent = parent

        self.string_vars = {}
        self.telemtry_labels = {}

        self.telemetry_keys = ['displacement', 'velocity', 'rpm', \
                'power', 'batt_remaining','voltage','current','conected',\
                'frame_size', 'int_time', 'time']

        for i in self.telemetry_keys:
            self.string_vars[i] = tk.StringVar()
            self.string_vars[i].set(i)
            self.telemtry_labels[i] = tk.Label(self, textvariable=self.string_vars[i],padx=5, pady=5, width=18,anchor='w')

        self.init_ui()

        self.telem_queue = Queue()
        self.p = Process(target=self.get_data)

    def init_ui(self):
        #options = (,padx=5, pady=5, bd=4, justify='left')
        ### ROBOT
        tk.Label(self, text='Robot:', bd=2, justify='left', relief='ridge', width=19, anchor='w').grid(row=0,column=0, sticky='w')
        tk.Label(self, text='Displacement [m]:', padx=5, pady=5, bd=2, justify='left', relief='ridge', width=18).grid(row=1,column=0, sticky='w')
        self.telemtry_labels['displacement'].grid(row=1,column=1, sticky='w')

        tk.Label(self, text='Velocity [m/h]:',padx=5, pady=5, bd=2, justify='left', relief='ridge', width=18).grid(row=2,column=0, sticky='w')
        self.telemtry_labels['velocity'].grid(row=2,column=1, sticky='w')

        tk.Label(self, text='RPM [r/min]:',padx=5, pady=5, bd=2, justify='left', relief='ridge', width=18).grid(row=3,column=0, sticky='w')
        self.telemtry_labels['rpm'].grid(row=3,column=1, sticky='w')

        ### BATTERY
        tk.Label(self, text='Battery:', bd=2, justify='left', relief='ridge', width=19, anchor='w').grid(row=4,column=0, sticky='w')
        tk.Label(self, text='Power [bool]:',padx=5, pady=5,  bd=2, justify='left', relief='ridge', width=18).grid(row=5,column=0, sticky='w')
        self.telemtry_labels['power'].grid(row=5,column=1, sticky='w')

        tk.Label(self, text='% Remaining [%age]:',padx=5, pady=5,  bd=2, justify='left', relief='ridge', width=18).grid(row=6,column=0, sticky='w')
        self.telemtry_labels['batt_remaining'].grid(row=6,column=1, sticky='w')

        tk.Label(self, text='Voltage [mV]:',padx=5, pady=5,  bd=2, justify='left', relief='ridge', width=18).grid(row=7,column=0, sticky='w')
        self.telemtry_labels['voltage'].grid(row=7,column=1, sticky='w')

        tk.Label(self, text='Current [mA]:',padx=5, pady=5,  bd=2, justify='left', relief='ridge', width=18).grid(row=8,column=0, sticky='w')
        self.telemtry_labels['current'].grid(row=8,column=1, sticky='w')

        ### CAMERA
        tk.Label(self, text='Camera:', bd=2, justify='left', relief='ridge', width=19, anchor='w').grid(row=9,column=0, sticky='w')
        tk.Label(self, text='Connected [bool]:',padx=5, pady=5,  bd=2, justify='left', relief='ridge', width=18).grid(row=10,column=0, sticky='w')
        self.telemtry_labels['conected'].grid(row=10,column=1, sticky='w')

        tk.Label(self, text='Frame Size [rxc]:',padx=5, pady=5,  bd=2, justify='left', relief='ridge', width=18).grid(row=11,column=0, sticky='w')
        self.telemtry_labels['frame_size'].grid(row=11,column=1, sticky='w')

        tk.Label(self, text='Integration Time [s]:',padx=5, pady=5,  bd=2, justify='left', relief='ridge', width=18).grid(row=12,column=0, sticky='w')
        self.telemtry_labels['int_time'].grid(row=12,column=1, sticky='w')

        ### MISC
        tk.Label(self, text='Miscellaneous:', bd=2, justify='left', relief='ridge', width=19, anchor='w').grid(row=13,column=0, sticky='w')
        tk.Label(self, text='Time since start [s]:',padx=5, pady=5, bd=2, justify='left', relief='ridge', width=18).grid(row=14,column=0, sticky='w')
        self.telemtry_labels['time'].grid(row=14, column=1, sticky='w')

        
        
    def update_(self, telemetry):
        for i in self.telemetry_keys:
            self.string_vars[i].set(telemetry[i])
        
    def persistent_update(self, delay=500):
        telem = self.telem_queue.get()
        self.update_(telem)
        self.update()

        root.after(delay, self.persistent_update, delay)

    def get_data(self):
        while True:
            #get data from json or whereever
            #telem = TODO()
            if not telem: 
                continue
            self.telem_queue.put(telem)

if __name__=='__main__':
    root = tk.Tk()
    t = TelemetryWidget(root)
    t.grid()
    root.update()
    #root.resizable(width=False, height=False)
    print t.winfo_height(), t.winfo_width()
    root.mainloop()
    sys.exit()
