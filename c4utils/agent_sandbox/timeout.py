import signal
from functools import wraps
from typing import TypeVar, Callable, Any
from contextlib import contextmanager

class MoveTimeoutError(Exception):
    """Raised when function execution exceeds time limit"""
    pass

@contextmanager
def timeout(seconds: float):
    """Context manager that raises TimeoutError if block execution exceeds time limit"""
    def signal_handler(signum, frame):
        raise MoveTimeoutError(f"Execution timed out after {seconds} seconds")

    # Set the signal handler and alarm
    signal.signal(signal.SIGALRM, signal_handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    
    try:
        yield
    finally:
        # Disable the alarm
        signal.setitimer(signal.ITIMER_REAL, 0)

F = TypeVar('F', bound=Callable[..., Any])

def with_timeout(func: F) -> F:
    """
    Decorator that applies timeout to a function.
    Expects the function to have timeout as its third argument.
    
    Usage:
        @with_timeout
        def generate_move(board, player, timeout) -> Move:
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        _, _, timeout_value = args
        with timeout(timeout_value):
            return func(*args, **kwargs)
    return wrapper