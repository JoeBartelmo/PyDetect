#!/usr/bin/env python
# Copyright MIT
# Primary Author: Nathan Dileas

from multiprocessing import Process, Queue, Manager
import cv2
import cv2.cv as cv
from PIL import Image, ImageTk
import Tkinter as tk
import time

class VideoWidget(tk.Frame):
    """
    Displays video streams from valmar.

    Args:
        parent: parent window
        frame_size: size to be displayed at, for focus in GUI
    """
    def __init__(self, parent, frame_size):
        tk.Frame.__init__(self, parent, width=frame_size[0], height=frame_size[1], bd=2, relief='groove')
        self.parent = parent

        self.queue = Queue()
        self.frame_size = frame_size

        # only visual element, Image display label
        self.initial_im = tk.PhotoImage(file='/home/hyperloop/PyDetect/gui/assets/blank_256x240.png')   #TODO change to relative path, image is mostly useless anyway
        self.image_label = tk.Label(self, image=self.initial_im, width=frame_size[0],height=frame_size[1])
        self.image_label.grid(row=0, column=0)

    def update_image(self):
        """ Update image in label to next image in queue. """

        frame = self.queue.get(False)   # non blocking call
        if frame == None:
            return

        frame_resized = cv2.resize(frame, self.frame_size)
        a = Image.fromarray(frame_resized)
        b = ImageTk.PhotoImage(image=a)
        self.image_label.configure(image=b, width=self.frame_size[0], height=self.frame_size[1])
        self.image_label._image_cache = b  # avoid garbage collection
        self.update()

if __name__=='__main__':
    root = tk.Tk()
    VideoWidget(root).grid()
    root.update()
    print root.winfo_height(), root.winfo_width()
    root.mainloop()
