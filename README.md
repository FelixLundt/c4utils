# C4Utils

Utility package for Connect Four tournament system.

## Installation

```bash
pip install c4utils
```

## Usage

### Conventions

The following conventions are used throughout the codebase:

- Board is represented as a 6x7 numpy array (rows x columns)
- Empty cells are 0, Player 1 pieces are 1, Player 2 pieces are 2 (all of type `int`)
- Column numbers are 0-6 (left to right, `int`s)
- Row numbers are 0-5 (bottom to top, `int`s)
- Player 1 always moves first


### Agents

Agents should be packages, exposing a `generate_move` function with signature:
```python
def generate_move(board: Board, player: Player, timeout: float) -> Move:
```

Accordingly, the function should:
- Accept a 6x7 numpy array (`board`), player(`player`) and a timeout in seconds (`timeout`).
- Return a column number (0-6).

Ideally, agents keep the time limit automatically, or run so fast that they won't exceed it.

In the tournament, the timeout will be enforced by using the wrapper `with_timeout` from `agent_sandbox.timeout` to add a timeout. This works as shown in `examples.agents.random_timeout_agent`
```python
from typing import cast
from examples.agents.random_agent import generate_move
from c4utils.agent_sandbox.timeout import with_timeout
from c4utils.c4_types import Move, Player, Board

@with_timeout
def generate_move_with_timeout(board: Board, player: Player, timeout: float) -> Move:
    """Generate a random valid move with a timeout."""
    return Move(generate_move(board, cast(Move, player), timeout))
```
based on the random agent from `examples.agents.random_agent`:
```python
import numpy as np
from c4utils.c4_types import Move, Player

def generate_move(board: np.ndarray, player: Player, timeout: float) -> Move:
    valid_moves = [col for col in range(board.shape[1]) if board[-1][col] == 0]
    return Move(np.random.choice(valid_moves)) 
```

If your agent can't stop evaluating at a given time, you could use this decorator to stop your own `generate_move` function shortly before the timeout expires and return some best guess as a move at least.


## Matches

To run games, simply use the `play_match` function from the `tournament.match` 
module and import the desired agents:
```python
from c4utils.tournament.match import play_match
from examples.random_timeout_agent import generate_move_with_timeout

winner, moves, error = play_match(generate_move_with_timeout, 
                                  generate_move_with_timeout)
```
This will run a game with empty starting board and a default of 5 seconds per move.
To change this, provide alternative starting boards or move time via the 
`initial_board` and `move_timeout` keyword arguments, respectively.

## Containerization

Agents can be containerized to run in an isolated environment. The `Dockerfile_random` shows how to containerize the random agent:

1. Use a slim Python base image
2. Install requirements 
3. Copy agent code and timeout wrapper
4. Create a wrapper script that applies the timeout decorator

The wrapper script imports the agent's `generate_move` function and decorates it with `@with_timeout` to enforce the time limit.

This containerization approach ensures agents run consistently and securely in the tournament environment.
