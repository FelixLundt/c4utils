import numpy as np
from typing import Callable, Union, NewType

# Type aliases
Player = np.int8
Board = np.ndarray
Move = np.int8
AgentFunction = Callable[[Board, Player], Move]

BOARD_SIZE = (6, 7)
PLAYER1 = Player(1)
PLAYER2 = Player(2)
NO_PLAYER = Player(0)
