# apply moves
# check for win
# check for draw
# check for stalemate
# check for illegal move
# check for game over
import numpy as np
from .c4_types import Board, Player, Move, BOARD_SIZE, NO_PLAYER, PLAYER1, PLAYER2

def apply_move(board: Board, move: Move, player: Player) -> Board:
    board = board.copy()
    lowest_open_row = np.where(board[:, move] == 0)[0][0]
    board[lowest_open_row, move] = player
    return board

def is_valid_move(board: Board, move: Move, player: Player) -> bool:
    is_correct_type = isinstance(move, Move)
    if not is_correct_type:
        return False
    is_in_bounds = 0 <= move <= BOARD_SIZE[1]
    if not is_in_bounds:
        return False
    is_open_row = board[-1, move] == 0
    if not is_open_row:
        return False
    correct_player = PLAYER1 if np.count_nonzero(board == NO_PLAYER) % 2 == 0 else PLAYER2
    if player != correct_player:
        return False
    return True

def check_win(board: Board, player: Player) -> bool:
    return any(is_win for is_win in [check_win_horizontal(board, player),
                                    check_win_horizontal(board.T, player),
                                    check_win_diagonal(board, player),
                                    check_win_diagonal(np.fliplr(board), player)])

def yield_all_windows(board_slice: np.ndarray, window_size: int) -> np.ndarray:
    for i in range(board_slice.shape[0] - window_size + 1):
        yield board_slice[i:i+window_size]

def check_win_horizontal(board: Board, player: Player) -> bool:
    for row in board:
        for window in yield_all_windows(row, 4):
            if np.all(window == player):
                return True
    return False

def check_win_diagonal(board: Board, player: Player) -> bool:
    window_size = 4
    for diag_index in range(-board.shape[0] + window_size, board.shape[1] - window_size +1):
        diag = np.diagonal(board, diag_index)
        for window in yield_all_windows(diag, window_size):
            if np.all(window == player):
                return True
    return False

def check_winner(board: Board) -> Player | None:
    if check_win(board, PLAYER1):
        return PLAYER1
    elif check_win(board, PLAYER2):
        return PLAYER2
    elif np.all(board != NO_PLAYER):
        return NO_PLAYER
    else:
        return None
