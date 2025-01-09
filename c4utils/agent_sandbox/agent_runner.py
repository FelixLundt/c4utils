from typing import Callable
import docker
from docker.models.containers import Container
from docker.errors import APIError as DockerAPIError, NotFound as DockerNotFound, ContainerError as DockerContainerError

# Local imports
from ..tournament.match import AgentRuntimeError
from ..c4_types import Board, Move, Player


class SandboxedAgent:
    """
    Runs an agent in a sandboxed Docker container for safe execution.
    """

    def __init__(self, image: str):
        self.image = image
        self.client = docker.from_env()
        self.container = None

    def __enter__(self) -> Container:
        self.container = self.client.containers.run(self.image, 
                                                    detach=True, 
                                                    tty=True,
                                                    network_disabled=True,
                                                    mem_limit="512m",
                                                    cpu_period=100000,
                                                    cpu_quota=50000)  # 50% CPU limit
        return self.container

    def cleanup(self):
        if self.container is not None:
            try:
                self.container.stop()
                self.container.remove()
            except Exception:
                # Silently ignore cleanup errors during deletion
                pass
            finally:
                self.container = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def __del__(self):
        """Backup cleanup on deletion"""
        self.cleanup()


def get_move_from_container(container: Container, board: Board, player: Player, timeout: float) -> Move:
    """
    Gets a move from the containerized agent running in the sandbox.
    
    Args:
        container: The containerized agent
        board: The current game board
        player: The player making the move (1 or 2)
        timeout: The time limit for the agent to generate a move
    Returns:
        Move: The selected column (0-6)
        
    Raises:
        MoveTimeoutError: If agent exceeds time limit
        AgentRuntimeError: If agent fails or returns invalid move
    """
    try:
        cmd = generate_move_cmd(board, player, timeout)
        _, (stdout, stderr) = container.exec_run(
            cmd,
            user='100',
            demux=True
        )
        if stderr is not None and len(stderr) > 0:  # Check if there's any error content
            raise AgentRuntimeError(f"Agent failed: {stderr.decode("utf-8")}")

        move = int(stdout.decode("utf-8").strip())

        return Move(move)

    except DockerContainerError as exc:
        raise AgentRuntimeError(f"Container execution failed: {str(exc)}") from exc
    except DockerNotFound as exc:
        raise AgentRuntimeError("Agent container not found") from exc
    except DockerAPIError as exc:
        raise AgentRuntimeError(f"Docker API error: {exc}") from exc
    except Exception as exc:
        raise AgentRuntimeError(f"Unexpected error: {exc}") from exc
    
def get_move_time_from_container(container: Container, board: Board, player: Player, timeout: float) -> float:
    cmd = move_time_cmd(board, player, timeout)
    _, (stdout, stderr) = container.exec_run(
        cmd,
        user='100',
        demux=True
    )
    return float(stdout.decode("utf-8").strip())
    
def get_generate_move_func_from_container(container: Container) -> Callable[[Board, Player, float], Move]:
    """
    Gets a move from the containerized agent running in the sandbox.
    """
    def generate_move(board: Board, player: Player, timeout: float) -> Move:
        return get_move_from_container(container, board, player, timeout)
    return generate_move

def generate_move_cmd(board: Board, player: Player, timeout: float) -> str:
    return (f"python3 -c "
            f"'import json; import numpy as np; from agent import generate_move;"
            f"board = np.array({board.tolist()}); "
            f"move = generate_move(board, {int(player)}, {timeout}); "
            f"print(json.dumps(int(move)))'")

def move_time_cmd(board: Board, player: Player, timeout: float) -> str:
    cmd = (f"python3 -c "
           f"'import time; import json; import numpy as np; from agent import generate_move;"
           f"board = np.array({board.tolist()});"
           f"start_time = time.time();"
           f"move = generate_move(board, {int(player)}, {timeout});"
           f"end_time = time.time();"
           f"print(json.dumps(end_time - start_time))'")
    return cmd
