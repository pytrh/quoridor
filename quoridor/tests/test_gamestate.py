"""
Unit tests for the gamelogic module
"""

import pytest
from quoridor.ai import AlphaBetaAI, GreedyAI, MinimaxAI
from quoridor.command import Command
from quoridor.gamemode import AiHeuristic, AiMode, GameMode
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
    game_mode: GameMode,
    history: list[Command],
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
                assert players[j].walls_remaining == game.players[i].walls_remaining
                assert players[j].position == game.players[i].position


def test_default_game():
    """Test that the default game is created correctly (2 players)"""
    game = GameState()
    __check_create_board(game)
    __check_game_parameters(game, 9, 2, GameMode.NORMAL, [])
    assert game.current_player.id == 0

    players = [
        Player(1, (4, 8), size=9, walls_remaining=10),
        Player(0, (4, 0), size=9, walls_remaining=10),
    ]
    __check_player(game, players)


def test_game_three_players():
    """Test a game with 3 players"""
    game = GameState(size=9, num_players=3, game_mode=GameMode.NORMAL, num_walls=5)
    __check_create_board(game)
    __check_game_parameters(game, 9, 3, GameMode.NORMAL, [])
    assert game.current_player.id == 0
    players = [
        Player(0, (4, 0), size=9, walls_remaining=5),
        Player(1, (4, 8), size=9, walls_remaining=5),
        Player(2, (0, 4), size=9, walls_remaining=5),
    ]
    __check_player(game, players)


def test_game_four_players():
    """Test a game with 4 players"""
    game = GameState(size=9, num_players=4, game_mode=GameMode.NORMAL, num_walls=10)
    __check_create_board(game)
    __check_game_parameters(game, 9, 4, GameMode.NORMAL, [])
    assert game.current_player.id == 0
    assert game.players[0].position == (4, 0)
    assert game.players[1].position == (4, 8)
    assert game.players[0].walls_remaining == 10
    assert game.players[1].walls_remaining == 10
    assert game.players[0].id == 0
    assert game.players[1].id == 1


def test_game_over():
    game = GameState(size=9, num_players=4, game_mode=GameMode.NORMAL, num_walls=10)
    __check_create_board(game)
    __check_game_parameters(game, 9, 4, GameMode.NORMAL, [])
    assert game.current_player.id == 0
    assert game.players[0].position == (4, 0)

    assert not game.game_over()

    game.players[0].position = (0, 8)
    assert game.game_over()
    game.players[0].position = (4, 0)

    game.players[1].position = (0, 0)
    game.current_player.id = 1
    assert game.game_over()
    game.players[1].position = (4, 8)

    game.players[2].position = (8, 8)
    game.current_player.id = 2
    assert game.game_over()
    game.players[2].position = (0, 4)

    game.players[3].position = (0, 8)
    game.current_player.id = 3
    assert game.game_over()
    game.players[3].position = (8, 4)


def test_backward_player():
    game = GameState(size=9, num_players=4, game_mode=GameMode.NORMAL, num_walls=10)
    __check_create_board(game)
    __check_game_parameters(game, 9, 4, GameMode.NORMAL, [])
    assert game.current_player.id == 0
    assert game.players[0].position == (4, 0)

    game.switch_player()
    assert game.current_player.id == 1

    game.backward_player()
    assert game.current_player.id == 0

    game.backward_player()
    assert game.current_player.id == 3

    game.players[0].is_dead = True
    game.num_players_remaining = game.num_players_remaining - 1
    assert game.num_players_remaining == 3
    game.switch_player()
    assert game.current_player.id == 1


def test_create_ai():
    game = GameState(
        size=9, num_players=4, game_mode=GameMode.NORMAL, num_walls=10, ai_ids={2}
    )
    __check_create_board(game)
    __check_game_parameters(game, 9, 4, GameMode.NORMAL, [])

    assert len(game.ai_controllers) == 1

    depth = 1
    heuristic = AiHeuristic.RUNNER
    assert isinstance(game.create_ai(AiMode.MINIMAX, depth, heuristic), MinimaxAI)
    assert isinstance(game.create_ai(AiMode.ALPHABETA, depth, heuristic), AlphaBetaAI)
    assert isinstance(game.create_ai(AiMode.GREEDY, depth, heuristic), GreedyAI)
