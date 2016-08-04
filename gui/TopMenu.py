import Tkinter as tk
import json
import copy

class TopMenu(tk.Menu):
    def __init__(self, parent, config_file, queue, name):
        tk.Menu.__init__(self, parent)
        self.client_queue_in = queue

        self.init_ui(config_file, name)

    def init_ui(self, config_file, name):
        commands_config = self.load_commands(config_file)

        command_menu = tk.Menu(self, tearoff=0)
        for key, val in commands_config.iteritems():
            
            copyval = '%s' % val['command']
            if val['options'] is None:
                
                command_menu.add_command(label=key, command=self.commandFunc(copyval))

            else:
                options = tk.Menu(self, tearoff=0)
                
                for opt in val['options']:
                    options.add_command(label=opt, command=self.commandFunc(copyval, opt))
                command_menu.add_cascade(label=key, menu=options)

        self.add_cascade(label=name, menu=command_menu)

    def commandFunc(self, cmd, option=False):
        if option == False:
            command = cmd
        else:
            command = cmd + ' ' + option
        
        def f():
            #print id(cmd)  # here from debugging
            self.client_queue_in.put(command)
        return f
    
    def put_thing_on_q(self):
        print self.config()

    def load_commands(self, config_file):
        with open(config_file) as f:
            configuration = \
                json.load(f)#.replace('\n', '').replace(' ', '').replace('\r', '')
        return configuration

if __name__=='__main__':
    from Queue import Queue
    root = tk.Tk()
    q = Queue()
    t = TopMenu(root, 'operations.json', q)
    root.config(menu=t)
    #t.grid()
    root.update()
    print t.winfo_height(), t.winfo_width()
    root.mainloop()

