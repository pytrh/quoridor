"""
Unit tests for the gamelogic module
"""

import pytest
from quoridor.gamestate import GameState
from quoridor.player import Player


def __check_create_board(game: GameState) -> None:
    """Test that board is created correctly"""
    for i in range(game.size):
        for j in range(game.size):
            assert game.board.node_exists((i, j))

    for i in range(game.size):
        for j in range(game.size):
            if i < game.size - 1:
                assert game.board.edge_exists((i, j), (i + 1, j))
            if j < game.size - 1:
                assert game.board.edge_exists((i, j), (i, j + 1))


def __check_game_parameters(
    game: GameState,
    size: int,
    num_players: int,
    game_mode: bool, # TODO: GameMode not bool
    history: list[list[str]],
) -> None:
    assert game.game_mode == game_mode
    assert game.size == size
    assert game.num_players == num_players
    assert game.history == history


def __check_player(game: GameState, players: list[Player]) -> None:
    assert len(players) == len(game.players)

    for i in range(len(players)):
        for j in range(len(players)):
            if players[j].id == game.players[i].id:
                assert players[j].id == game.players[i].id
                assert players[j].fences_remaining == game.players[i].fences_remaining
                assert players[j].position == game.players[i].position


def test_default_game():
    """Test that the default game is created correctly (2 players)"""
    game = GameState()
    __check_create_board(game)

    __check_game_parameters(game, 9, 2, False, [[]])
    assert game.current_player == 0
    assert game.move_count == 0

    players = [Player(1, (4, 8), 10), Player(0, (4, 0), 10)]
    __check_player(game, players)


def test_game():
    """Test a game with 3 players"""
    game = GameState(size=9, num_players=3, game_mode=False, num_walls=5)
    __check_create_board(game)
    __check_game_parameters(game, 9, 3, False, [[]])
    assert game.current_player == 0
    assert game.move_count == 0
    players = [Player(0, (4, 0), 5), Player(1, (4, 8), 5), Player(2, (0, 4), 5)]
    __check_player(game, players)

    # test a game with 4 players
    game = GameState(size=9, num_players=4, game_mode=False, num_walls=5)
    __check_create_board(game)
    __check_game_parameters(game, 9, 4, False, [[]])
    assert game.current_player == 0
    assert game.move_count == 0
    assert game.players[0].position == (4, 0)
    assert game.players[1].position == (4, 8)
    assert game.players[0].walls_remaining == 10
    assert game.players[1].walls_remaining == 10
    assert game.players[0].id == 0
    assert game.players[1].id == 1
