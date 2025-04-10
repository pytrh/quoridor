import pytest
from quoridor.heuristic import (
    total_heuristic,
    runner_heuristic,
    central_control_heuristic,
    aggressive_blocking_heuristic
)
from quoridor.gamestate import GameState
from quoridor.gamemode import AiMode

def test_runner_heuristic_basic():
        g1 = GameState(size = 3,num_players = 2,num_walls = 10, 
                ai_mode = AiMode.MINIMAX , ai_depth = 1)
        g2 = GameState(size = 3,num_players = 2,num_walls = 10, 
                ai_mode = AiMode.MINIMAX , ai_depth = 1)
        assert (runner_heuristic(g1) == runner_heuristic(g2)
                and runner_heuristic(g2) < 0 and runner_heuristic(g1) < 0)
        
        
def test_central_control_heuristic_centered_player():
        g1 = GameState(size = 3,num_players = 2,num_walls = 10, 
                ai_mode = AiMode.MINIMAX , ai_depth = 1)
        g2 = GameState(size = 3,num_players = 2,num_walls = 10, 
                ai_mode = AiMode.MINIMAX , ai_depth = 1)
        assert isinstance(central_control_heuristic(g1), float)
        assert isinstance(central_control_heuristic(g2), float)
        assert (central_control_heuristic(g1) == central_control_heuristic(g2))
        assert (central_control_heuristic(g2) < 0 and central_control_heuristic(g1) < 0)

def test_aggressive_blocking_heuristic():
        g1 = GameState(size = 3,num_players = 2,num_walls = 10, 
                ai_mode = AiMode.MINIMAX , ai_depth = 1)
        g2 = GameState(size = 3,num_players = 2,num_walls = 10, 
                ai_mode = AiMode.MINIMAX , ai_depth = 1)
        assert (aggressive_blocking_heuristic(g2) > 0 and aggressive_blocking_heuristic(g1) > 0)

def test_total_heuristic():
        g1 = GameState(size = 3,num_players = 2,num_walls = 10, 
                ai_mode = AiMode.MINIMAX , ai_depth = 1)
        g2 = GameState(size = 3,num_players = 2,num_walls = 10, 
                ai_mode = AiMode.MINIMAX , ai_depth = 1)
        assert isinstance(total_heuristic(g1), float)
        assert isinstance(total_heuristic(g2), float)
        assert (total_heuristic(g1) == total_heuristic(g2))