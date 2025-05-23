import numpy as np
from .c4_types import Player, AgentFunction, BOARD_SIZE, PLAYER1, PLAYER2, Move
from .rules import is_valid_move

def validate_agent_function(func: AgentFunction, validation_timeout: float) -> tuple[bool, None | Exception]:
    """Validates that an agent function meets the required interface."""
    try:
        valid = all([check_first_move(func, validation_timeout), check_later_move(func, validation_timeout)])
        return valid, None
    except Exception as e:
        return False, e

def check_first_move(func: AgentFunction) -> bool:
    board = np.zeros(BOARD_SIZE, dtype=Player)
    move = func(board, PLAYER1, validation_timeout)
    return is_valid_move(board, Move(move), PLAYER1)

def check_later_move(func: AgentFunction) -> bool:
    board = np.zeros(BOARD_SIZE, dtype=Player)
    board[0, 0] = PLAYER1
    board[0, 1] = PLAYER2
    board[0, 4] = PLAYER1
    board[1, 1] = PLAYER2
    board[1, 2] = PLAYER1
    move = func(board, PLAYER2, validation_timeout)
    return is_valid_move(board, Move(move), PLAYER2)
