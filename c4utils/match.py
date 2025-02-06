import numpy as np
from dataclasses import dataclass, field
from typing import ClassVar, Tuple, Optional
from pathlib import Path
from .c4_types import Board, Player, PLAYER1, PLAYER2, Move, BOARD_SIZE
from . import rules
from .agent_sandbox.agent_runner import SandboxedAgent, get_generate_move_func_from_container

@dataclass
class GameState:
    """
    Represents the state of a game, including the board, current player, and previous moves.
    """
    
    players: ClassVar[Tuple[Player, Player]] = (PLAYER1, PLAYER2)
    board: Board = field(default_factory=lambda: np.zeros(BOARD_SIZE, dtype=Player))
    winner: Player | None = field(init=False, default=None)

    def __post_init__(self):
        self.winner = rules.check_winner(self.board)

    def update(self, move: Move):
        if self.winner is not None:
            raise ValueError(f"Game is already over. Winner: {self.winner}")
        if not rules.is_valid_move(self.board, move, self.current_player):
            raise ValueError(f"Invalid move: {move}. Type: {type(move)}.")
        self.board = rules.apply_move(self.board, move, self.current_player)
        self.winner = rules.check_winner(self.board)

    @property
    def is_game_over(self) -> bool:
        return self.winner is not None
    
    @property
    def current_player(self) -> Player:
        count_players = [np.count_nonzero(self.board == player) for player in self.players]
        return self.players[count_players.index(min(count_players))]


def _play_match(gen_move_func_player_1, gen_move_func_player_2,
               initial_board: Optional[Board] = None,
               move_timeout: float = 5.0) -> tuple[Player, list[Move], Optional[Exception]]:
    """
    Play a match between two agents with a timeout for each move.
    
    Args:
        gen_move_func_player_1: Move generator function for player 1
        gen_move_func_player_2: Move generator function for player 2
        initial_board: Optional starting board state
        move_timeout: Maximum time in seconds allowed for each move (default: 5.0)
    
    Returns:
        Tuple of (winner, moves, error)
    """
    game_state = GameState() if initial_board is None else GameState(board=initial_board)
    moves = []

    while not game_state.is_game_over:
        gen_move_func = gen_move_func_player_1 if game_state.current_player == PLAYER1 else gen_move_func_player_2
        try:
            # Note: The actual move generation and timeout handling should be 
            # implemented in the agent_sandbox.agent_runner module
            current_board = game_state.board.copy()
            move = gen_move_func(current_board, game_state.current_player, move_timeout)
            game_state.update(move)
            moves.append(move)
            
        except Exception as e:
            opponent = PLAYER1 if game_state.current_player == PLAYER2 else PLAYER2
            return opponent, moves, e
    return game_state.winner, moves, None

def play_match(agent_sandbox_sif_1: Path, agent_sandbox_sif_2: Path,
               initial_board: Optional[Board] = None,
               move_timeout: float = 5.0) -> tuple[Player, list[Move], Optional[Exception]]:
    with SandboxedAgent(agent_sandbox_sif_1) as player_1, SandboxedAgent(agent_sandbox_sif_2) as player_2:
        generate_move_func_player_1 = get_generate_move_func_from_container(player_1)
        generate_move_func_player_2 = get_generate_move_func_from_container(player_2)
        return _play_match(generate_move_func_player_1, generate_move_func_player_2, initial_board, move_timeout)