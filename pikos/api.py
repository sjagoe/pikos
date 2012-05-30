import sys

from pikos.monitor import Monitor
from pikos.recorders.text_stream_recorder import TextStreamRecorder
from pikos.monitors.function_monitor import FunctionMonitor

def baserecorder(filter_):
    """ Factory function that returns a default recorder.
    """
    return TextStreamRecorder(sys.stdout, filter_=filter_, auto_flush=True)

def log_functions(filter_):
    """ Factory function that returns a default function logger.
    """
    return FunctionMonitor(baserecorder(filter_=filter_))

#: Easy to find placeholder for the Monitor decorator class.
monitor = Monitor