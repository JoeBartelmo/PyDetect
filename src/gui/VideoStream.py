# Copyright MIT
# Primary Author: Nathan Dileas

import Tkinter as tk
import sys
from multiprocessing import Queue, Process
import time

import cv2
import numpy

from VideoWidget import VideoWidget
import stealth_pumpkin

class VideoStream(tk.Frame):
    def __init__(self, parent, source, name, frame_size=(320, 240), num=0):
        tk.Frame.__init__(self, parent, padx=3, pady=3, bd=2, relief='groove', takefocus=1)
        self.parent = parent

        self.num = num
        self.name = name
        self.frame_size = frame_size

        # keybind click to make it big        
        #self.focus_set()
        #self.bind("<Button-1>", self.focus)
        
        self.init_ui()
        
        # processes and queues
        self.raw_q_1 = Queue()
        do_pump = lambda: stealth_pumpkin.script(self.raw_q_1, self.pumpkin.queue)
        self.pumpkin.proc = Process(target=do_pump)
        self.proc = Process(target=self.image_capture)

        # video capture 
        self.vidcap = cv2.VideoCapture(source)
        #self.vidcap.set(cv2.cv.CV_CAP_PROP_BUFFERSIZE, 3) # TODO check docs on this

        self.fps = self.vidcap.get(cv2.cv.CV_CAP_PROP_FPS)
        self.fwidth = int(self.vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
        self.fheight = int(self.vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.cv.CV_FOURCC('X','V','I','D')
        self.vidout = cv2.VideoWriter('output.avi', fourcc, 30, frame_size)

        self.after_id = None

    def init_ui(self):
        self.raw_vid = VideoWidget(self, self.frame_size)
        self.pumpkin = VideoWidget(self, self.frame_size)

        self.pumpkin.grid(row=0, column=0, sticky='nw', columnspan=2)
        self.raw_vid.grid(row=0, column=0, sticky='nw', columnspan=2)
        
        self.show_pump = tk.IntVar()
        self.show_pump.set(0)
        self.show()

        tk.Checkbutton(self, text="Pumpkin", variable=self.show_pump, command=self.show).grid(row=1,column=1, sticky='se')
        tk.Label(self, text=self.name, justify='left').grid(row=1, column=0, sticky='sw')

    def focus(self, event):
        self.focus_set()
        self.parent.stream_active.set(self.num)
        self.parent.show_stream()

    def show(self):
        if self.show_pump.get() == 0:
            self.raw_vid.tkraise()
        elif self.show_pump.get() == 1:
            self.pumpkin.tkraise()
        
    def start(self):
        self.proc.start()
        self.pumpkin.proc.start()

    def image_capture(self): 
        while True:
            while self.raw_vid.queue.qsize() < 100:
                flag, frame = self.vidcap.read()

                if not flag:
                    return

                img = demosaic(frame)
                img_col = color_correct(img)

                self.raw_q_1.put(frame)
                self.raw_vid.queue.put(frame)  # TODO save also
                self.vidout.write(frame)

    def play(self):
        #print self.raw_vid.queue.qsize(), self.pumpkin.queue.qsize()

        if self.raw_vid.queue.qsize() != 0:

            self.raw_vid.update_image()
            self.pumpkin.update_image()

        self.after_id = self.after(25, self.play)   # TODO make constant

    def pause(self):
        for i in range(50):
            if self.after_id is not None:
                self.after_cancel(self.after_id)
                self.after_id = None

    def move(self, t):
        if mode == 0:  # relative to start
            self.vidcap.set(cv2.cv.CAP_PROP_POS_MSEC, t*1000)
        if mode == 1:  # relative to current position
            current_pos = self.vidcap.get(cv2.cv.CAP_PROP_POS_MSEC)
            self.vidcap.set(cv2.cv.CAP_PROP_POS_MSEC, t*1000 + current_pos)
        if mode == 2:  # relative to end
            pass

    def quit_(self):
        self.pause()

        self.pumpkin.proc.terminate()
        self.proc.terminate()
        
        self.vidcap.release()
        self.vidout.release()

        self.quit()

def demosaic(input_im):
    #img_data = numpy.asarray(input_im, dtype=numpy.uint8)
    #rgb = cv2.cvtColor(img_data, cv2.COLOR_BAYER_GR2RGB)
    return input_im

def color_correct(input_im):
    # do nothing for now
    return input_im

if __name__=='__main__':
    root = tk.Tk()
    VideoStream(root).grid()
    root.update()
    print root.winfo_height(), root.winfo_width()
    root.mainloop()

