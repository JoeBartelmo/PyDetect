from TelemetryWidget import TelemetryWidget
from MasterWidget import MasterWidget
from ControlWidget import ControlWidget
from VideoStream import VideoStream

import Tkinter as tk

import sys

class MainApplication(tk.Frame):
    """
    Main Window for GUI.

    Consists of several widgets:
        Telemtry: TelemetryWidget, shows output from valmar
        Streams: VideoStream, shows video from valmar
        Stream Control: MasterWidget, controls playback of streams
        Command: ControlWidget, sends commands and shows logs from valmar

    Args:
        parent: parent window
        client_queue_in: queue to get telemetry and logging info
        client_queue_out: queue to communicate commands
        server_ip: server IP address for rtsp stream access
    """
    def __init__(self, parent, client_queue_in, client_queue_out, server_ip):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.init_ui(client_queue_in, client_queue_out, server_ip)

        self.start_streams()
        self.start_telemtry()

        #self.streams[0].play()
        #self.streams[1].play()
        #self.streams[2].play()

    def init_ui(self, client_queue_in, client_queue_out, server_ip):
        """ Initialize visual elements of widget. """
        self.streams = []

        print 'Attempting to connect to rtsp stream from left camera'
        l_src = 'rtsp://' + server_ip + ':8555/'   # left camera setup
        l = VideoStream(self, l_src, 'Left')
        l.grid(row=0, column=0)
        self.streams.append(l)

        print 'Attempting to connect to rtsp stream from centre camera'
        c_src = 'rtsp://' + server_ip + ':8554/'   # center camera setup
        c = VideoStream(self, c_src, 'Center', frame_size=(640,480))
        c.grid(row=2, column=0, columnspan=2, rowspan=2)
        self.streams.append(c)

        print 'Attempting to connect to rtsp stream from right camera'
        r_src = 'rtsp://' + server_ip + ':8556/'   # right camera setup
        r = VideoStream(self, r_src, 'Right')
        r.grid(row=0, column=1)
        self.streams.append(r)

        # radiobuttons for choosing which stream is in focus
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

        # stream control widget
        self.master_w = MasterWidget(self, self.streams)
        self.master_w.grid(row=1, column=1)

        # telemetry display widget
        self.telemetry_w = TelemetryWidget(self, client_queue_in)
        self.telemetry_w.grid(row=0, column=4, rowspan=3)

        # valmar control and logging widget
        self.command_w = ControlWidget(self, client_queue_out)
        self.command_w.grid(row=3, column=4, rowspan=1)

        r, c = self.grid_size()
        for i in range(r):
            self.grid_rowconfigure(i, pad=5)

        for i in range(c):
            self.grid_columnconfigure(i, pad=5)

        self.grid(sticky='e')

    def start_streams(self):
        """ start frame capture from streams. """
        for stream in self.streams:
            stream.vthread.start()

    def start_telemtry(self):
        """ after 5 seconds, start telemtry updates. """
        self.telemetry_w.tthread.start()
        #self.after(5000, self.telemetry_w.persistent_update)   # TODO decide on appropriate interval

    def show_stream(self):
        """ Change stream focus. """
        for s in self.streams:
            s.grid_forget()

        if self.stream_active.get() == 0:  # left focus
            self.stream_rearrange(order=[0,1,2])
        elif self.stream_active.get() == 1:  # center focus
            self.stream_rearrange(order=[1,0,2])
        elif self.stream_active.get() == 2:  # right focus
            self.stream_rearrange(order=[2,0,1])
    
        self.update()

    def stream_rearrange(self, order=[1,0,2]):
        a, b, c = order
        self.streams[a].frame_size = (640,480)
        self.streams[a].image_label.config(width=640, height=480)
        self.streams[a].grid(row=2, column=0, columnspan=2, rowspan=2)

        self.streams[b].frame_size = (320,240)
        self.streams[b].image_label.config(width=320, height=240)
        self.streams[b].grid(row=0, column=0)

        self.streams[c].frame_size = (320,240)
        self.streams[c].image_label.config(width=320, height=240)
        self.streams[c].grid(row=0, column=1)
        
    def close_(self):
        """ Customized quit function to allow for safe closure of processes. """
        self.master_w.quit()
        self.telemetry_w.quit_()

        for stream in self.streams:
            stream.quit_()
        print 'asdf'
        self.quit()
        print 'asdf2'
        self.parent.quit()
        print 'asdf3'
        self.parent.destroy()
        print 'asdf4'

