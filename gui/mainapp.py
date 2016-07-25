from TelemetryWidget import TelemetryWidget
from MasterWidget import MasterWidget
from ControlWidget import ControlWidget
from VideoStream import VideoStream

import Tkinter as tk

class MainApplication(tk.Frame):
    def __init__(self, parent, client_queue_in, client_queue_out, server_ip, **kwargs):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.init_ui(client_queue_in, client_queue_out, server_ip)

        self.start_streams()
        self.start_telemtry()

    def init_ui(self, client_queue_in, client_queue_out, server_ip):
        self.streams = []

        l_src = 'rtsp://%s/8555' % (server_ip)
        l = VideoStream(self, 0, 'Left', '/home/rithyperloop/PyDetect/src/assets/econ_raw.jpg', num=0)
        l.grid(row=0, column=0)
        self.streams.append(l)

        c_src = 'rtsp://%s/8554' % (server_ip)
        c = VideoStream(self, 1, 'Center', '/home/rithyperloop/PyDetect/src/assets/econ_raw.jpg', num=1, frame_size=(640,480))
        c.grid(row=2, column=0, columnspan=2, rowspan=2)
        self.streams.append(c)

        r_src = 'rtsp://%s/8556' % (server_ip)
        r = VideoStream(self, 2, 'Right', '/home/rithyperloop/PyDetect/src/assets/econ_raw.jpg', num=2)
        r.grid(row=0, column=1)
        self.streams.append(r)

        buttons = ['Left', 'Center', 'Right']

        frame = tk.Frame(self, bd=2, relief='groove')
        col = 0
        self.stream_active = tk.IntVar()
        self.stream_active.set(1)
        for text in buttons:
            b = tk.Radiobutton(frame, text=text, variable=self.stream_active, value=col,\
                         command=self.show_stream)
            b.grid(row=0, column=col, padx=5, pady=5)
            col += 1
        frame.grid(row=1, column=0)

        self.master_w = MasterWidget(self, self.streams)
        self.master_w.grid(row=1, column=1)

        self.telemetry_w = TelemetryWidget(self, client_queue_in)
        self.telemetry_w.grid(row=0, column=4, rowspan=3)

        self.command_w = ControlWidget(self, client_queue_out)
        self.command_w.grid(row=3, column=4, rowspan=1)

        r, c = self.grid_size()
        for i in range(r):
            self.grid_rowconfigure(i, pad=5)

        for i in range(c):
            self.grid_columnconfigure(i, pad=5)

        self.grid(sticky='e')

    def start_streams(self):
        for stream in self.streams:
            stream.start()   # start grabbing frames

    def start_telemtry(self):
        self.telemetry_w.start()
        self.after(5000, self.telemetry_w.persistent_update)

    def show_stream(self):
        for s in self.streams:
            s.grid_forget()

        if self.stream_active.get() == 0:  # left focus
            self.streams[0].raw_vid.frame_size = (640,480)
            self.streams[0].pumpkin.frame_size = (640,480)
            self.streams[0].grid(row=2, column=0, columnspan=2, rowspan=2)

            self.streams[1].raw_vid.frame_size = (320,240)
            self.streams[1].pumpkin.frame_size = (320,240)
            self.streams[1].grid(row=0, column=0)

            self.streams[2].raw_vid.frame_size = (320,240)
            self.streams[2].pumpkin.frame_size = (320,240)
            self.streams[2].grid(row=0, column=1)
                
        elif self.stream_active.get() == 1:  # center focus
            self.streams[1].raw_vid.image_label.configure(width=640,height=480)
            self.streams[1].pumpkin.image_label.configure(width=640,height=480)
            self.streams[1].grid(row=2, column=0, columnspan=2, rowspan=2)

            self.streams[0].raw_vid.frame_size = (320,240)
            self.streams[0].pumpkin.frame_size = (320,240)
            self.streams[0].grid(row=0, column=0)

            self.streams[2].raw_vid.frame_size = (320,240)
            self.streams[2].pumpkin.frame_size = (320,240)
            self.streams[2].grid(row=0, column=1)

        elif self.stream_active.get() == 2:  # right focus
            self.streams[2].raw_vid.frame_size = (640,480)
            self.streams[2].pumpkin.frame_size = (640,480)
            self.streams[2].grid(row=2, column=0, columnspan=2, rowspan=2)

            self.streams[0].raw_vid.frame_size = (320,240)
            self.streams[0].pumpkin.frame_size = (320,240)
            self.streams[0].grid(row=0, column=0)

            self.streams[1].raw_vid.frame_size = (320,240)
            self.streams[1].pumpkin.frame_size = (320,240)
            self.streams[1].grid(row=0, column=1)
        
        self.update()
    
    def close_(self):
        self.master_w.quit_()
        self.telemetry_w.quit_()
        self.quit()

