import cv2
from PIL import Image, ImageTk
import numpy
from Queue import Queue, Empty
import time
import Tkinter as tk

from Threads import VideoThread
from TelemetryWidget import TelemetryWidget
from ControlWidget import ControlWidget
from img_proc.misc import demosaic


import logging
logger = logging.getLogger('mars_logging')

class MainApplication(tk.Frame):
    def __init__(self, parent, client_queue_cmd, client_queue_log, client_queue_telem, server_ip):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.stream_order = [0,1,2]

        self.init_ui(client_queue_cmd, client_queue_log, client_queue_telem, server_ip)

        self.fast = cv2.FastFeatureDetector()
        
        self.start_streams()
        self.start_telemetry()
        self.displayed_image = numpy.zeros((720,640,3))
        
    def init_ui(self, client_queue_cmd, client_queue_log, client_queue_telem, server_ip):
        """ Initialize visual elements of widget. """
        self.streams = []

        logger.info('Attempting to connect to rtsp stream from left camera')
        l_src = 'rtsp://' + server_ip + ':8554/'   # left camera setup
        l = VideoThread(cv2.VideoCapture(l_src), Queue())
        self.streams.append(l)

        logger.info('Attempting to connect to rtsp stream from center camera')
        c_src = 'rtsp://' + server_ip + ':8555/'   # center camera setup
        c = VideoThread(cv2.VideoCapture(c_src), Queue())
        self.streams.append(c)

        logger.info('Attempting to connect to rtsp stream from right camera')
        r_src = 'rtsp://' + server_ip + ':8556/'   # right camera setup
        r = VideoThread(cv2.VideoCapture(r_src), Queue())
        self.streams.append(r)

        logger.info('Appending photo image widget to main app')
        # Image display label
        self.initial_im = tk.PhotoImage()
        self.image_label = tk.Label(self, image=self.initial_im, width=640,height=720)
        self.image_label.grid(row=0, column=0, rowspan=2, sticky='nw')

        logger.info('Launching telemetry widget')
        # telemetry display widget
        self.telemetry_w = TelemetryWidget(self, client_queue_telem)
        self.telemetry_w.grid(row=0, column=1, padx=5, pady=5, sticky='nesw')

        logger.info('Launching Control Widget')
        # control and logging widget
        self.command_w = ControlWidget(self, client_queue_cmd, client_queue_log)
        self.command_w.grid(row=1, column=1, rowspan=2, padx=5, pady=5, sticky='nw')


        logger.info('Finalizing frame...')
        # radiobuttons for choosing which stream is in focus
        frame = tk.Frame(self, bd=2, relief='groove')
        self.stream_active = tk.IntVar()
        self.stream_active.set(0)
        self.pump = tk.IntVar()
        
        tk.Radiobutton(frame, text='Left', variable=self.stream_active, value=0, command=self.choose_focus).grid(row=0, column=0, padx=5, pady=5)
        tk.Radiobutton(frame, text='Center', variable=self.stream_active, value=1, command=self.choose_focus).grid(row=0, column=1, padx=5, pady=5)
        tk.Radiobutton(frame, text='Right', variable=self.stream_active, value=0, command=self.choose_focus).grid(row=0, column=2, padx=5, pady=5)
        tk.Checkbutton(frame, text='Pumpkin', variable=self.pump).grid(row=0, column=4)

        frame.grid(row=1, column=0, sticky='s')

        logger.info('Mars Client Initialized')
        self.grid()

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
        center = (10, 390)
        topleft = (10, 230)
        topright = (10, 230)

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
        a, b, c = self.stream_order
        
        try:
            l_frame = demosaic(self.streams[a]._queue.get(False))
        except Empty:
            l_frame = None
        try:
            c_frame = demosaic(self.streams[b]._queue.get(False))
        except Empty:
            c_frame = None
        try:
            r_frame = demosaic(self.streams[c]._queue.get(False))
        except Empty:
            r_frame = None

        self.addText(l_frame, c_frame, r_frame)

        if l_frame is not None:
            l_frame = cv2.resize(l_frame, (320, 240))
            self.displayed_image[:240,:320,:] = l_frame
        if c_frame is not None:    
            c_frame = cv2.resize(c_frame, (640, 480))
            self.displayed_image[240:, :,:] = c_frame
        if r_frame is not None:
            r_frame = cv2.resize(r_frame, (320, 240))
            self.displayed_image[:240,320:640,:] = r_frame

        big_frame = numpy.asarray(self.displayed_image, dtype=numpy.uint8)

        imageFromArray = Image.fromarray(big_frame)
        tkImage = ImageTk.PhotoImage(image=imageFromArray)
        self.image_label.configure(image=tkImage, width=big_frame.shape[0], height=big_frame.shape[1])
        self.image_label._image_cache = tkImage  # avoid garbage collection

        self.update()
        
        self.after(delay, self.display_streams, delay)

    def start_streams(self):
        for s in self.streams:
            if s._vidcap.isOpened():
                s.start()
        
        self.after(100, self.display_streams)   # TODO decide on appropriate interval

    def start_telemetry(self):
        """ after 5 seconds, start telemtry updates. """
        self.telemetry_w.tthread.start()

    def close_(self):
        logger.debug('GUI: Stopping all video streams...')
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
        #self.quit()
        self.destroy()
        #self.parent.quit()
        #self.parent.destroy()
            

if __name__ == '__main__':
    root = tk.Tk()   # get root window
    server_ip = 'hyperlooptk1.student.rit.edu'
    in_queue = Queue()
    out_queue = Queue()

    # define mainapp instance
    m = MainApplication(root, in_queue, out_queue, server_ip)

    # run forever
    root.mainloop()



