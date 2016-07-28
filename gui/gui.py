from mainapp import MainApplication
import Tkinter as tk
from multiprocessing import Process

def start(client_queue_in, client_queue_out, server_ip):
    """
    Start graphical interface for client.

    Args:
        client_queue_in: queue to get telemetry and logging info
        client_queue_out: queue to communicate commands
        server_ip: server IP address for rtsp stream access
    """
    root = tk.Tk()   # get root window

    # define mainapp instance
    m = MainApplication(root, client_queue_in, client_queue_out, server_ip)
    root.protocol("WM_DELETE_WINDOW", m.close_)

    # title and icon
    root.wm_title('Hyperloop Imaging Team')
    # TODO change to relative path
    #img = tk.PhotoImage()
    #root.tk.call('wm', 'iconphoto', root._w, img)

    # run forever
    root.mainloop()
    print 'sadhi;knsafdklnfdsknl;fsadjn;fagsdl;kjnfdsalkjnfdslkjn;fdslkfdsalk;n'

if __name__=='__main__':
    from Queue import Queue

    in_queue = Queue()
    out_queue = Queue()
    server_ip = 'hyperlooptk1.student.rit.edu'

    start(in_queue, out_queue, server_ip)
