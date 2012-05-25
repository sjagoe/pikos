import sys

from pikos.monitor import Monitor
from pikos.recorders.text_stream_recorder import TextStreamRecorder
from pikos.loggers.function_logger import FunctionLogger

def baserecorder():
    """ Factory function that returns a default recorder.
    """
    return TextStreamRecorder(sys.stdout, auto_flush=True)

def log_functions():
    """ Factory function that returns a default function logger.
    """
    return FunctionLogger(baserecorder())

#: Easy to find placeholder for the Monitor decorator class.
monitor = Monitor