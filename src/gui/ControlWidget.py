import Tkinter as tk

class ControlWidget(tk.Frame):
    def __init__(self, parent, p=None):
        tk.Frame.__init__(self, parent, bd=2, relief='groove')
        self.parent = parent

        self.init_ui()

    def init_ui(self):
        self.cmd = tk.StringVar()
        e = tk.Entry(self, textvariable=self.cmd, width=27)
        e.grid(row=1,column=0)
        e.bind("<Return>", self.send_command)

        tk.Button(self, text='SEND', command=self.send_command).grid(row=1,column=1, padx=5, pady=5)

        self.log = tk.StringVar()
        tk.Label(self, textvariable=self.log, bg='white', width=37, height=30,anchor='sw', justify='left').grid(row=0,column=0, columnspan=2, sticky='w', padx=5, pady=5)

    def send_command(self, event=None):
        cmd = self.cmd.get()
        if cmd is not '':
            self.log.set(self.log.get() + '\nCMD SENT: '+ cmd)
            self.cmd.set('')
            pass # FIXME ACTUALLY SEND CMD

    def log(self, item):
        if type(item) is str:
            self.log.set(self.log.get() + '\nLOG: '+ item)

if __name__=='__main__':
    root = tk.Tk()
    ControlWidget(root).grid()
    root.update()
    print root.winfo_height(), root.winfo_width()
    root.mainloop()
