import Tkinter as tk
import os

from mainapp import MainApplication
from TopMenu import TopMenu

import logging

def start(client_queue_cmd, client_queue_log, client_queue_telem, server_ip):
    """
    Start graphical interface for client.

    Args:
        client_queue_in: queue to get telemetry and logging info
        client_queue_out: queue to communicate commands
        server_ip: server IP address for rtsp stream access
    """
    logger = logging.getLogger('mars_logging')
    logger.info('Creating GUI')
    root = tk.Tk()   # get root window

    # define mainapp instance
    m = MainApplication(root, client_queue_cmd, client_queue_log, client_queue_telem, server_ip)

    # menu
    menu_ = TopMenu(root, '../gui/operations.json', client_queue_cmd, 'Commands')
    root.config(menu=menu_)

    # title and icon
    root.wm_title('Hyperloop Imaging Team')
    img = tk.PhotoImage(os.path.join(os.getcwd(), '../gui/assets/rit_imaging_team.png'))
    root.tk.call('wm', 'iconphoto', root._w, img)

    #explicitly close each widget, then destroy root
    def destroyCallback():
        logger.debug('GUI entering destroy callback...')
        menu_.destroy() 
        m.close_()
        root.destroy()

    root.protocol('WM_DELETE_WINDOW', destroyCallback)
    
    root.update()
    root.mainloop()

if __name__=='__main__':
    from Queue import Queue
    from ColorLogger import initializeLogger 

    logger = initializeLogger('./', logging.DEBUG, 'mars_logging', sout = True, colors = True)
    logger.debug('GUI is running independant of client, attempting to connect to server hyperlooptk1.student.rit.edu')

    cmd_queue = Queue()
    log_queue = Queue()
    telem_queue = Queue()
    server_ip = 'hyperlooptk1.student.rit.edu'

    start(cmd_queue, log_queue, telem_queue, server_ip)

    while not cmd_queue.empty():
        print cmd_queue.get()    
