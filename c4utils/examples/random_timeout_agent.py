'''
Random agent with timeout that generates a random valid move.

This is an example for how student submissions are going to be forced to
use the timeout context manager. We can use internal types here again.
'''
from typing import cast
from .random_agent import generate_move
from c4utils.agent_sandbox.timeout import with_timeout
from c4utils.types import Move, Player, Board


@with_timeout
def generate_move_with_timeout(board: Board, player: Player, timeout: float) -> Move:
    """Generate a random valid move with a timeout."""
    return Move(generate_move(board, cast(int, player), timeout))
