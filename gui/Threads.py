import threading
import time
from Queue import Empty

class VideoThread(threading.Thread):
    def __init__(self, vidcap, queue):
        super(VideoThread, self).__init__()
        self._vidcap = vidcap
        self._queue = queue
        self._stop = threading.Event()

        self.transformFunction = None

    def run(self):
        print time.time()
        while self.stopped() is False:
            
            flag, frame = self._vidcap.read()

            if not flag:
                continue

            if self.transformFunction is not None:
                frame = self.transformFunction(frame)

            self._queue.put(frame)
            #print self._queue.qsize()

            #size = self._queue.qsize()
            #while self._queue.qsize() > 5 and self._queue.qsize() >= size - 5 and self.stopped() == False:
            #    time.sleep(.001)

        self.empty_queue()
        self._queue.join()
        self._vidcap.release()
        print 'Killing Video Thread'

    def empty_queue(self):
        while self._queue.empty() is False:
            __ = self._queue.get()
            self._queue.task_done()

    def get_ideal_images(self):
        self.ideal_pump = []

        for s in self.streams:
            if s._vidcap.isOpened():
                flag, frame = s._vidcap.read()
                if not flag:
                    continue
                ideal_keypoint = self.fast.detect(frame, None)
                self.ideal_pump.append(stealth_pumpkin(frame, ideal_keypoint))


    def stop(self):
        self._stop.set()
   
    def transform(self, func):
        self.transformFunction = func

    def stopped(self):
        return self._stop.isSet()


class TelemetryThread(threading.Thread):
    def __init__(self, telem_widget, client_queue):
        super(TelemetryThread, self).__init__()
        self._queue = client_queue
        self._widget = telem_widget
        self._stop = threading.Event()

        self.transformFunction = None

    def run(self):
        while self.stopped() is False:
            try:
                item = self._queue.get(timeout=0.75)
            except Empty:
                continue

            if type(item) == str:    # i.e. is a warning or error
                self._widget.update_(item)
                self._widget.update()

            elif item:
                self._widgets.parent.command_w.log(item)   # TODO change to depickle or de-json

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


