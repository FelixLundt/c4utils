import time
import numpy as np
from c4utils.c4_types import Move, Player

def generate_move(board: np.ndarray, player: Player, timeout: float) -> Move:
    """Generate a random valid move."""
    time.sleep(timeout/2)
    return Move(0)
