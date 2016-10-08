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

import cv2
from PIL import Image, ImageTk
import numpy
from Queue import Queue, Empty
import time
import Tkinter as tk

from Threads import VideoThread
from TelemetryWidget import TelemetryWidget
from ControlWidget import ControlWidget
from img_proc.misc import *

import logging
logger = logging.getLogger('mars_logging')


CAMERA_LOC_MAP = {'Left Camera': '../gui/left.sdp', 'Right Camera': '../gui/right.sdp', 'Front Camera': '../gui/center.sdp'}

class MainApplication(tk.Frame):
    '''
    Responsible for launching all 3 streams and reconnecting when needed.
    '''
    def __init__(self, parent, client_queue_cmd, client_queue_log, client_queue_telem, server_ip):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.stream_order = [0,1,2]
        self.server_ip = server_ip
        #for aspect ratio resizing of image
        #we found 720/640 to give the most aesthetic view
        self.imageHeight  = 720 
        self.imageWidth = 640
        self.aspectRatio = 720/640
 
        #Left Camera, Center Camera, Right Camera
        self.streams = [None, None, None]
        self.displayed_image = numpy.zeros((self.imageHeight,self.imageWidth,3))
        
        self.init_ui(client_queue_cmd, client_queue_log, client_queue_telem, server_ip)

        self.fast = cv2.FastFeatureDetector()
        
        self.runStreams = False
        
        self.start_streams()
        self.start_telemetry()

    def image_resize(self, event):
        if abs(event.width - self.imageWidth) > 2 or abs(event.height - self.imageHeight) > 2:
            self.imageHeight = event.height
            self.imageWidth = event.width
     
            self.displayed_image = numpy.zeros((self.imageHeight,self.imageWidth,3))

    def init_ui(self, client_queue_cmd, client_queue_log, client_queue_telem, server_ip):
        """ Initialize visual elements of widget. """

        logger.info('Appending photo image widget to main app')
        # Image display label
        self.initial_im = tk.PhotoImage()
        self.image_label = tk.Label(self, image=self.initial_im)
        #self.image_label.grid(row=0, column=0, rowspan=2, sticky='nw')
        self.image_label.grid(row=0, column=0, rowspan = 2, sticky = 'nsew')
        self.image_label.bind('<Configure>', self.image_resize)

        logger.info('Launching telemetry widget')
        # telemetry display widget
        self.telemetry_w = TelemetryWidget(self, client_queue_telem)
        #self.telemetry_w.grid(row=0, column=1, padx=5, pady=5, sticky='nesw')
        self.telemetry_w.grid(row=0, column=1, sticky='nsew')

        logger.info('Launching Control Widget')
        # control and logging widget
        self.command_w = ControlWidget(self, client_queue_cmd, client_queue_log)
        #self.command_w.grid(row=1, column=1, rowspan=2, padx=5, pady=5, sticky='nw')
        self.command_w.grid(row=1, column=1, sticky='nsew') 

        logger.info('Finalizing frame...')
        # radiobuttons for choosing which stream is in focus
        #frame = tk.Frame(self, bd=2, relief='groove')
        self.stream_active = tk.IntVar()
        self.stream_active.set(0)
        self.pump = tk.IntVar()
        #frame.grid(row=1, column=0, sticky='s')
        
        #tk.Radiobutton(frame, text='Left', variable=self.stream_active, value=0, command=self.choose_focus).grid(row=0, column=0, padx=5, pady=5)
        #tk.Radiobutton(frame, text='Center', variable=self.stream_active, value=1, command=self.choose_focus).grid(row=0, column=1, padx=5, pady=5)
        #tk.Radiobutton(frame, text='Right', variable=self.stream_active, value=0, command=self.choose_focus).grid(row=0, column=2, padx=5, pady=5)
        #tk.Checkbutton(frame, text='Pumpkin', variable=self.pump).grid(row=0, column=4)
        self.grid(row = 0, column=0, sticky="nsew")
        logger.info('Client GUI Initialized')
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)
        for i in range(0,2):
            self.grid_columnconfigure(i, weight=1)
            self.grid_rowconfigure(i, weight=1)
        
        #self.bind('<Configure>', self._resize)

    def toggle_pumpkin(self, event):
        if self.pump.get() == 1:
            def transfromFunc(frame):
                # do pumpkin processing

                frame_kp = self.fast.detect(frame, None)
                squash = stealth_pumpkin(frame, frame_kp)

                pumpkins_indexes = sneaky_squash(ideal_image, squash)   # TODO fix ideal_image junk

                return highlight.highlight(frame, pumpkins_indexes, color=(255,0,0))
                
            for idx, stream in enumerate(self.streams):
                s.transform(transformFunc)

        else:
            for s in self.streams:
                s.transform(None)

    def choose_focus(self):
        """ Change stream focus. """
        if self.stream_active.get() == 0:  # center focus
            self.stream_order = [0,1,2]
        elif self.stream_active.get() == 1:  # left focus
            self.stream_order = [1,0,2]
        elif self.stream_active.get() == 2:  # right focus
            self.stream_order = [0,2,1]
        else:
            self.stream_order = [0,1,2]
    
    def addText(self, l_frame, c_frame, r_frame):
        """ Change text on boxes """
        font = cv2.FONT_HERSHEY_SIMPLEX
        center = (10, (self.imageWidth / 2) + 70)
        topleft = (10, (self.imageHeight / 3) - 10)
        topright = (10, (self.imageHeight / 3) - 10)

        def setText(l_text, r_text, c_text):
            if l_frame is not None:
                cv2.putText(l_frame, l_text, topleft, font, 0.5, (255,0,0), 1)
            if c_frame is not None:
                cv2.putText(c_frame, c_text, center, font, 0.5, (255,0,0), 1)
            if r_frame is not None:
                cv2.putText(r_frame, r_text, topright, font, 0.5, (255,0,0), 1)

        if self.stream_active.get() == 0:  # left focus
            setText('Center', 'Right', 'Left')
        elif self.stream_active.get() == 1:  # center focus
            setText('Left', 'Right', 'Center')
        elif self.stream_active.get() == 2:  # right focus
            setText('Right', 'Center', 'Left')

        return (l_frame, c_frame, r_frame)

    def display_streams(self, delay=0):
        if self.runStreams == False:
            self.runStreams = True
            return

        a, b, c = self.stream_order
        
        try:
            l_frame = color_correct(self.streams[a]._queue.get(False))
        except Empty:
            l_frame = None
        try:
            c_frame = color_correct(self.streams[b]._queue.get(False))
        except Empty:
            c_frame = None
        try:
            r_frame = color_correct(self.streams[c]._queue.get(False))
        except Empty:
            r_frame = None

        
        thirdHeight = int(self.imageHeight / 3)
        halfWidth = int(self.imageWidth / 2)
        
        if l_frame is not None:
            l_frame = cv2.resize(l_frame, (halfWidth, thirdHeight))
            self.displayed_image[:thirdHeight,:halfWidth,:] = l_frame
        if c_frame is not None:    
            c_frame = cv2.resize(c_frame, (self.imageWidth, self.imageHeight - thirdHeight))
            self.displayed_image[thirdHeight:, :,:] = c_frame
        if r_frame is not None:
            r_frame = cv2.resize(r_frame, (self.imageWidth - halfWidth, thirdHeight))
            self.displayed_image[:thirdHeight,halfWidth:self.imageWidth,:] = r_frame

        self.addText(l_frame, c_frame, r_frame)
        
        big_frame = numpy.asarray(self.displayed_image, dtype=numpy.uint8)

        imageFromArray = Image.fromarray(big_frame)
        try:
            tkImage = ImageTk.PhotoImage(image=imageFromArray)
            self.image_label.configure(image=tkImage)
        
            self.image_label._image_cache = tkImage  # avoid garbage collection

            self.update()
        except RuntimeError:
            logger.warning('Unable to update image frame. Assuming application has been killed unexpectidly.')
            return
        self.after(delay, self.display_streams, delay)

    def start_streams(self):
        '''
        1) If streams are open, close them
        2) Attempt connection to each RTSP stream
        '''
        if self.runStreams:
            logger.info('Streams were already open on GUI, releasing and restarting capture')
            self.runStreams = False
            for s in self.streams:
                if s is not None and s._vidcap is not None and s._vidcap.isOpened():
                    s.stop()
                    s.join()
                    s = None
            self.displayed_image = numpy.zeros((self.imageHeight,self.imageWidth,3))

        iteration = 0
        for camera in CAMERA_LOC_MAP:
            #logger.info('Attempting to connect to ' + camera + ' on port ' + str(CAMERA_PORT_MAP[camera]))
            captureCv = VideoThread(camera, CAMERA_LOC_MAP[camera], Queue())
            self.streams[iteration] = captureCv
            iteration += 1

        for s in self.streams:
            s.start()

        self.runStreams = True
        
        self.after(100, self.display_streams)   # TODO decide on appropriate interval

    def start_telemetry(self):
        """ after 5 seconds, start telemtry updates. """
        self.telemetry_w.tthread.start()

    def close_(self):
        logger.debug('GUI: Stopping all video streams...')
        self.runStreams = False 
        #stop the threads
        for stream in self.streams:
            stream.stop()
            if stream.is_alive():
                stream.join()
        logger.debug('GUI destroying widgets...')
        #throw widgets in garbage
        self.telemetry_w.quit_()
        self.command_w.destroy()

        logger.debug('GUI Destorying main application box...')
        self.destroy()

if __name__ == '__main__':
    root = tk.Tk()   # get root window
    server_ip = 'hyperlooptk1.student.rit.edu'
    in_queue = Queue()
    out_queue = Queue()
    online_queue = Queue()

    # define mainapp instance
    m = MainApplication(root, in_queue, out_queue, online_queue, server_ip)

    # run forever
    root.mainloop()

