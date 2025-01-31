import time
import numpy as np
from c4utils.c4_types import Move, Player

def generate_move(board: np.ndarray, player: Player, timeout: float) -> Move:
    """Generate a dummy move (leftmost column)with a fixed time."""
    time.sleep(timeout/2)
    valid_moves = np.where(board[0, :] == 0)[0]
    return Move(valid_moves[0])
