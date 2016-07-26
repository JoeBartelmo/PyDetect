from mainapp import MainApplication
import Tkinter as tk
from multiprocessing import Process

def start(client_queue_in, client_queue_out, server_ip):
    root = tk.Tk()

    # define mainapp instance
    m = MainApplication(root, client_queue_in, client_queue_out, server_ip)
    root.protocol("WM_DELETE_WINDOW", m.close_)

    # title and icon
    root.wm_title('Hyperloop Imaging Team')
    img = tk.PhotoImage(file='/home/hyperloop/PyDetect/gui/assets/rit_imaging_team.png')
    root.tk.call('wm', 'iconphoto', root._w, img)

    # run forever
    Process(target=root.mainloop).start()

if __name__=='__main__':
    from Queue import Queue

    in_queue = Queue()
    out_queue = Queue()
    server_ip = '192.0.0.1'

    start(in_queue, out_queue, server_ip)
