import sys

from pikos.monitor import Monitor
from pikos.recorders.text_stream_recorder import TextStreamRecorder
from pikos.monitors.function_monitor import FunctionMonitor

def baserecorder():
    """ Factory function that returns a default recorder.
    """
    return TextStreamRecorder(sys.stdout, auto_flush=True)

def log_functions():
    """ Factory function that returns a default function logger.
    """
    return FunctionMonitor(baserecorder())

#: Easy to find placeholder for the Monitor decorator class.
monitor = Monitor
