# C4Utils

Utility package for Connect Four tournament system.

## Installation

For development, install the package locally from the root of the repository:
```bash
pip install -e .
```

Once released, or to install the latest development version directly from GitHub, you can use:
```bash
pip install git+https://github.com/FelixLundt/c4utils.git
```
(Eventually, it may also be available on PyPI via `pip install c4utils`)

## Usage

### Conventions

The following conventions are used throughout the codebase:

- Board is represented as a 6x7 numpy array (`c4utils.c4_types.Board`), with `dtype=c4utils.c4_types.Player` (which is `numpy.int8`).
- Empty cells are 0.
- Player 1 pieces are `c4utils.c4_types.PLAYER1` (1).
- Player 2 pieces are `c4utils.c4_types.PLAYER2` (2).
- Column numbers are 0-6 (left to right), represented by `c4utils.c4_types.Move` (which is `int`).
- Row numbers are 0-5 (bottom to top, `int`s).
- Player 1 always moves first.


### Agents

Agents should be Python packages exposing a `generate_move` function with the following signature:
```python
from c4utils.c4_types import Board, Player, Move

def generate_move(board: Board, player: Player, timeout: float) -> Move:
    # ... agent logic ...
```

Accordingly, the function must:
- Accept:
    - `board`: A 6x7 NumPy array representing the current game state, with `dtype=Player`.
    - `player`: The current player's identifier (`PLAYER1` or `PLAYER2`).
    - `timeout`: A `float` indicating the remaining time in seconds for the agent to make a move.
- Return:
    - `Move`: An integer column number (0-6) where the agent wishes to place its piece.

Agents are expected to respect the `timeout`. If an agent's internal logic doesn't handle timeouts, the `with_timeout` decorator from `c4utils.agent_sandbox.timeout` can be used. This decorator will raise a `TimeoutError` if the function execution exceeds the specified duration.

Example using `with_timeout` (as seen in `examples.agents.random_timeout_agent`):
```python
from examples.agents.random_agent import generate_move as random_agent_move # Renamed for clarity
from c4utils.agent_sandbox.timeout import with_timeout
from c4utils.c4_types import Move, Player, Board

@with_timeout
def generate_move_with_timeout(board: Board, player: Player, timeout: float) -> Move:
    """Generate a random valid move with a timeout."""
    # The 'random_agent_move' function itself should adhere to the
    # (Board, Player, float) -> Move signature.
    return random_agent_move(board, player, timeout)
```
Based on the random agent from `examples.agents.random_agent`:
```python
import numpy as np
from c4utils.c4_types import Move, Player, Board # Board for type hint clarity

def generate_move(board: Board, player: Player, timeout: float) -> Move: # Added Board type hint
    valid_moves = [col for col in range(board.shape[1]) if board[board.shape[0]-1][col] == 0] # Check top row for validity
    return Move(np.random.choice(valid_moves))
```

If your agent has complex, potentially long-running computations, you should implement logic to periodically check the remaining time and return a best-effort move if the `timeout` is approaching. The `with_timeout` decorator provides a hard cutoff.


## Matches

To run games, simply use the `play_match` function from the `c4utils.tournament.match`
module and import the desired agents' `generate_move` functions:
```python
from c4utils.tournament.match import play_match
from examples.agents.random_timeout_agent import generate_move_with_timeout # Example agent

# Assuming generate_move_agent1 and generate_move_agent2 are compliant agent functions
# winner, moves, error_info = play_match(generate_move_agent1, 
#                                        generate_move_agent2)

# Example with the random_timeout_agent against itself:
winner, moves, error_info = play_match(generate_move_with_timeout, 
                                       generate_move_with_timeout)

if error_info:
    print(f"Game ended due to error: {error_info['player']} - {error_info['message']}")
else:
    print(f"Winner: {winner}, Moves: {moves}")

```
This will run a game with an empty starting board and a default timeout of 5 seconds per move.
To change this, provide alternative starting boards or move times via the
`initial_board` and `move_timeout` keyword arguments, respectively. The `error_info` in the return tuple will contain details if a game ends due to an agent error or timeout.

## Containerization (Tournament Environment)

In the tournament, student agents will be run inside Apptainer (formerly Singularity) containers for isolation and consistent execution environments.

Students will need to provide:
1.  Their agent code (as a Python package exposing the `generate_move` function).
2.  A `requirements.txt` file listing any dependencies.

The tournament system will then use an Apptainer Definition File (`.def`) to build a SIF (Singularity Image Format) container. This definition file will typically:
1.  Start from a base Python image.
2.  Install the dependencies from `requirements.txt`.
3.  Copy the agent's code into the container.
4.  Set up an entry point or execution script that loads the agent's `generate_move` function.

The `with_timeout` decorator (or equivalent timeout enforcement mechanism) will be applied to the agent's `generate_move` function when it's called by the game-playing orchestrator, ensuring that move time limits are strictly enforced within the containerized environment.

This containerization approach ensures that each agent runs with its specified dependencies in a secure and reproducible manner.
