import Tkinter as tk

class ControlWidget(tk.Frame):
    """
    This widget is responsible for showing output from the valmar system and
    sending commands to the mars controller.

    Shows a text box for output, including a log of sent commands, and
    an input box with a send button. It is also keybound to 'Return'.

    Args:
        parent: parent window
        client_queue_out: transfers commands back to the controller

    """
    def __init__(self, parent, client_queue_cmd, client_queue_log):
        tk.Frame.__init__(self, parent, bd=2, relief='groove')
        self.parent = parent

        self.cmd_queue = client_queue_cmd

        self.init_ui()

    def init_ui(self):
        """ Initialize visual elements of widget. """
        # entry box for commands
        self.cmd = tk.StringVar()
        e = tk.Entry(self, textvariable=self.cmd, width=30)
        e.grid(row=1,column=0, padx=5, pady=5, sticky='w')
        e.bind("<Return>", self.send_command)

        # send button
        send_b = tk.Button(self, text='Send', command=self.send_command)
        send_b.grid(row=1,column=1, padx=5, pady=5, sticky='w')

        # log label
        self.log_var = tk.StringVar()
        log_w = tk.Label(self, textvariable=self.log_var, width=50, height=15, \
                        bg='white', anchor='sw', justify='left')
        log_w.grid(row=0, column=0, columnspan=2, sticky='w', padx=5, pady=5)

    def send_command(self, event=None):
        """ Send command to client. """
        cmd = self.cmd.get()
        if cmd is not '':
            self.cmd_queue.put(cmd)   # send command to client

            self.log('CMD Sent: '+ cmd)
            self.cmd.set('')
            
    def log(self, item):
        self.log_var.set(self.log_var.get() + '\n'+ item)

if __name__=='__main__':
    from Queue import Queue
    root = tk.Tk()
    ControlWidget(root, Queue()).grid()
    root.update()
    print root.winfo_height(), root.winfo_width()
    root.mainloop()
