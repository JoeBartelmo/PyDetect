from gui.mainapp import MainApplication
import sys
sys.path.insert(0, '../img_proc')

def start_gui(client_queue_in, client_queue_out, server_ip):
    root = tk.Tk()

    # define mainapp instance
    m = MainApplication(root, server_ip, client_queue_in, client_queue_out)
    root.protocol("WM_DELETE_WINDOW", m.close_)

    # title and icon
    root.wm_title('Hyperloop Imaging Team')
    img = tk.PhotoImage(file='../assets/rit_imaging_team.png')
    root.tk.call('wm', 'iconphoto', root._w, img)

    # run forever
    root.mainloop()

if __name__=='__main__':
    from queue import Queue

    in_queue = Queue()
    out_queue = Queue()
    server_ip = '192.0.0.1'

    start_gui(in_queue, out_queue, server_ip)
