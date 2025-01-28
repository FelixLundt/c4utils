import pytest
from time import sleep
from pathlib import Path
import docker
from docker.errors import ImageNotFound
import numpy as np
from c4utils.agent_sandbox.timeout import with_timeout, MoveTimeoutError
from c4utils.c4_types import Player, Move
from c4utils.tournament.match import play_match
from c4utils.agent_sandbox.agent_runner import SandboxedAgent, DevSandboxedAgent, \
    get_generate_move_func_from_container, get_move_from_container
from examples.agents.random_agent import generate_move as random_agent
from examples.agents.random_timeout_agent import generate_move_with_timeout as random_agent_with_timeout
from examples.timing.time_example_agents import move_time_sandboxed_random_agent, move_time_sandboxed_fixed_time_agent
import subprocess


# Development environment fixtures
@pytest.fixture(scope='session')
def random_sandbox():
    """Sandbox directory for development testing"""
    path = Path('/workspace/examples/agent_random')
    assert path.exists(), f"Sandbox directory not found at {path}"
    return path

@pytest.fixture(scope='session')
def fixed_time_sandbox():
    """Sandbox directory for development testing"""
    path = Path('/workspace/examples/agent_fixed_time')
    assert path.exists(), f"Sandbox directory not found at {path}"
    return path

# Production environment fixtures
@pytest.fixture(scope='session')
def random_sif():
    """SIF file for production testing"""
    path = Path('/workspace/examples/agent_random.sif')
    assert path.exists(), f"SIF file not found at {path}"
    return path

@pytest.fixture(scope='session')
def fixed_time_sif():
    """SIF file for production testing"""
    path = Path('/workspace/examples/agent_fixed_time.sif')
    assert path.exists(), f"SIF file not found at {path}"
    return path

# Timeout Tests
@pytest.mark.parametrize("sleep_time, should_raise", [
    (0.5, False),  # Should not raise
    (2, True)      # Should raise
])
def test_time_out_decorator(sleep_time, should_raise):
    @with_timeout
    def test_function(a, b, timeout):
        sleep(sleep_time)
    
    timeout = 1
    if should_raise:
        with pytest.raises(MoveTimeoutError):
            test_function(1, 2, timeout)
    else:
        test_function(1, 2, timeout)

@pytest.mark.parametrize("agent_func, expected_move", [
    (random_agent, lambda move: 0 <= move <= 6),
    (lambda board, player, timeout: Move(0), lambda move: move == Move(0))
])
def test_time_out_with_agents(agent_func, expected_move):
    board = np.zeros((6, 7), dtype=Player)
    player = Player(1)
    @with_timeout
    def agent_with_timeout(board, player, timeout):
        return agent_func(board, player, timeout)
    
    timeout = 1
    move = agent_with_timeout(board, player, timeout)
    assert expected_move(move)

# Sandbox Tests
@pytest.mark.dev
@pytest.mark.integration
@pytest.mark.parametrize("sandbox_fixture, expected_move", [
    ("random_sandbox", lambda move: 0 <= move <= 6),
    ("fixed_time_sandbox", lambda move: move == Move(0))
])
def test_sandboxed_agent(sandbox_fixture, expected_move, request):
    sandbox = request.getfixturevalue(sandbox_fixture)
    with DevSandboxedAgent(sandbox) as runner:
        generate_move_func = get_generate_move_func_from_container(runner)
        board = np.zeros((6, 7), dtype=Player)
        player = Player(1)
        move = generate_move_func(board, player, 1.)
        assert expected_move(move)

# SIF Tests
@pytest.mark.prod
@pytest.mark.integration
@pytest.mark.parametrize("sif_fixture, expected_move", [
    ("random_sif", lambda move: 0 <= move <= 6),
    ("fixed_time_sif", lambda move: move == Move(0))
])
def test_sif_agent(sif_fixture, expected_move, request):
    sif = request.getfixturevalue(sif_fixture)
    with SandboxedAgent(sif) as runner:
        generate_move_func = get_generate_move_func_from_container(runner)
        board = np.zeros((6, 7), dtype=Player)
        player = Player(1)
        move = generate_move_func(board, player, 0.1)
        assert expected_move(move)

# Match Tests
@pytest.mark.dev
@pytest.mark.integration
def test_match_between_sandboxed_agents(random_sandbox):
    timeout = 0.5
    with DevSandboxedAgent(random_sandbox) as player1, DevSandboxedAgent(random_sandbox) as player2:
        generate_move_funcs = [get_generate_move_func_from_container(player1), get_generate_move_func_from_container(player2)]
        winner, moves, error = play_match(generate_move_funcs[0], generate_move_funcs[1], move_timeout=timeout)
        assert error is None

@pytest.mark.prod
@pytest.mark.integration
def test_match_between_agents(random_sif):
    timeout = 0.5
    with SandboxedAgent(random_sif) as player1, SandboxedAgent(random_sif) as player2:
        generate_move_funcs = [get_generate_move_func_from_container(player1), get_generate_move_func_from_container(player2)]
        winner, moves, error = play_match(generate_move_funcs[0], generate_move_funcs[1], move_timeout=timeout)
        assert error is None

# Move Time Acceptance Tests
@pytest.mark.parametrize("move_time_func, timeout, max_time", [
    (move_time_sandboxed_random_agent, 1., 0.1),
    (move_time_sandboxed_fixed_time_agent, 1., 0.01)
])
def test_move_time_acceptance(move_time_func, timeout, max_time):
    move_times = move_time_func(timeout, iterations=10)
    assert all(move_time <= max_time for move_time in move_times)

# Container Tests
@pytest.mark.parametrize("agent_fixture, command", [
    ("random_sandbox", "print('hello')"),
    ("random_sif", "print('hello')")
])
def test_container_startup(agent_fixture, command, request):
    agent = request.getfixturevalue(agent_fixture)
    with SandboxedAgent(agent) as runner:
        try:
            result = runner.exec_command(command)
            assert result == "hello"
        except Exception as e:
            pytest.fail(f"Failed to execute command in container: {str(e)}")

@pytest.mark.parametrize("agent_fixture", [
    ("random_sandbox"),
    ("random_sif")
])
def test_container_cleanup(agent_fixture, request):
    agent = request.getfixturevalue(agent_fixture)
    instance_name = None
    with SandboxedAgent(agent) as runner:
        instance_name = runner.instance_name
        result = subprocess.run(
            ["apptainer", "instance", "list"],
            capture_output=True,
            text=True
        )
        assert instance_name in result.stdout, "Container instance not found in running instances"
    
    result = subprocess.run(
        ["apptainer", "instance", "list"],
        capture_output=True,
        text=True
    )
    assert instance_name not in result.stdout, "Container instance still running after cleanup"
