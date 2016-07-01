#!/usr/bin/env python
#
# @file "main"
# @authors "Joseph Bartelmo"
# @contact "joebartelmo@gmail.com"
# @date "5/4/2016"
# @copyright "MIT"
#

import Tkinter as tk
import sys
import argparse

from client.json_serializable_object import SerializableClient
from client.TelemetryWidget import TelemetryWidget
from client.MasterWidget import MasterWidget
from client.ControlWidget import ControlWidget
from client.VideoStream import VideoStream

class MainApplication(tk.Frame):
    def __init__(self, parent, args, **kwargs):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.serializedClient = SerializableClient(args.json_file)

        self.init_ui()

        self.start_streams()
        self.start_telemtry()

    def init_ui(self):
        self.streams = []

        l = VideoStream(self, 0, 'Left', num=0)
        l.grid(row=0, column=0)
        self.streams.append(l)

        c = VideoStream(self, 'drop.avi', 'Center', frame_size=(640,480), num=1)
        c.grid(row=2, column=0, columnspan=2, rowspan=2)
        self.streams.append(c)

        r = VideoStream(self, 'drop.avi', 'Right', num=2)
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

        self.telemetry_w = TelemetryWidget(self)
        self.telemetry_w.grid(row=0, column=4, rowspan=3)

        self.command_w = ControlWidget(self)
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
        #self.telemetry_w.start()
        #self.telemtry_w.persistent_update()
        pass

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

def main(args):
    root = tk.Tk()
    MainApplication(root, args)
    root.update()
    print root.winfo_height(), root.winfo_width()
    root.mainloop()
    sys.exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('json_file', type=str, help='JSON file for stream setup')
    args = parser.parse_args()

    if args.json_file.split('.')[-1] is not 'json':
        print 'Not a valid .json file extension'

    main(args)
