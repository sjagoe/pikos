import argparse
from pikos.monitors.api import (FunctionMonitor, LineMonitor, FunctionMemoryMonitor,
                                LineMemoryMonitor)

MONITORS = {'functions': FunctionMonitor,
            'lines': LineMonitor,
            'function_memory': FunctionMemoryMonitor,
            'line_memory': LineMemoryMonitor}

def run_code_under_monitor(script, monitor):
    """Compile the file and run inside the monitor context.

    Parameters
    ----------
    filename : str
       The filename of the script to run.
    
    monitor : object
       The monitor (i.e. context manager object) to use.

    """

    sys.path.insert(0, os.path.dirname(script))
    with open(script, 'rb') as handle:
        code = compile(handle.read(), script, 'exec')

    globs = {
        '__file__': script,
        '__name__': '__main__',
        '__package__': None}

    with monitor:
        exec cmd in globs, None

def MonitorType(monitor_name):
    """Create the monitor from the command arguments. """
    return MONITORS[monitor_name]
    
def main():
    import sys


    description = "Execute the python script inside the pikos monitor context. "
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-m', '--monitor', type=MonitorType, default='functions', 
                        choices=MONITORS.keys(), help='The monitor to use')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), 
                        help='Output results to a file')
    parser.add_argument('--buffered', action='store_true', 
                        help='Use a buffered stream.')
    parser.add_argument('script', help='The script to run')
    args = parser.parse_args()

    stream = args.output if  args.output is not None else sys.stdout
    recorder = TextStreamRecorder(stream, auto_flush=(not args.buffered))
    monitor = args.monitor(recorder=recorder)
    run_code_under_monitor(args.script, monitor)
            
if __name__ == '__main__':
    main()
