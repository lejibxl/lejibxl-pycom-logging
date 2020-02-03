"""
lejibxl 2020
based on Adafruit logger : https://github.com/adafruit/Adafruit_CircuitPython_Logger.git
"""

import utime
import pycom
from machine import Timer


LEVELS = [(00, 'NOTSET'),
          (10, 'DEBUG'),
          (20, 'INFO'),
          (30, 'WARNING'),
          (40, 'ERROR'),
          (50, 'CRITICAL')]

for value, name in LEVELS:
    globals()[name] = value

def level_for(value):
    """Convert a numberic level to the most appropriate name.

    :param value: a numeric level

    """
    for i in range(len(LEVELS)):
        if value == LEVELS[i][0]:
            return LEVELS[i][1]
        elif value < LEVELS[i][0]:
            return LEVELS[i-1][1]
    return LEVELS[0][1]

class LoggingHandler(object):
    """Abstract logging message handler."""

    def format(self, level, msg):
        """Generate a timestamped message.

        :param level: the logging level
        :param msg: the message to log

        """
        return '{0}: {1} - {2}'.format(utime.ticks_ms() , level_for(level), msg)

    def emit(self, level, msg):
        """Send a message where it should go.
        Place holder for subclass implementations.
        """
        raise NotImplementedError()


class PrintHandler(LoggingHandler):
    """Send logging messages to the console by using print."""

    def emit(self, level, msg):
        """Send a message to teh console.

        :param level: the logging level
        :param msg: the message to log

        """
        print(self.format(level, msg))


class FileHandler(LoggingHandler):

    def __init__(self, filename):
        """Create an instance.

        :param filename: the name of the file to which to write messages

        """
        self._filename = filename

    def format(self, level, msg):
        """Generate a string to log.

        :param level: The level at which to log
        :param msg: The core message

        """
        return super().format(level, msg) + '\r\n'

    def emit(self, level, msg):
        """Generate the message and write it to the UART.

        :param level: The level at which to log
        :param msg: The core message

        """
        with open(self._filename, 'a+') as f:
            f.write(self.format(level, msg))

class rgbledHandler(LoggingHandler):

    def __init__(self):
        """Create an instance.

        :param :

        """

    def format(self, level, msg):
        """Generate led color.

        :param level: The level at which to log
        :param msg: The core message

        """
        return None

    def emit(self, level, msg):
        """Generate the message and write it to the UART.

        :param level: The level at which to log
        :param msg: The core message

        """
        pycom.heartbeat(False)
        if   level == 00 : colour = 0x0000   #NOTSET
        elif level == 10 : colour = 0x0000   #DEBUG
        elif level == 20 : colour = 0x007f00   #INFO
        elif level == 30 : colour = 0x7f7f00   #WARNING
        elif level == 40 : colour = 0x7f0000   #ERROR
        elif level == 50 : colour = 0x7f0000   #CRITICAL
        pycom.rgbled(0x007f00) # green
        Timer.Alarm(handler=lambda u: pycom.heartbeat(True) , s=2)

# The level module-global variables get created when loaded
#pylint:disable=undefined-variable

logger_cache = dict()

def getLogger(name):
    """Create or retrieve a logger by name.

    :param name: the name of the logger to create/retrieve

    """
    if name not in logger_cache:
        logger_cache[name] = Logger()
    return logger_cache[name]

class Logger(object):
    """Provide a logging api."""

    def __init__(self):
        """Create an instance.

        :param handler: what to use to output messages. Defaults to a PrintHandler.

        """
        self._handler = {PrintHandler():0}

    def addHandler(self, hldr, level):
        """Sets the handler of this logger to the specified handler.
        *NOTE* this is slightly different from the CPython equivalent which adds
        the handler rather than replaceing it.

        :param hldr: the handler

        """
        self._handler[hldr] = level

    def log(self, level, format_string, *args):
        """Log a message.

        :param level: the priority level at which to log
        :param format_string: the core message string with embedded formatting directives
        :param args: arguments to ``format_string.format()``, can be empty

        """
        for __handler, __level in self._handler.items():
            if level >= __level:
                __handler.emit(level, format_string % args)

    def debug(self, format_string, *args):
        """Log a debug message.

        :param format_string: the core message string with embedded formatting directives
        :param args: arguments to ``format_string.format()``, can be empty

        """
        self.log(DEBUG, format_string, *args)

    def info(self, format_string, *args):
        """Log a info message.

        :param format_string: the core message string with embedded formatting directives
        :param args: arguments to ``format_string.format()``, can be empty

        """
        self.log(INFO, format_string, *args)

    def warning(self, format_string, *args):
        """Log a warning message.

        :param format_string: the core message string with embedded formatting directives
        :param args: arguments to ``format_string.format()``, can be empty

        """
        self.log(WARNING, format_string, *args)

    def error(self, format_string, *args):
        """Log a error message.

        :param format_string: the core message string with embedded formatting directives
        :param args: arguments to ``format_string.format()``, can be empty

        """
        self.log(ERROR, format_string, *args)

    def critical(self, format_string, *args):
        """Log a critical message.

        :param format_string: the core message string with embedded formatting directives
        :param args: arguments to ``format_string.format()``, can be empty

        """
        self.log(CRITICAL, format_string, *args)
