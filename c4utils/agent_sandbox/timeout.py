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

def with_timeout(seconds: float) -> Callable[[F], F]:
    """
    Decorator that applies timeout to a function.
    
    Usage:
        @with_timeout(5.0)
        def generate_move(board, player, timeout) -> Move:
            ...
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with timeout(seconds):
                return func(*args, **kwargs)
        return wrapper
    return decorator 