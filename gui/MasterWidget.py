# Copyright MIT
# Primary Author: Nathan Dileas

import Tkinter as tk
import sys
import cv2
import time

class MasterWidget(tk.Frame):
    def __init__(self, parent, streams):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.streams = streams

        self.init_ui()
      
        self.after_id = None

    def init_ui(self):
        self.pause_button = tk.Button(self, text=u'\u23F8', command=self.pause)
        self.play_button = tk.Button(self, text=u'\u25B6', command=self.play)
        self.move_forward = tk.Button(self, text='>>', command=lambda:self.move(10, 1))
        self.move_back = tk.Button(self, text='<<', command=lambda:self.move(-10, 1))
        self.snap_current = tk.Button(self, text='|>', command=lambda:self.move(0, 2))
        self.snap_start = tk.Button(self, text='<|', command=lambda:self.move(0, 0))
        tk.Button(self, text='X', command=self.quit_).grid(row=0,column=6, sticky='nw')

        self.snap_start.grid(row=0, column=0)
        self.move_back.grid(row=0, column=1)
        self.pause_button.grid(row=0, column=2)
        self.play_button.grid(row=0, column=3)
        self.move_forward.grid(row=0, column=4)
        self.snap_current.grid(row=0, column=5)
        
    def play(self):
        for s in self.streams:
            if s.vidcap.isOpened():
                s.play()

        self.after_id = self.after(30, self.play)

    def pause(self):
        for i in range(50):
            if self.after_id is not None:
                self.after_cancel(self.after_id)
                self.after_id = None

    def move(self, *args):
        for s in self.streams:
            s.move(*args)

    def quit_(self):
        for s in self.streams:
            if s.vidcap.isOpened():
                s.quit_()
        self.quit()
        self.parent.quit()

