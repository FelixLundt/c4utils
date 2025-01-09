import pytest
import numpy as np
import c4utils.game.rules as rules
from c4utils.c4_types import Player, Move, BOARD_SIZE, NO_PLAYER, PLAYER1, PLAYER2


@pytest.fixture
def empty_board():
    return np.zeros(BOARD_SIZE, dtype=Player)


@pytest.fixture
def filled_board():
    return np.array([[1, 1, 1, 2, 1, 1, 1],
                     [2, 2, 2, 1, 2, 2, 2],
                     [1, 1, 1, 2, 1, 1, 1],
                     [2, 2, 2, 1, 0, 2, 2],
                     [0, 1, 0, 1, 0, 1, 1],
                     [0, 0, 0, 0, 0, 0, 0]])


@pytest.fixture
def drawn_board():
    return np.array([[1, 1, 1, 2, 1, 1, 1],
                     [2, 2, 2, 1, 2, 2, 2],
                     [1, 1, 1, 2, 1, 1, 1],
                     [2, 2, 2, 1, 2, 2, 2],
                     [1, 1, 1, 2, 1, 1, 1],
                     [2, 2, 2, 1, 2, 2, 2]])


@pytest.fixture(params=["0", "a", 2.3, 1.0])
def wrong_move_types(request):
    return request.param


@pytest.fixture(params=[
    np.array([[1, 1, 1, 1, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0]]),
    np.array([[0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 1, 1, 1, 1],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0]])
])
def horizontal_win_boards(request):
    return request.param


@pytest.fixture(params=[
    np.array([[1, 0, 0, 0, 0, 0, 0],
              [0, 1, 0, 0, 0, 0, 0],
              [0, 0, 1, 0, 0, 0, 0],
              [0, 0, 0, 1, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [1, 0, 0, 0, 0, 0, 0]]),
    np.array([[0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [1, 0, 0, 0, 0, 0, 0],
              [0, 1, 0, 0, 0, 0, 0],
              [0, 0, 1, 0, 0, 0, 0],
              [0, 0, 0, 1, 0, 0, 0]]),
    np.array([[0, 0, 0, 1, 0, 0, 0],
              [0, 0, 0, 0, 1, 0, 0],
              [0, 0, 0, 0, 0, 1, 0],
              [0, 0, 0, 0, 0, 0, 1],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0]]),
    np.array([[0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 1, 0, 0, 0],
              [0, 0, 0, 0, 1, 0, 0],
              [0, 0, 0, 0, 0, 1, 0],
              [0, 0, 0, 0, 0, 0, 1]])],
    ids=['bottom_left', 'top_left', 'bottom_right', 'top_right'])
def diagonal_win_boards(request):
    return request.param


def test_move_on_empty_board(empty_board):
    new_board = rules.apply_move(empty_board, Move(0), PLAYER1)
    assert np.array_equal(new_board, np.array([[1, 0, 0, 0, 0, 0, 0],
                                              [0, 0, 0, 0, 0, 0, 0],
                                              [0, 0, 0, 0, 0, 0, 0],
                                              [0, 0, 0, 0, 0, 0, 0],
                                              [0, 0, 0, 0, 0, 0, 0],
                                              [0, 0, 0, 0, 0, 0, 0]]))


def test_move_leaves_original_board_unchanged(empty_board):
    _ = rules.apply_move(empty_board, Move(0), PLAYER1)
    assert np.array_equal(empty_board, np.zeros(BOARD_SIZE, dtype=Player))


def test_move_on_filled_board(filled_board):
    new_board = rules.apply_move(filled_board, Move(4), PLAYER2)
    expected_board = filled_board.copy()
    expected_board[3, 4] = 2
    assert np.array_equal(new_board, expected_board)


def test_if_wrong_type_move_is_invalid(empty_board, wrong_move_types):
    assert not rules.is_valid_move(empty_board, wrong_move_types, PLAYER1)


def test_if_move_out_of_bounds_is_invalid(empty_board):
    assert not rules.is_valid_move(empty_board, 7, PLAYER1)
    assert not rules.is_valid_move(empty_board, -1, PLAYER1)


def test_if_move_on_occupied_column_is_invalid(drawn_board):
    assert not rules.is_valid_move(drawn_board, 0, PLAYER1)


def test_if_move_by_player_2_on_even_turn_is_invalid(empty_board):
    assert not rules.is_valid_move(empty_board, Move(0), PLAYER2)


def test_if_move_by_player_1_on_odd_turn_is_invalid(empty_board):
    odd_board = empty_board.copy()
    odd_board[0, 0] = 1
    assert not rules.is_valid_move(odd_board, Move(0), PLAYER1)


def test_horizontal_win(horizontal_win_boards):
    assert rules.check_win_horizontal(horizontal_win_boards, PLAYER1) is True


def test_diagonal_win_up_right(diagonal_win_boards):
    assert rules.check_win_diagonal(diagonal_win_boards, PLAYER1) is True


def test_diagonal_win_up_right_player_2(diagonal_win_boards):
    assert rules.check_win_diagonal(2 * diagonal_win_boards, PLAYER2) is True


def test_winner_is_player_1(horizontal_win_boards):
    assert rules.check_winner(horizontal_win_boards) == PLAYER1
    assert rules.check_winner(horizontal_win_boards.T) == PLAYER1


def test_winner_is_player_2(diagonal_win_boards):
    assert rules.check_winner(2 * diagonal_win_boards) == PLAYER2
    assert rules.check_winner(2 * diagonal_win_boards.T) == PLAYER2


def test_winner_is_no_player(filled_board):
    assert rules.check_winner(filled_board) is None


def test_winner_is_no_player_when_board_is_full(drawn_board):
    assert rules.check_winner(drawn_board) == NO_PLAYER

def test_yield_all_windows():
    test_array = np.arange(3, 9)
    expected_windows = [np.array([3, 4, 5, 6]), 
                        np.array([4, 5, 6, 7]), 
                        np.array([5, 6, 7, 8])]
    for idx, window in enumerate(rules.yield_all_windows(test_array, 4)):
        assert np.array_equal(window, expected_windows[idx])
