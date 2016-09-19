import os.path
import logging
#http://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

#The background is set with 40 plus the number of the color, and the foreground with 30

#These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

def formatter_message(message, use_color = True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message

COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': BLUE,
    'CRITICAL': RED,
    'ERROR': RED
}

def initializeLogger(path, level, name, formatter = None, sout = False, colors = False, client = False):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if formatter is None:
        if colors is True:
            if client == False:
                format_string = "%(levelname)s$RESET: %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
            else:
                format_string = "%(levelname)s$RESET: %(message)s"
            color_format = formatter_message(format_string, True)
            formatter = ColoredFormatter(color_format)
        else:
            formatter = logging.Formatter("%(levelname)s: %(message)s")

    fileHandler = logging.FileHandler(os.path.join(path, name + ".txt"),"w")
    fileHandler.setFormatter(formatter)
    fileHandler.setLevel(level)

    logger.addHandler(fileHandler)
    if sout is True:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color = True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)

