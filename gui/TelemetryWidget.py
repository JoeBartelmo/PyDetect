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

        self.string_vars = {}
        self.telemtry_labels = {}

        self.telemetry_keys = ['','displacement', 'velocity', 'rpm', \
                '', 'power', 'batt_remaining','voltage','current', '', 'conected',\
                'frame_size', 'int_time', '', 'time']
        self.pretty_keys = ['Robot:','Displacement [m]:', 'Velocity [m/h]:', 'RPM [r/min]:', 'Battery:', 'Power [bool]:', '% Remaining [%age]:', 'Voltage [mV]:', 'Current [mA]:', 'Camera:', 'Connected [bool]:', 'Frame Size [rxc]:', 'Integration Time [s]:', 'Miscellaneous:', 'Time since start [s]:']

        self.init_ui()
        self.telem_queue = client_queue_in
        self.tthread = TelemetryThread(self, client_queue_in)

    def init_ui(self):
        """ Initialize visual elements of widget. """

        for idx, key in enumerate(self.telemetry_keys):
            # label
            l = tk.Label(self, text=self.pretty_keys[idx], padx=5, pady=5, bd=2, justify='left', relief='ridge', width=18)
            l.grid(row=idx, column=0, sticky='w')

            # actual telemetry
            self.string_vars[key] = tk.StringVar()
            self.string_vars[key].set(key)
            self.telemtry_labels[key] = tk.Label(self, textvariable=self.string_vars[key], padx=5, pady=5, width=18, anchor='w')
            self.telemtry_labels[key].grid(row=idx,column=1, sticky='w')
        
    def run_telemetry(self, delay=100):
        """ Update telemetry continuously. """
        item = None

        try:
            item = self.tthread._queue.get(timeout=0.50)   # non-blocking
            if item:
                for i in self.telemetry_keys:
                    self.string_vars[i].set(telemetry[i])
                self.update()
        except Empty:
            pass
        
        self.after(delay, self.run_telemetry, delay)

    def quit_(self):
        """ Customized quit function to allow for safe closure of processes. """
        self.tthread.stop()
        if self.tthread.is_alive():
            self.tthread.join()
        self.quit()

if __name__=='__main__':
    from Queue import Queue
    root = tk.Tk()
    t = TelemetryWidget(root, Queue())
    t.grid()
    root.update()
    print t.winfo_height(), t.winfo_width()
    root.mainloop()
    sys.exit()
