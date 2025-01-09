import pytest
from time import sleep
import docker
from docker.errors import ImageNotFound
import numpy as np
from c4utils.agent_sandbox.timeout import with_timeout, MoveTimeoutError
from c4utils.agent_sandbox.agent_runner import SandboxedAgent, \
    get_generate_move_func_from_container, get_move_from_container
from c4utils.examples.random_agent import generate_move as random_agent
from c4utils.examples.random_timeout_agent import generate_move_with_timeout as random_agent_with_timeout
from c4utils.examples.time_example_agents import move_time_random_agent, move_time_fixed_time_agent
from c4utils.c4_types import Player, Move
from c4utils.tournament.match import play_match

@pytest.fixture(scope='session')
def random_image():
    client = docker.from_env()
    try:
        client.images.get('random_agent')
    except ImageNotFound:
        pytest.skip("Required Docker image 'random_agent' not found")
    return 'random_agent'

@pytest.fixture(scope='session')
def fixed_time_image():
    client = docker.from_env()
    try:
        client.images.get('fixed_time_agent')
    except ImageNotFound:
        pytest.skip("Required Docker image 'fixed_time_agent' not found")
    return 'fixed_time_agent'

def test_time_out_decorator_does_not_raise_error_when_function_finishes_in_time():
    @with_timeout
    def test_function(a, b, timeout):
        sleep(timeout/2)
    timeout = 1
    test_function(1, 2, timeout)

def test_time_out_decorator_raises_error_when_function_finishes_too_late():
    @with_timeout
    def test_function(a, b, timeout):
        sleep(timeout*2)
    with pytest.raises(MoveTimeoutError):
        timeout = 1
        test_function(1, 2, timeout)

def test_time_out_decorator_works_with_random_agent():
    board = np.zeros((6, 7), dtype=Player)
    player = Player(1)
    @with_timeout
    def random_agent_with_timeout(board, player, timeout):
        return random_agent(board, player, timeout)
    timeout = 1
    move = random_agent_with_timeout(board, player, timeout)
    assert 0 <= move <= 6

def test_time_out_with_dumb_generate_move_function():
    board = np.zeros((6, 7), dtype=Player)
    player = Player(1)
    @with_timeout
    def dumb_generate_move(board, player, timeout):
        return Move(0)
    timeout = 1
    move = dumb_generate_move(board, player, timeout)
    assert move == Move(0)

def test_time_out_with_function_that_takes_slightly_less_than_the_timeout():
    timeout = 1
    @with_timeout
    def foo(a, b, timeout):
        sleep(timeout - 0.01)
        return 'finished'
    assert 'finished' == foo(1, 2, timeout)

def test_timeout_decorator_template():
    board = np.zeros((6, 7), dtype=Player)
    player = Player(1)
    timeout = 1.
    move = random_agent_with_timeout(board, player, timeout)
    assert 0 <= move <= 6

@pytest.mark.integration
def test_run_random_agent_from_docker_image(random_image):
    with SandboxedAgent(random_image) as runner:
        board = np.zeros((6, 7), dtype=Player)
        player = Player(1)
        move = get_move_from_container(runner, board, player, timeout=1.)
        assert 0 <= move <= 6

@pytest.mark.integration
def test_container_wrapper_for_gen_move(random_image):
    with SandboxedAgent(random_image) as runner:
        generate_move_func = get_generate_move_func_from_container(runner)
        board = np.zeros((6, 7), dtype=Player)
        player = Player(1)
        move = generate_move_func(board, player, 0.1)
        assert 0 <= move <= 6

@pytest.mark.integration
def test_time_out_with_fixed_time_agent(fixed_time_image):
    timeout = 1
    with SandboxedAgent(fixed_time_image) as runner:
        generate_move_func = get_generate_move_func_from_container(runner)
        board = np.zeros((6, 7), dtype=Player)
        player = Player(1)
        move = generate_move_func(board, player, timeout)
        assert move == Move(0)
@pytest.mark.integration
def test_match_between_containerized_random_agents(random_image):
    timeout = 0.5
    with SandboxedAgent(random_image) as runner:
        generate_move_func = get_generate_move_func_from_container(runner)
        winner, moves, error = play_match(generate_move_func, generate_move_func, move_timeout=timeout)
        assert error is None

@pytest.mark.integration
def test_random_agent_move_time_acceptance():
    timeout = 1.
    move_times = move_time_random_agent(timeout, iterations=10)
    print(move_times)
    assert all(move_time <= 0.1 for move_time in move_times)

@pytest.mark.integration
def test_fixed_time_agent_move_time_acceptance():
    timeout = 1.
    move_times = move_time_fixed_time_agent(timeout, iterations=10)
    overheads = [move_time - timeout/2. for move_time in move_times]
    print(f'Overheads: {overheads}')
    assert all(overhead < 0.01 for overhead in overheads)

