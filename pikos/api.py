
from pikos.monitor import Monitor

def baserecorder(filter_=None):
    """ Factory function that returns a basic recorder.
    """
    import sys
    from pikos.recorders.text_stream_recorder import TextStreamRecorder
    return TextStreamRecorder(sys.stdout, filter_=filter_, auto_flush=True)

def monitor_functions(filter_=None):
    """ Factory function that returns a basic function monitor.
    """
    from pikos.monitors.function_monitor import FunctionMonitor
    return Monitor(FunctionMonitor(baserecorder(filter_=filter_)))

def monitor_lines(filter_=None):
    """ Factory function that returns a basic line monitor.
    """
    from pikos.monitors.line_monitor import LineMonitor
    return Monitor(LineMonitor(baserecorder(filter_=filter_)))

def memory_on_functions(filter_=None):
    """ Factory function that returns a basic line monitor.
    """
    from pikos.monitors.function_memory_monitor import FunctionMemoryMonitor
    return Monitor(FunctionMemoryMonitor(baserecorder(filter_=filter_)))

def memory_on_lines(filter_=None):
    """ Factory function that returns a basic line monitor.
    """
    from pikos.monitors.line_memory_monitor import LineMemoryMonitor
    return Monitor(LineMemoryMonitor(baserecorder(filter_=filter_)))

#: Easy to find placeholder for the Monitor decorator class.
monitor = Monitor
