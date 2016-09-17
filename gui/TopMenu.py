import Tkinter as tk
import json
import copy

import logging
logger = logging.getLogger('mars_logging')

class TopMenu(tk.Menu):
    '''
    This class loads in a json file from "config_file"
    and dynamically generates functions based off of the commands
    specified within. Additionally you may define custom commands
    in the top menu in the init_ui method

    Note: Our current json file is operations.json defined locally to
        this file
    '''
    def __init__(self, parent, config_file, queue, name):
        tk.Menu.__init__(self, parent)
        self.client_queue_in = queue
        self.name = name

        self.command_menu = tk.Menu(self, tearoff = 0)
        self.client_menu = tk.Menu(self, tearoff = 0)
        self.init_ui(config_file, name)

    def init_ui(self, config_file, name):
        commands_config = self.load_commands(config_file)

        for key, val in commands_config.iteritems():
            copyval = '%s' % val['command']
            if val['options'] is None:
                self.command_menu.add_command(label=key, command=self.commandFunc(copyval))
            else:
                options = tk.Menu(self, tearoff=0)
                
                for opt in val['options']:
                    options.add_command(label=opt, command=self.commandFunc(copyval, opt))
                self.command_menu.add_cascade(label=key, menu=options)

    def add_menu_item(self, commandName, function, menuRoot = 'client'):
        '''
        Adds a new menu item to the TopMenu. 
        name: Displayed name of the command
        function: callback function assigned when button is clicked
        root: MenuItem to append the new operation under
            client: Client Commands item
            server: Server Commands Item
            None: Root level
        '''
        print 'damn', menuRoot
        if menuRoot == 'client':
            self.client_menu.add_command(label=commandName, command = function)
        if menuRoot == 'server':
            self.command_menu.add_command(label=commandName, command = function)
        elif menuRoot is None:
            self.add_command(label=commandName, command = function)

    def finalize_menu_items(self):  
        '''
        Adds the menu items this menu
        '''
        #updates topmenu with given command_menu
        self.add_cascade(label = self.name, menu=self.command_menu)
        #seperate clientside Commands
        self.add_cascade(label = 'Client Commands', menu = self.client_menu)
    
    def commandFunc(self, cmd, option=False):
        '''
        Because of memory referencing in python, we use a functional technique
        to avoid referencing the same variable the whole time.
        '''
        if option == False:
            command = cmd
        else:
            command = cmd + ' ' + option
        
        def topMenuFunctionReference():
            logger.debug('Piping "' + command + '" to the client')
            self.client_queue_in.put(command)
        
        return topMenuFunctionReference

    def load_commands(self, config_file):
        '''
        Loads in local Command json file
        '''
        with open(config_file) as f:
            configuration = \
                json.load(f)
        return configuration

if __name__=='__main__':
    from Queue import Queue
    root = tk.Tk()
    q = Queue()
    t = TopMenu(root, '../gui/operations.json', q)
    root.config(menu=t)
    #t.grid()
    root.update()
    print t.winfo_height(), t.winfo_width()
    root.mainloop()

