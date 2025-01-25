from typing import Callable
import subprocess
import json
import numpy as np
from pathlib import Path

# Local imports
from ..tournament.match import AgentRuntimeError
from ..c4_types import Board, Move, Player

class SandboxedAgent:
    """
    Runs an agent in a sandboxed Apptainer container for safe execution.
    """

    def __init__(self, sif_path: Path):
        self.sif_path = sif_path
        self.instance_name = f"agent_{hash(str(sif_path))}"  # Unique instance name
        self.instance = None

    def __enter__(self):
        try:
            # Start the Apptainer instance
            subprocess.run(
                ["apptainer", "instance", "start",
                 "--memory", "512m",  # Memory limit
                 "--cpu-shares", "512",  # CPU limit (half of default 1024)
                 self.sif_path,
                 self.instance_name],
                check=True
            )
            return self
        except subprocess.CalledProcessError as e:
            raise AgentRuntimeError(f"Failed to start container: {str(e)}")

    def cleanup(self):
        if self.instance_name:
            try:
                subprocess.run(
                    ["apptainer", "instance", "stop", self.instance_name],
                    check=True
                )
            except Exception:
                # Silently ignore cleanup errors during deletion
                pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def __del__(self):
        """Backup cleanup on deletion"""
        self.cleanup()

    def exec_command(self, cmd: str) -> str:
        """Execute a command in the container instance and return the output"""
        try:
            result = subprocess.run(
                ["apptainer", "exec", f"instance://{self.instance_name}", 
                 "python3", "-c", cmd],
                capture_output=True,
                text=True,
                check=True
            )
            if result.stderr:
                raise AgentRuntimeError(f"Agent failed: {result.stderr}")
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise AgentRuntimeError(f"Container execution failed: {str(e)}")
        except Exception as e:
            raise AgentRuntimeError(f"Unexpected error: {str(e)}")


def get_move_from_container(container: SandboxedAgent, board: Board, player: Player, timeout: float) -> Move:
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
        output = container.exec_command(cmd)
        move = int(output)
        return Move(move)
    except Exception as exc:
        raise AgentRuntimeError(f"Failed to get move: {str(exc)}") from exc

def get_move_time_from_container(container: SandboxedAgent, board: Board, player: Player, timeout: float) -> float:
    cmd = move_time_cmd(board, player, timeout)
    output = container.exec_command(cmd)
    return float(output)

def get_generate_move_func_from_container(container: SandboxedAgent) -> Callable[[Board, Player, float], Move]:
    """
    Gets a move generation function from the containerized agent.
    """
    def generate_move(board: Board, player: Player, timeout: float) -> Move:
        return get_move_from_container(container, board, player, timeout)
    return generate_move

def generate_move_cmd(board: Board, player: Player, timeout: float) -> str:
    return (f"import json; import numpy as np; from agent import generate_move;"
            f"board = np.array({board.tolist()}); "
            f"move = generate_move(board, {int(player)}, {timeout}); "
            f"print(json.dumps(int(move)))")

def move_time_cmd(board: Board, player: Player, timeout: float) -> str:
    return (f"import time; import json; import numpy as np; from agent import generate_move;"
            f"board = np.array({board.tolist()});"
            f"start_time = time.time();"
            f"move = generate_move(board, {int(player)}, {timeout});"
            f"end_time = time.time();"
            f"print(json.dumps(end_time - start_time))")
