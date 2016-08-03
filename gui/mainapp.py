import cv2
from PIL import Image, ImageTk
import numpy
import Tkinter as tk
from Threads import VideoThread
from Queue import Queue, Empty
import time

from TelemetryWidget import TelemetryWidget
from ControlWidget import ControlWidget
from img_proc.misc import demosaic

class MainApplication(tk.Frame):
    def __init__(self, parent, client_queue_cmd, client_queue_log, client_queue_telem, server_ip):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.stream_order = [0,1,2]

        self.init_ui(client_queue_cmd, client_queue_log, client_queue_telem, server_ip)
        
        self.start_streams()
        self.start_telemetry()
        
    def init_ui(self, client_queue_cmd, client_queue_log, client_queue_telem, server_ip):
        """ Initialize visual elements of widget. """
        self.streams = []

        print 'Attempting to connect to rtsp stream from left camera'
        l_src = 'rtsp://' + server_ip + ':8554/'   # left camera setup
        l = VideoThread(cv2.VideoCapture(l_src),  Queue())
        self.streams.append(l)

        print 'Attempting to connect to rtsp stream from centre camera'
        c_src = 'rtsp://' + server_ip + ':8555/'   # center camera setup
        c = VideoThread(cv2.VideoCapture(c_src),  Queue())
        self.streams.append(c)

        print 'Attempting to connect to rtsp stream from right camera'
        r_src = 'rtsp://' + server_ip + ':8556/'   # right camera setup
        r = VideoThread(cv2.VideoCapture(r_src),  Queue())
        self.streams.append(r)

        # Image display label
        self.initial_im = tk.PhotoImage()
        self.image_label = tk.Label(self, image=self.initial_im, width=640,height=720)
        self.image_label.grid(row=0, column=0, rowspan=2, sticky='nw')

        # telemetry display widget
        self.telemetry_w = TelemetryWidget(self, client_queue_telem)
        self.telemetry_w.grid(row=0, column=1, padx=5, pady=5, sticky='nw')

        # valmar control and logging widget
        self.command_w = ControlWidget(self, client_queue_cmd, client_queue_log)
        self.command_w.grid(row=1, column=1, rowspan=2, padx=5, pady=5, sticky='nw')

        # radiobuttons for choosing which stream is in focus
        buttons = ['Left', 'Center', 'Right']

        frame = tk.Frame(self, bd=2, relief='groove')
        col = 0
        self.stream_active = tk.IntVar()
        self.stream_active.set(0)
        for text in buttons:
            b = tk.Radiobutton(frame, text=text, variable=self.stream_active, value=col,\
                         command=self.choose_focus)
            b.grid(row=0, column=col, padx=5, pady=5)
            col += 1
        frame.grid(row=1, column=0, sticky='s')

        self.grid()

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
            cv2.putText(l_frame, l_text, topleft, font, 0.5, (255,0,0), 1)
            cv2.putText(c_frame, c_text, center, font, 0.5, (255,0,0), 1)
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

        for s in self.streams:
            if not s._vidcap.isOpened():
                return
        
        l_frame = demosaic(self.streams[a]._queue.get())
        c_frame = demosaic(self.streams[b]._queue.get())
        r_frame = demosaic(self.streams[c]._queue.get())

        l_frame = cv2.resize(l_frame, (320, 240))
        c_frame = cv2.resize(c_frame, (640, 480))
        r_frame = cv2.resize(r_frame, (320, 240))

        self.addText(l_frame, c_frame, r_frame)

        big_frame = numpy.zeros((720,640,3))
        big_frame[:240,:320,:] = l_frame
        big_frame[:240,320:640,:] = r_frame
        big_frame[240:, :,:] = c_frame

        big_frame = numpy.asarray(big_frame, dtype=numpy.uint8)

        a = Image.fromarray(big_frame)
        b = ImageTk.PhotoImage(image=a)
        self.image_label.configure(image=b, width=big_frame.shape[0], height=big_frame.shape[1])
        self.image_label._image_cache = b  # avoid garbage collection

        self.update()
        self.after(delay, self.display_streams, delay)

    def start_streams(self):
        for s in self.streams:
            if s._vidcap.isOpened():
                s.start()

        self.after(100, self.display_streams)

    def start_telemetry(self):
        """ after 5 seconds, start telemtry updates. """
        self.telemetry_w.tthread.start()
        #self.after(5000, self.telemetry_w.persistent_update)   # TODO decide on appropriate interval

    def close_(self):
        self.telemetry_w.quit_()

        for stream in self.streams:
            stream.stop()
            if stream.is_alive():
                stream.join()

        self.quit()
        self.parent.quit()
        self.parent.destroy()
            

if __name__ == '__main__':
    root = tk.Tk()   # get root window
    server_ip = 'hyperlooptk1.student.rit.edu'
    in_queue = Queue()
    out_queue = Queue()

    # define mainapp instance
    m = MainApplication(root, in_queue, out_queue, server_ip)

    # run forever
    root.mainloop()

    """
    stream = 'rtsp://129.21.56.100:8556/'

    vid = cv2.VideoCapture(stream)

    while vid.isOpened() is True:
        fl, fr = vid.read()
        if fl:
            cv2.imshow(stream, fr)
            cv2.waitKey(1)
    """


