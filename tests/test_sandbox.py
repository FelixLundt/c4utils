import pytest
from time import sleep
from pathlib import Path
import numpy as np
from c4utils.agent_sandbox.timeout import with_timeout, MoveTimeoutError
from c4utils.c4_types import Player, Move
from c4utils.match import _play_match
from c4utils.agent_sandbox.agent_runner import SandboxedAgent, get_generate_move_func_from_container
from examples.agents.random_agent import generate_move as random_agent
from examples.timing.time_example_agents import move_time_sandboxed_random_agent, move_time_sandboxed_fixed_time_agent
import subprocess


@pytest.fixture(scope='session')
def random_sandbox():
    """SIF file for production testing"""
    path = Path('/workspace/examples/agent_random.sif')
    assert path.exists(), f"SIF file not found at {path}"
    return path

@pytest.fixture(scope='session')
def fixed_time_sandbox():
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
@pytest.mark.integration
@pytest.mark.parametrize("sandbox_fixture, expected_move", [
    ("random_sandbox", lambda move: 0 <= move <= 6),
    ("fixed_time_sandbox", lambda move: move == Move(0))
])
def test_sandboxed_agent(sandbox_fixture, expected_move, request):
    sandbox = request.getfixturevalue(sandbox_fixture)
    with SandboxedAgent(sandbox) as runner:
        generate_move_func = get_generate_move_func_from_container(runner)
        board = np.zeros((6, 7), dtype=Player)
        player = Player(1)
        move = generate_move_func(board, player, 1.)
        assert expected_move(move)

# Match Tests
@pytest.mark.integration
def test_match_between_sandboxed_agents(random_sandbox):
    timeout = 0.5
    with SandboxedAgent(random_sandbox) as player1, SandboxedAgent(random_sandbox) as player2:
        generate_move_funcs = [get_generate_move_func_from_container(player1), get_generate_move_func_from_container(player2)]
        winner, moves, error = _play_match(generate_move_funcs[0], generate_move_funcs[1], move_timeout=timeout)
        assert error is None

# Move Time Acceptance Tests
@pytest.mark.integration
@pytest.mark.parametrize("move_time_func, timeout, max_time", [
    (move_time_sandboxed_random_agent, 1., 0.15),
    (move_time_sandboxed_fixed_time_agent, 1., 0.05)
])
def test_move_time_acceptance(move_time_func, timeout, max_time):
    move_times = move_time_func(timeout, iterations=10)
    assert all(move_time <= max_time for move_time in move_times[1:])

# Container Tests
@pytest.mark.parametrize("agent_fixture, command", [
    ("random_sandbox", "print('hello')"),
    ("fixed_time_sandbox", "print('hello')")
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
    ("fixed_time_sandbox")
])
def test_container_cleanup(agent_fixture, request):
    agent = request.getfixturevalue(agent_fixture)
    instance_name = None
    with SandboxedAgent(agent) as runner:
        instance_name = runner.instance_name
        result = subprocess.run(
            ["apptainer", "instance", "list"],
            capture_output=True,
            text=True, check=True
        )
        assert instance_name in result.stdout, "Container instance not found in running instances"
    
    result = subprocess.run(
        ["apptainer", "instance", "list"],
        capture_output=True,
        text=True, check=True
    )
    assert instance_name not in result.stdout, "Container instance still running after cleanup"
