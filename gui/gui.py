import Tkinter as tk
import os
import tkMessageBox
from mainapp import MainApplication
from TopMenu import TopMenu

import logging

MARS_EXIT_COMMAND = 'exit'

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
    
    #kill command destroys mars too
    def killMars():
        client_queue_cmd.put(MARS_EXIT_COMMAND)

    #explicitly close each widget, then destroy root
    def destroyCallback():
        logger.debug('GUI entering destroy callback...')
        result = tkMessageBox.askyesno('Leaving GUI, Should Mars be Disabled?', 'Leaving GUI, should Mars be Disabled?')

        if result:
            killMars()
        menu_.destroy() 
        mainApplication.close_()
        root.destroy()


    # define mainapp instance
    mainApplication = MainApplication(root, client_queue_cmd, client_queue_log, client_queue_telem, server_ip) 
    mainApplication.grid(column = 0, row = 0, sticky="nsew")
    # menu
    menu_ = TopMenu(root, '../gui/operations.json', client_queue_cmd, 'Commands')
    ### Add custom commands here
    menu_.add_menu_item('Refresh Streams', mainApplication.start_streams)
    ###
    menu_.finalize_menu_items()
    root.config(menu=menu_)

    # title and icon
    root.wm_title('Hyperloop Imaging Team')
    img = tk.PhotoImage('../gui/assets/rit_imaging_team.png')
    root.tk.call('wm', 'iconphoto', root._w, img)
    
    #call destroyCallback on clicking X
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
