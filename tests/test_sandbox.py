import pytest
from time import sleep
import numpy as np
from c4utils.agent_sandbox.timeout import with_timeout, MoveTimeoutError
from c4utils.examples.random_agent import generate_move as random_agent
from c4utils.examples.random_timeout_agent import generate_move_with_timeout as random_agent_with_timeout
from c4utils.types import Player, Move


def test_time_out_decorator_does_not_raise_error_when_function_finishes_in_time():
    timeout = 1
    @with_timeout(timeout)
    def test_function():
        sleep(timeout/2)
        print("Hello, world!")
    test_function()

def test_time_out_decorator_raises_error_when_function_finishes_too_late():
    timeout = 1
    @with_timeout(timeout)
    def test_function():
        sleep(timeout*2)
        print("Hello, world!")
    with pytest.raises(MoveTimeoutError):
        test_function()

def test_time_out_decorator_works_with_random_agent():
    board = np.zeros((6, 7), dtype=Player)
    player = Player(1)
    timeout = 1
    @with_timeout(timeout)
    def random_agent_with_timeout(board, player, timeout=10. * timeout):
        return random_agent(board, player, timeout)
    move = random_agent_with_timeout(board, player, timeout=1)
    assert 0 <= move <= 6

def test_time_out_with_dumb_generate_move_function():
    board = np.zeros((6, 7), dtype=Player)
    player = Player(1)
    timeout = 1
    @with_timeout(timeout)
    def dumb_generate_move(board, player, timeout=10. * timeout):
        return Move(0)
    move = dumb_generate_move(board, player, timeout=1)
    assert move == Move(0)

def test_time_out_with_function_that_takes_slightly_less_than_the_timeout():
    timeout = 1
    @with_timeout(timeout)
    def foo():
        sleep(timeout - 0.01)
        return 'finished'
    assert 'finished' == foo()

def test_timeout_decorator_template():
    board = np.zeros((6, 7), dtype=Player)
    player = 1
    timeout = 1.
    move = random_agent_with_timeout(board, player, timeout)
    assert 0 <= move <= 6
