# C4Utils

Utility package for Connect Four tournament system.

## Installation

```bash
pip install c4utils
```

## Usage

Create an agent by implementing the `generate_move` function:
```python
import numpy as np
from c4utils.agent.interface import Board, Player, Move
def generate_move(board: Board, player: Player) -> Move:
# Your code here
pass
```

The function should:
- Accept a 6x7 numpy array (`board`) and player number (`player`)
- Return a column number (0-6) as `np.int8`
- Complete within 1 second
- Use only allowed imports (numpy, math, random)

To use this package:

1. Create the directory structure
2. Copy all the files
3. Install in development mode:
```bash
pip install -e .
```

4. Run tests:
```bash
pytest
```