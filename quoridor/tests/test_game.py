"""
Unit tests for the gamelogic module
"""

import pytest
from src.gamelogic import GameLogic
from src.gamestate import GameState


def test_create_game():
    """Test that the game is created correctly"""
    game = GameState()
    for i in range(game.size):
        for j in range(game.size):
            assert game.board.node_exists((i, j))

    for i in range(game.size):
        for j in range(game.size):
            if i < game.size - 1:
                game.board.edge_exists((i, j), (i + 1, j))
            if j < game.size - 1:
                game.board.edge_exists((i, j), (i, j + 1))

    assert game.current_player == 0
    assert len(game.players) == 2
    assert game.blitz_mode == False
    assert game.size == 9
    assert game.move_count == 0
    assert game.players[0].position == (4, 0)
    assert game.players[1].position == (4, 8)
    assert game.players[0].fences_remaining == 10
    assert game.players[1].fences_remaining == 10
    assert game.players[0].id == 0
    assert game.players[1].id == 1
