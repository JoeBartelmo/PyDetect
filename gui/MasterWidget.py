# Copyright MIT
# Primary Author: Nathan Dileas

import Tkinter as tk
import sys
import cv2
import time

class MasterWidget(tk.Frame):
    """
    Controls playback of video streams from valmar.

    Tkinter elements:
        Skip to beginning: self-explanatory
        Skip backward: skip backward 10 seconds
        pause: self-explanatory
        play: self-explanatory
        Skip forward: skip forward 10 seconds
        Skip to current: self-explanatory

    Args:
        parent: parent window
        streams: VideoStream objects

    """
    def __init__(self, parent, streams):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.streams = streams

        self.init_ui()
      
        self.after_id = None  # allows for correct pausing behavior

    def init_ui(self):
        """ Initialize visual elements of widget. """
        self.pause_button = tk.Button(self, text=u'\u23F8', command=self.pause)
        self.play_button = tk.Button(self, text=u'\u25B6', command=self.play)
        self.move_forward = tk.Button(self, text='>>', command=lambda:self.move(10, 1))
        self.move_back = tk.Button(self, text='<<', command=lambda:self.move(-10, 1))
        self.snap_current = tk.Button(self, text='|>', command=lambda:self.move(0, 2))
        self.snap_start = tk.Button(self, text='<|', command=lambda:self.move(0, 0))
        
        self.snap_start.grid(row=0, column=0)
        self.move_back.grid(row=0, column=1)
        self.pause_button.grid(row=0, column=2)
        self.play_button.grid(row=0, column=3)
        self.move_forward.grid(row=0, column=4)
        self.snap_current.grid(row=0, column=5)
        
    def play(self):
        """ Play video streams. """ 
        for s in self.streams:
            if s.vidcap.isOpened():
                s.play()

    def pause(self):
        """ Pause video streams. """ 
        for i in range(50):
            if self.after_id is not None:
                self.after_cancel(self.after_id)
                self.after_id = None

    def quit_(self):
        """ Customized quit function to allow for safe closure of processes. """
        self.quit()

