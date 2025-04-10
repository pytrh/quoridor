import pytest
from quoridor.gamestate import GameState, AiMode
from quoridor.ai import GreedyAI, MinimaxAI, AlphaBetaAI
from quoridor.command import MovePawnCommand, Command
from quoridor.heuristic import (runner_heuristic,
                                central_control_heuristic,
                                aggressive_blocking_heuristic)


def notation_to_coord(pos: str, size: int) -> tuple[int, int]:
    col = ord(pos[0].lower()) - ord("a")
    row = int(pos[1:])
    return (col, size - row)

def parse_move(move: str, size: int) -> tuple[int, int]:
    _, end = move.split("-")
    return notation_to_coord(end, size)


@pytest.fixture
def basic_game_state():
    return GameState(size=3, num_players=2, num_walls=10)

def test_greedy_ai_returns_valid_move(basic_game_state):
    
    ai = GreedyAI(depth=1, heuristic=runner_heuristic)
    move = ai.suggest_move(basic_game_state)
    assert isinstance(move, MovePawnCommand)
    target = parse_move(str(move), basic_game_state.size)
    assert target in basic_game_state.possible_moves(basic_game_state.current_player.id)


def test_minimax_ai_returns_valid_command(basic_game_state):
    ai = MinimaxAI(depth=1, heuristic=runner_heuristic)
    move = ai.suggest_move(basic_game_state)
    assert isinstance(move, Command)
    target = parse_move(str(move), basic_game_state.size)
    assert target in basic_game_state.possible_moves(basic_game_state.current_player.id)
    move.execute()
    assert not basic_game_state.game_over()
    move.undo()

    ai = MinimaxAI(depth=2, heuristic=runner_heuristic)
    move = ai.suggest_move(basic_game_state)
    assert isinstance(move, Command)
    target = parse_move(str(move), basic_game_state.size)
    assert target in basic_game_state.possible_moves(basic_game_state.current_player.id)
    move.execute()
    assert not basic_game_state.game_over()
    move.undo()


def test_alphabeta_ai_returns_valid_command(basic_game_state):
    ai = AlphaBetaAI(depth=1, heuristic=runner_heuristic)
    move = ai.suggest_move(basic_game_state)
    assert isinstance(move, Command)
    target = parse_move(str(move), basic_game_state.size)
    assert target in basic_game_state.possible_moves(basic_game_state.current_player.id)
    move.execute()
    assert not basic_game_state.game_over()
    move.undo()

    ai = AlphaBetaAI(depth=2, heuristic=runner_heuristic)
    move = ai.suggest_move(basic_game_state)
    assert isinstance(move, Command)
    target = parse_move(str(move), basic_game_state.size)
    assert target in basic_game_state.possible_moves(basic_game_state.current_player.id)
    move.execute()
    assert not basic_game_state.game_over()
    move.undo()
