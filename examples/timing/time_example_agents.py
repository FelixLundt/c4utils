"""
Timing examples and benchmarks for different agent implementations.
"""
import time
from typing import Callable
import numpy as np
from c4utils.agent_sandbox.agent_runner import SandboxedAgent, get_move_time_from_container
from c4utils.c4_types import Player
from pathlib import Path

def move_time_sandboxed_random_agent(timeout: float, iterations: int | None = None) -> list[float]:
    with SandboxedAgent(Path('/workspace/examples/agent_random.sif')) as runner:
        board = np.zeros((6, 7), dtype=Player)
        player = Player(1)
        move_times = []
        if iterations is None:
            move_time = get_move_time_from_container(runner, board, player, timeout)
            move_times.append(move_time)
        else: 
            for _ in range(iterations):
                move_time = get_move_time_from_container(runner, board, player, timeout)
                move_times.append(move_time)
    return move_times

def move_time_sandboxed_fixed_time_agent(timeout: float, iterations: int | None = None) -> list[float]:
    with SandboxedAgent(Path('/workspace/examples/agent_fixed_time.sif')) as runner:
        board = np.zeros((6, 7), dtype=Player)
        player = Player(1)
        move_times = []
        if iterations is None:
            move_time = get_move_time_from_container(runner, board, player, timeout)
            move_times.append(move_time)
        else: 
            for _ in range(iterations):
                move_time = get_move_time_from_container(runner, board, player, timeout)
                move_times.append(move_time)
    return move_times

def print_results(move_time_func: Callable[[float, int | None], list[float]],
                  move_times: list[float], timeout: float, start_time: float, end_time: float):
    print(move_time_func.__name__, [f"{t:.3f}" for t in move_times])
    if move_time_func.__name__ == "move_time_fixed_time_agent":
        print(f'Overheads: {[f"{(move_time - timeout/2):.3f}" for move_time in move_times]}')
        print(f'Sleep time: {timeout/2:.3f} seconds')
    print(f"Time taken: {end_time - start_time:.3f} seconds")

def run_move_timing(timeout: float = 1.0, iterations: int = 10):
    print('Running agents in running container:')
    for move_time_func in [move_time_sandboxed_random_agent, move_time_sandboxed_fixed_time_agent]:
        start_time = time.time()
        move_times = move_time_func(timeout, iterations)
        end_time = time.time()
        print_results(move_time_func, move_times, timeout, start_time, end_time)
        print('')
    print('Running agents in new container:')
    for move_time_func in [move_time_sandboxed_random_agent, move_time_sandboxed_fixed_time_agent]:
        start_time = time.time()
        move_times = []
        for _ in range(iterations):
            move_times.append(move_time_func(timeout, None)[0])
        end_time = time.time()
        print_results(move_time_func, move_times, timeout, start_time, end_time)
        print('')
