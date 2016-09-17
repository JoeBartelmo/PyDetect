import Tkinter as tk
from Queue import Queue
from Queue import Empty 
import logging
from CustomTextWidget import CustomText
import tkFont
logger = logging.getLogger('mars_logging')

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
        self.log_queue = client_queue_log
        self.cmd = tk.StringVar()

        self.init_ui()
        self.log_loop()

    def init_ui(self):
        """ Initialize visual elements of widget. """
        # entry box for commands
        e = tk.Entry(self, textvariable=self.cmd, width=30)
        e.grid(row=1,column=0, padx=5, pady=5, sticky='w')
        e.bind("<Return>", self.send_command)

        # send button
        send_b = tk.Button(self, text='Send', command=self.send_command)
        send_b.grid(row=1,column=1, padx=5, pady=5, sticky='w')

        # log output
        self.log_output = CustomText(self, bg = 'white', setgrid = True)
        self.log_output.grid(row=0, column=0, columnspan=2, sticky='w', padx=5, pady=5)

        #highlight/bolding
        self.log_output.tag_configure("red", foreground="#ff0000",    font = "Consolas 8 bold" )
        self.log_output.tag_configure("orange", foreground="#ff4500", font = "Consolas 8 bold" )
        self.log_output.tag_configure("italic", foreground="#000000", font = "Consolas 8 italic" )
        self.log_output.tag_configure("purple", foreground="#68228b", font = "Consolas 8 bold" )
        
    def send_command(self):
        """ Send command to client. """
        print('Clicked Send Cmd Button')
        cmd = self.cmd.get()
        if cmd != '':
            print('Piping "' + cmd + '" to the client...')
            self.cmd_queue.put(cmd)   # send command to client
            self.cmd.set('')

    def highlight(self, record, is_command = False):
        '''
        Responsible for highlighting the logging entries
        '''
        recordLevel = getattr(record, 'levelno', 0)        

        #user command
        if is_command:
            self.log_output.highlight_pattern(record.msg, "purple")
            return
        #debug
        elif recordLevel == logging.DEBUG:
            self.log_output.highlight_pattern(record.msg, "italic")
        #warning
        elif recordLevel == logging.WARNING:
            self.log_output.highlight_pattern(record.msg, "orange")
        #error
        elif recordLevel == logging.ERROR or recordLevel == logging.CRITICAL:
            self.log_output.highlight_pattern(record.msg, "red")            

    def log_loop(self):
        try:
            record = self.log_queue.get(timeout=.01)
            print record, ' obtained from queue'
            msgAttr = getattr(record, "msg", record)
            self.log_output.insert(tk.END, msgAttr + '\n')
            self.log_output.see(tk.END)
            #self.log_output.pack()
            self.highlight(record, 'Sending Command' in msgAttr)
            #self.update()
        except Empty:
           pass 
        self.after(100, self.log_loop)

    def quit_(self):
        self.destroy()

if __name__=='__main__':
    root = tk.Tk()
    testQueue = Queue()
    ControlWidget(root, testQueue, testQueue).grid()
    root.update()
    root.mainloop()
