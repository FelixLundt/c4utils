from typing import Callable
import subprocess
from pathlib import Path
from uuid import uuid4
import hashlib
import json

# Local imports
from ..c4_types import Board, Move, Player, AgentRuntimeError


class SandboxedAgent:
    """
    Runs an agent in a sandboxed Apptainer container for safe execution.
    """

    def __init__(self, sif_path: Path):
        """Initialize the agent runner with either a SIF file or sandbox directory"""
        self.container_path = str(sif_path)
        # Create a short hash of the path (first 4 chars) + random uuid (4 chars)
        path_hash = hashlib.md5(self.container_path.encode()).hexdigest()[:4]
        random_suffix = uuid4().hex[:4]
        self.instance_name = f"{path_hash}_{random_suffix}"
        self.instance = None

    def __enter__(self):
        try:
            # Ensure cleanup of any existing instance with same name
            self.cleanup()
            
            # Start the Apptainer instance 
            result = subprocess.run(
                ["apptainer", "instance", "start",
                 "--fakeroot",
                 "--writable-tmpfs",
                 "--contain",
                 self.container_path,
                 self.instance_name],
                capture_output=True,
                text=True,
                check=True
            )

            # Verify the instance is running
            verify = subprocess.run(
                ["apptainer", "instance", "list"],
                capture_output=True,
                text=True,
                check=True
            )
            
            if self.instance_name not in verify.stdout:
                raise AgentRuntimeError(
                    f"Container failed to start. Start output: {result.stderr}\n"
                    f"Instance list: {verify.stdout}"
                )
            
            return self
        except subprocess.CalledProcessError as e:
            raise AgentRuntimeError(
                f"Failed to start container: {str(e)}\n"
                f"stderr: {e.stderr if hasattr(e, 'stderr') else 'no stderr'}"
            )
        except Exception as e:
            raise AgentRuntimeError(f"Unexpected error starting container: {str(e)}")

    def cleanup(self):
        if self.instance_name:
            try:
                # First check if the instance exists
                result = subprocess.run(
                    ["apptainer", "instance", "list"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # Only try to stop if instance exists
                if self.instance_name in result.stdout:
                    subprocess.run(
                        ["apptainer", "instance", "stop", self.instance_name],
                        capture_output=True,
                        check=True
                    )
            except Exception as e:
                # Log the error but don't raise
                print(f"Warning: cleanup error for {self.instance_name}: {str(e)}")

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
                check=False  # Don't raise on non-zero exit codes
            )
            
            if result.returncode != 0:
                raise AgentRuntimeError(
                    f"Agent failed with exit code {result.returncode}\n"
                    f"stdout: {result.stdout}\n"
                    f"stderr: {result.stderr}"
                )
            
            if result.stderr:
                # Log stderr even on success
                print(f"Warning: Agent produced stderr: {result.stderr}")
                
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise AgentRuntimeError(
                f"Container execution failed:\n"
                f"stdout: {e.stdout if hasattr(e, 'stdout') else 'no stdout'}\n"
                f"stderr: {e.stderr if hasattr(e, 'stderr') else 'no stderr'}"
            )
        except Exception as e:
            raise AgentRuntimeError(f"Unexpected error: {str(e)}")


def get_move_from_container(container: SandboxedAgent, board: Board, player: Player, timeout: float) -> Move:
    """Gets a move from the containerized agent running in the sandbox."""
    try:
        cmd = generate_move_cmd(board, player, timeout)
        output = container.exec_command(cmd)
        
        response = json.loads(output)
        if response['status'] == 'error':
            raise AgentRuntimeError(
                f"Agent failed:\n"
                f"Error: {response['error']}\n"
                f"Traceback:\n{response['traceback']}"
            )
            
        return Move(response['move'])
    except json.JSONDecodeError:
        raise AgentRuntimeError(f"Agent returned invalid JSON: {output}")
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
    return (
        "import json, numpy as np, traceback\n"
        "try:\n"
        "    from agent import generate_move\n"
        "    board = np.array({board})\n"
        "    move = generate_move(board, {player}, {timeout})\n"
        "    print(json.dumps({{'status': 'success', 'move': int(move)}}))\n"
        "except Exception as e:\n"
        "    print(json.dumps({{\n"
        "        'status': 'error',\n"
        "        'error': str(e),\n"
        "        'traceback': traceback.format_exc()\n"
        "    }}))\n"
    ).format(
        board=board.tolist(),
        player=int(player),
        timeout=timeout
    )

def move_time_cmd(board: Board, player: Player, timeout: float) -> str:
    return (f"import time; import json; import numpy as np; from agent import generate_move;"
            f"board = np.array({board.tolist()});"
            f"start_time = time.time();"
            f"move = generate_move(board, {int(player)}, {timeout});"
            f"end_time = time.time();"
            f"print(json.dumps(end_time - start_time))")
