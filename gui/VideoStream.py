import time
#from multiprocessing import Queue, Process   # change to from queue import Queue?
from Queue import Queue
import sys

import cv2
import numpy
import Tkinter as tk

import img_proc.stealth_pumpkin as stealth_pumpkin
from img_proc.misc import demosaic, color_correct
from Threads import VideoThread
from PIL import Image, ImageTk

import vlc_bindings as vlc

import logging
logger = logging.getLogger('mars_logging')

class VideoStream(tk.Frame):
    """
    Deals with video streams from valmar.

    Args:
        parent: parent window
        source: source for cv2 VideoCapture object
        name: for label in GUI
        frame_size: size to be displayed at, for focus in GUI
        num: for setting focus in parent widget
    """
    def __init__(self, parent, source, name, frame_size=(320, 240)):
        tk.Frame.__init__(self, parent, padx=3, pady=3, bd=2, relief='groove', takefocus=1)
        self.parent = parent

        self.name = name
        self.frame_size = frame_size
        
        # videocapture and video capture thread declaration
        self.vidcap = cv2.VideoCapture(source)
        self.display_q = Queue()
        self.vthread = VideoThread(self.vidcap, self.display_q)

        self.init_ui()

    def init_ui(self):
        """ Initialize visual elements of widget. """
        # Image display label
        self.initial_im = tk.PhotoImage()
        self.image_label = tk.Label(self, image=self.initial_im, width=self.frame_size[0],height=self.frame_size[1])
        self.image_label.grid(row=0, column=0, sticky='nw', columnspan=2)

        self.show_pump = tk.IntVar()
        self.show_pump.set(0)

        tk.Checkbutton(self, text="Pumpkin", variable=self.show_pump, command=self.show).grid(row=1,column=1, sticky='se')
        tk.Label(self, text=self.name, justify='left').grid(row=1, column=0, sticky='sw')

    def show(self):
        """ Whether or not to show pumpkin processing. """
        # TODO change to modify vthread func
        if self.show_pump.get() == 0:
            self.vthread.transform(None)
        if self.show_pump.get() == 1:
            self.vthread.transform(stealth_pumpkin.pumpkin)

    def update_image(self):
        """ Update image in label to next image in queue. """

        #print 'otha queue' + str(self.display_q.qsize())
        frame = self.display_q.get(timeout = 0.01)   # non blocking call

        if frame == None:
            return
        #print(frame);
        frame_resized = cv2.resize(frame, self.frame_size)
        a = Image.fromarray(frame_resized)
        b = ImageTk.PhotoImage(image=a)
        self.image_label.configure(image=b, width=self.frame_size[0], height=self.frame_size[1])
        self.image_label._image_cache = b  # avoid garbage collection
        self.update()

    def quit_(self):
        """ Customized quit function to allow for safe closure of processes. """
        self.vthread.stop()
        if self.vthread.isAlive():
            self.vthread.join()       
        self.quit()

if __name__=='__main__':
    root = tk.Tk()
    VideoStream(root).grid()
    root.update()
    print root.winfo_height(), root.winfo_width()
    root.mainloop()

