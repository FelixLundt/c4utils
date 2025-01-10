"""
Example of a minimal valid agent implementation.
Used for testing and demonstration purposes.
"""
import numpy as np
from c4utils.c4_types import Move, Player

def generate_move(board: np.ndarray, player: Player, timeout: float) -> Move:
    valid_moves = [col for col in range(board.shape[1]) if board[-1][col] == 0]
    return Move(np.random.choice(valid_moves)) 