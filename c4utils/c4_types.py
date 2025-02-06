from typing import Callable
import numpy as np

# Type aliases
Player = np.int8
Board = np.ndarray
Move = np.int8
AgentFunction = Callable[[Board, Player, float], Move]

BOARD_SIZE = (6, 7)
PLAYER1 = Player(1)
PLAYER2 = Player(2)
NO_PLAYER = Player(0)

class MoveTimeoutError(Exception):
    """Raised when an agent takes too long to generate a move"""
    pass

class AgentRuntimeError(Exception):
    """Raised when an agent encounters an error during move generation"""
    pass