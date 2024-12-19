import pytest
import numpy as np
from c4utils.tournament.match import GameState, play_match
from c4utils.examples.random_timeout_agent import generate_move_with_timeout as random_agent
from c4utils.types import BOARD_SIZE, PLAYER1, PLAYER2, Move, NO_PLAYER

@pytest.fixture
def winning_board_player_1():
    return np.array([[1, 1, 1, 1, 2, 2, 2],
                     [0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0]])

@pytest.fixture
def win_on_next_move_board_player_1(winning_board_player_1):
    win_next_move_board = winning_board_player_1.copy()
    win_next_move_board[0, 3] = NO_PLAYER    
    return win_next_move_board

@pytest.fixture
def board_after_first_move_0():
    return np.array([[1, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0]])

def test_game_state_initialization():
    game_state = GameState()
    assert game_state.board.shape == BOARD_SIZE
    assert game_state.winner is None
    assert game_state.players == (PLAYER1, PLAYER2)

def test_game_state_initialization_with_winning_board(winning_board_player_1):
    game_state = GameState(board=winning_board_player_1)
    assert game_state.winner == PLAYER1

def test_game_state_update_fails_on_invalid_move():
    game_state = GameState()
    with pytest.raises(ValueError):
        game_state.update(Move(-1))

def test_game_state_update_succeeds_on_valid_move(board_after_first_move_0):
    game_state = GameState()
    game_state.update(Move(0))
    assert game_state.winner is None
    assert np.array_equal(game_state.board, board_after_first_move_0)
    
def test_game_state_update_fails_on_game_over(winning_board_player_1):
    game_state = GameState(board=winning_board_player_1)
    with pytest.raises(ValueError):
        game_state.update(Move(0))

def test_game_state_update_succeeds_on_game_over(win_on_next_move_board_player_1):
    game_state = GameState(board=win_on_next_move_board_player_1)
    game_state.update(Move(3))
    assert game_state.winner == PLAYER1

def test_current_player_on_empty_board():
    game_state = GameState()
    assert game_state.current_player == PLAYER1

def test_current_player_on_board_with_one_move(board_after_first_move_0):
    game_state = GameState(board=board_after_first_move_0)
    assert game_state.current_player == PLAYER2

def test_play_match_succeeds_on_game_over(winning_board_player_1):
    winner, moves, error = play_match(lambda board, player: Move(0), lambda board, player: Move(0), initial_board=winning_board_player_1)
    assert winner == PLAYER1
    assert moves == []
    assert error is None

def test_play_match_fails_on_exception():
    winner, moves, error = play_match(lambda board, player, timeout: Move(0), lambda board, player, timeout: 1/0)
    assert winner == PLAYER1
    assert moves == [Move(0)]
    assert isinstance(error, ZeroDivisionError)

def test_random_agent_does_not_fail():
    _, moves, error = play_match(random_agent, lambda board, player, timeout: Move(0))
    assert error is None
    assert len(moves) >= 7