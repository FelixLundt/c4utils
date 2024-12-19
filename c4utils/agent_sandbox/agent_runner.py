import importlib.util
import signal
from typing import Optional, Callable, Any
from pathlib import Path
from contextlib import contextmanager
import docker
from ..tournament import MoveTimeoutError, AgentRuntimeError
from ..types import Board, Player, Move

TIME_LIMIT = 1.0  # 1 second per move

class TimeoutException(Exception):
    pass

@contextmanager
def time_limit(seconds: float):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    
    signal.signal(signal.SIGALRM, signal_handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)

class AgentRunner:
    def __init__(self, timeout: float = 5.0):
        self.client = docker.from_env()
        self.timeout = timeout

    def run_agent(self, container_id: str, board: Board, player: Player) -> Move:
        try:
            with time_limit(self.timeout):
                result = self.client.containers.get(container_id).exec_run(
                    cmd=[...],  # container execution logic
                )
                return process_move(result)
        except TimeoutException:
            raise MoveTimeoutError(f"Agent took longer than {self.timeout}s")
        except docker.errors.ContainerError as e:
            raise AgentRuntimeError(f"Container execution failed: {str(e)}")
        except docker.errors.APIError as e:
            raise AgentRuntimeError(f"Docker API error: {str(e)}")

def process_move(result: Any) -> Move:
    return Move(result)
