'''
Random agent that generates a random valid move.

This is an example for what student submissions should expose, and therefore
uses standard python (and numpy) types.
'''

import numpy as np

def generate_move(board: np.ndarray, player: int, timeout: float) -> int:
    """Generate a random valid move."""
    valid_moves = [col for col in range(board.shape[1]) if board[0][col] == 0]
    return np.random.choice(valid_moves)
