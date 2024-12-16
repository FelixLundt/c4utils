import numpy as np
from typing import cast
from ..types import Board, Player, Move

def generate_move(board: Board, player: Player, timeout: float) -> Move:
    """Generate a random valid move."""
    valid_moves = [col for col in range(7) if board[0][col] == 0]
    return cast(Move, np.int8(np.random.choice(valid_moves))) 