# Copyright MIT
# Primary Author: Nathan Dileas
import time
from multiprocessing import Queue, Process   # change to from queue import Queue?
import sys

import cv2
import numpy
import Tkinter as tk

from VideoWidget import VideoWidget
import img_proc.stealth_pumpkin as stealth_pumpkin
from img_proc.misc import demosaic, color_correct

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
    def __init__(self, parent, source, name, frame_size=(320, 240), num=0):
        tk.Frame.__init__(self, parent, padx=3, pady=3, bd=2, relief='groove', takefocus=1)
        self.parent = parent

        self.num = num
        self.name = name
        self.frame_size = frame_size
        self.source = source
        
        self.init_ui()
        
        # processes and queues
        self.raw_q_1 = Queue()
        do_pump = lambda: stealth_pumpkin.script(self.raw_q_1, self.pumpkin.queue)
        self.pumpkin.proc = Process(target=do_pump)
        self.proc = Process(target=self.image_capture)

        # video capture 
        self.vidcap = cv2.VideoCapture(source)
        #self.vidcap.set(cv2.cv.CV_CAP_PROP_BUFFERSIZE, 3) # TODO check docs on this

        #self.fps = self.vidcap.get(cv2.cv.CV_CAP_PROP_FPS)
        self.fwidth = int(self.vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
        self.fheight = int(self.vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

        self.vidcap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640)
        self.vidcap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480)

        #fourcc = cv2.cv.CV_FOURCC('M','J','P','G')   # TODO fix writing out
        #self.vidout = cv2.VideoWriter('output.avi', fourcc, self.fps, (self.fheight,self.fwidth))

    def init_ui(self):
        """ Initialize visual elements of widget. """
        self.raw_vid = VideoWidget(self, self.frame_size)
        self.pumpkin = VideoWidget(self, self.frame_size)

        self.pumpkin.grid(row=0, column=0, sticky='nw', columnspan=2)
        self.raw_vid.grid(row=0, column=0, sticky='nw', columnspan=2)
        
        self.show_pump = tk.IntVar()
        self.show_pump.set(0)
        self.show()

        tk.Checkbutton(self, text="Pumpkin", variable=self.show_pump, command=self.show).grid(row=1,column=1, sticky='se')
        tk.Label(self, text=self.name, justify='left').grid(row=1, column=0, sticky='sw')

    def show(self):
        """ Whether or not to show pumpkin processing. """
        if self.show_pump.get() == 0:
            self.raw_vid.tkraise()
        elif self.show_pump.get() == 1:
            self.pumpkin.tkraise()
        
    def start(self):
        """ Start capture and processing. """
        self.proc.start()
        self.pumpkin.proc.start()

    def image_capture(self):
        """ Capture images from source provided. """
        #while True:
        while self.raw_vid.queue.qsize() < 100:
           
            flag, frame = self.vidcap.read()
            #print flag

            if not flag:
                break

            img = demosaic(frame)
            img_col = color_correct(img)

            self.raw_q_1.put(img)
            self.raw_vid.queue.put(img)  # TODO save also
            #self.vidout.write(frame)

    def check_stream(self):
        # TODO fix for threadsafe checking of videocap status and time
        self.vidcap.release()
        self.vidcap = cv2.VideoCapture(self.source)
        

    def play(self):
        """ Play video from source. """
        #print self.name, self.raw_vid.queue.qsize(), self.pumpkin.queue.qsize()

        if self.raw_vid.queue.qsize() == 0:
            return

        self.raw_vid.update_image()
        self.pumpkin.update_image()

    def move(self, t):
        """ Move videocapture oject to specified time. """
        if mode == 0:  # relative to start
            self.vidcap.set(cv2.cv.CAP_PROP_POS_MSEC, t*1000)
        if mode == 1:  # relative to current position
            current_pos = self.vidcap.get(cv2.cv.CAP_PROP_POS_MSEC)
            self.vidcap.set(cv2.cv.CAP_PROP_POS_MSEC, t*1000 + current_pos)
        if mode == 2:  # relative to end
            pass

    def quit_(self):
        """ Customized quit function to allow for safe closure of processes. """

        if self.vidcap.isOpened():
            self.pumpkin.proc.terminate()
            self.proc.terminate()
        
        self.vidcap.release()
        #self.vidout.release()

        self.quit()

if __name__=='__main__':
    root = tk.Tk()
    VideoStream(root).grid()
    root.update()
    print root.winfo_height(), root.winfo_width()
    root.mainloop()

