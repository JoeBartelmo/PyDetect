import Tkinter as tk

class TopMenu(tk.Menu):
    def __init__(self, parent, config_file):
        tk.Menu.__init__(self, parent)

        self.init_ui(config_file)

    def init_ui(self, config_file):
        config = self.load_config(config_file)
        # format is dropdown text, item text, then command
        config = {'help':{'help':'help'}, 'commands':{'stop':{'brake':'1232', 'other':'213ewqf'},'start':'M1103'}}

        for key in config:
            _menu = tk.Menu(self, tearoff=0)
            
            for key_1 in config[key]:
                if type(config[key][key_1]) == str:
                    _menu.add_command(label=key_1, command=config[key][key_1])
                elif type(config[key][key_1]) == dict:
                    _menu_1 = tk.Menu(self, tearoff=0)
                    #print key, key_1, config
                    for key_2 in config[key][key_1]:
                        _menu_1.add_command(label=key_2, command=config[key][key_1][key_2])
                    _menu.add_cascade(label=key_1, menu=_menu_1)
    
            self.add_cascade(label=key, menu=_menu)

    def load_config(self, config_file):
        
        pass

if __name__=='__main__':
    root = tk.Tk()
    t = TopMenu(root, 'config.json')
    root.config(menu=t)
    #t.grid()
    root.update()
    print t.winfo_height(), t.winfo_width()
    root.mainloop()

