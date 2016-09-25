# Copyright (c) 2016, Jeffrey Maggio and Joseph Bartelmo
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial 
# portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Copyright MIT
# Primary Author: Nathan Dileas

import Tkinter as tk
import sys
import cv2
import time

import logging
logger = logging.getLogger('mars_logging')

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
        
    def play(self, delay=10):
        """ Play video streams. """
        self.after_id = None
        
        for s in self.streams:
            if s.vidcap.isOpened() and s.display_q.qsize() > 0:
                s.update_image()
        
        self.after_id = self.after(delay, self.play, delay)

    def pause(self):
        """ Pause video streams. """ 
        for i in range(50):
            if self.after_id is not None:
                self.after_cancel(self.after_id)
                self.after_id = None

    def quit_(self):
        """ Customized quit function to allow for safe closure of processes. """
        self.pause()
        self.quit()

