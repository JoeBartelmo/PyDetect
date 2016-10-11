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

LEFT_CAM  =  '../gui/left.sdp'
RIGHT_CAM =  '../gui/right.sdp'
CENTER_CAM = '../gui/center.sdp'

CAMERAS = [LEFT_CAM, CENTER_CAM, RIGHT_CAM]

class MainApplication(tk.Frame):
    '''
    Main application handle, contains the frame that contains all other widgets
    '''
    def __init__(self, parent, client_queue_cmd, client_queue_log, client_queue_telem, client_queue_beam, destroy_event, server_ip):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        #this is now depricated, we no longer need the ip, but we may in the future so i'm leaving it here
        self.server_ip = server_ip
        self.client_queue_cmd = client_queue_cmd
        self.client_queue_log = client_queue_log
        self.client_queue_telem = client_queue_telem
        self.client_queue_beam = client_queue_beam
        #we found 720/640 to give the most aesthetic view
        self.imageHeight  = 720 
        self.imageWidth = 640
        
        self.destroy_event = destroy_event
 
        #Left Camera, Center Camera, Right Camera
        self.streams = [None, None, None]
        self.displayed_image = numpy.zeros((self.imageHeight,self.imageWidth,3))
        
        self.init_ui()

        self.fast = cv2.FastFeatureDetector()
        
        self.runStreams = False
        
        self.start_streams()
        self.start_telemetry()

    def image_resize(self, event):
        '''
        Handles the 'OnResize' for the ImageTk window
        '''
        if abs(event.width - self.imageWidth) > 2 or abs(event.height - self.imageHeight) > 2:
            self.imageHeight = event.height
            self.imageWidth = event.width
     
            self.displayed_image = numpy.zeros((self.imageHeight,self.imageWidth,3))

    def init_ui(self):
        """ Initialize visual elements of widget. """

        logger.info('Appending photo image widget to main app')
        # Image display label
        self.initial_im = tk.PhotoImage()
        self.image_label = tk.Label(self, image=self.initial_im)
        self.image_label.grid(row=0, column=0, rowspan = 2, sticky = 'nsew')
        self.image_label.bind('<Configure>', self.image_resize)

        logger.info('Launching telemetry widget')
        # telemetry display widget
        self.telemetry_w = TelemetryWidget(self, self.client_queue_telem, self.client_queue_beam)
        self.telemetry_w.grid(row=0, column=1, sticky='nsew')

        logger.info('Launching Control Widget')
        # control and logging widget
        self.command_w = ControlWidget(self, self.client_queue_cmd, self.client_queue_log)
        self.command_w.grid(row=1, column=1, sticky='nsew') 

        logger.info('Finalizing frame...')
        # radiobuttons for choosing which stream is in focus
        self.stream_active = tk.IntVar()
        self.focus_center()
        #self.pump = tk.IntVar()
        #tk.Checkbutton(frame, text='Pumpkin', variable=self.pump).grid(row=0, column=4)
        self.grid(row = 0, column=0, sticky="nsew")
        logger.info('Client GUI Initialized')
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)
        for i in range(0,2):
            self.grid_columnconfigure(i, weight=1)
            self.grid_rowconfigure(i, weight=1)

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

    def focus_left(self):
        self.stream_active.set(0)
    def focus_center(self):
        self.stream_active.set(1)
    def focus_right(self):
        self.stream_active.set(2)

    def get_stream_order(self):
        if self.stream_active.get() == 0:
            return (1, 0, 2)
        elif self.stream_active.get() == 1:
            return (0, 1, 2)
        elif self.stream_active.get() == 2:
            return (0, 2, 1)
    
    def addText(self, big_frame):
        """ Change text on boxes to their designated names """
        font = cv2.FONT_HERSHEY_SIMPLEX
        center = (10, (self.imageHeight - 10))
        topright = ((self.imageWidth / 2) + 10, (self.imageHeight / 3) - 10)
        topleft = (10, (self.imageHeight / 3 - 10))

        def setText(l_text, c_text, r_text):
            cv2.putText(big_frame, l_text, topleft, font, 0.5, (255,0,0), 1)
            cv2.putText(big_frame, c_text, center, font, 0.5, (255,0,0), 1)
            cv2.putText(big_frame, r_text, topright, font, 0.5, (255,0,0), 1)

        if self.stream_active.get() == 0:  # left focus
            setText('Center', 'Lefta', 'Right')
        #default
        elif self.stream_active.get() == 1:  # center focus
            setText('Left', 'Center', 'Right')
        elif self.stream_active.get() == 2:  # right focus
            setText('Left', 'Right', 'Center')

        return big_frame

    def display_streams(self, delay=0):
        '''
        Where the Image window gets updated.
        
        Check to see if we're obtaining data
        attempt to grab a non-blocking frame from each camera
        On success, color correct, and pipe into it's designated portion of the image.
        
        We then have to do some slight manipulation with a matrix to get it to fit
        properly. Then we slam it on the ImageTk window.
        '''
        try:
            if self.destroy_event.isSet() == True:
                self.runStreams = False
                self.parent.displayMarsDisconnected()
                return

            if self.runStreams == False:
                self.runStreams = True
                return

            leftFrame, centerFrame, rightFrame = self.get_stream_order()
            
            try:
                l_frame = color_correct(self.streams[leftFrame]._queue.get(False))
            except Empty:
                l_frame = None
            try:
                c_frame = color_correct(self.streams[centerFrame]._queue.get(False))
            except Empty:
                c_frame = None
            try:
                r_frame = color_correct(self.streams[rightFrame]._queue.get(False))
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
            
            big_frame = numpy.asarray(self.displayed_image, dtype=numpy.uint8)

            self.addText(big_frame)

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
        except KeyboardInterrupt:
            self.close_()

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

        for camera in range(0, len(CAMERAS)):
            #logger.info('Attempting to connect to ' + camera + ' on port ' + str(CAMERA_PORT_MAP[camera]))
            captureCv = VideoThread(CAMERAS[camera], CAMERAS[camera], Queue())
            self.streams[camera] = captureCv

        for s in self.streams:
            s.start()

        self.runStreams = True
        
        self.after(100, self.display_streams)

    def start_telemetry(self):
        """ after 5 seconds, start telemtry updates. """
        self.telemetry_w.tthread.start()

    def close_(self):
        logger.info('GUI: Stopping all video streams...')
        self.runStreams = False 
        #stop the threads
        for stream in self.streams:
            stream.stop()
            if stream.is_alive():
                stream.join()
        logger.info('GUI destroying widgets...')
        #throw widgets in garbage
        self.telemetry_w.quit_()
        self.command_w.destroy()

        logger.info('GUI Destorying main application box...')
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

