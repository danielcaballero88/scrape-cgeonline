"""Utils module for logging."""
import sys
import traceback


def exc_to_str(exception: Exception) -> str:
    """Take an exception and return the traceback in a string."""
    _exc_type, _exc_obj, _exc_tb = sys.exc_info()
    exception_str = str(exception) + "\n" + traceback.format_exc()
    return exception_str
