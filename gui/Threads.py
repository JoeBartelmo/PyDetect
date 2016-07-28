import threading
from Queue import Empty

class VideoThread(threading.Thread):
    def __init__(self, vidcap, queue):
        super(VideoThread, self).__init__()
        self._vidcap = vidcap
        self._queue = queue
        self._stop = threading.Event()

        self.transformFunction = None

    def run(self):

        while self.stopped() is False:
            
            flag, frame = self._vidcap.read()

            if not flag:
                continue

            if self.transformFunction is not None:
                frame = self.transformFunction(frame)

            self._queue.put(frame)
            print 'It\'s ALIVE'

        self._vidcap.release()
        print 'it\'s dead'

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

            if not telem:
                continue
            
            if type(item) == str:    # i.e. is a warning or error
                self._widget.update_(item)
                self._widget.update()

            elif item:
                self._widgets.parent.command_w.log(item)   # TODO change to depickle 

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


