import inspect

def is_context_manager(obj):
    """ Check if the obj is a context manager """
    # FIXME: this should work for now.
    return hasattr(obj, '__enter__') and hasattr(obj, '__exit__')
