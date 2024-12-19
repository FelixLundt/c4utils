import numpy as np
from ..types import Player, Move, AgentFunction, BOARD_SIZE

def validate_agent_function(func: AgentFunction) -> bool:
    """Validates that an agent function meets the required interface."""
    try:
        board = np.zeros((6, 7), dtype=Player)
        move = func(board, Player(1))
        return isinstance(move, (int, Move)) and 0 <= move < BOARD_SIZE[1]
    except Exception as e:
        print(f"Agent validation failed: {e}")
        return False

