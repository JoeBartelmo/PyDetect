import client_gui

def start_gui(client_queue_in, client_queue_out, server_ip):
    root = tk.Tk()

    # define mainapp instance
    m = client_gui.MainApplication(root, server_ip, client_queue_in, client_queue_out)
    root.protocol("WM_DELETE_WINDOW", m.close_())

    # run forever
    root.mainloop()

if __name__=='__main__':
    from queue import Queue

    in_queue = Queue()
    out_queue = Queue()
    server_ip = '192.0.0.1'

    start_gui(in_queue, out_queue, server_ip)
