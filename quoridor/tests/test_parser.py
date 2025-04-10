import pytest
from quoridor.parser import (
    _print_graph,
    get_string_from_board,
    parse_history_to_str,
    parse_state_to_string,
    parse_string_to_graph,
    parse_string_to_state,
)
from quoridor.graph import Graph
from quoridor.gamemode import GameMode
from quoridor.gamestate import GameState
from quoridor.player import Player


def test_parse_string_to_graph_basic():
    board_string = [
        "    1   2   3 ",
        "  +---+---+---+",
        "a |           |",
        "  +   +   +   +",
        "b |           |",
        "  +   +   +   +",
        "c |           |",
        "  +---+---+---+",
    ]

    graph = parse_string_to_graph("\n".join(board_string))

    expected_nodes = [(i, j) for i in range(3) for j in range(3)]
    for node in expected_nodes:
        assert node in graph._graph

    assert (0, 1) in graph._graph[(0, 0)]
    assert (1, 0) in graph._graph[(0, 0)]


def test_parse_string_to_graph_with_wall():
    board_string = [
        "    1   2   3 ",
        "  +---+---+---+",
        "a |           |",
        "  +---+---+   +",
        "b |           |",
        "  +   +   +   +",
        "c |   |       |",
        "  +---+---+---+",
    ]

    graph = parse_string_to_graph("\n".join(board_string))

    assert (1, 0) not in graph._graph[(0, 0)] or (0, 0) not in graph._graph[(1, 0)]
    assert (2, 0) not in graph._graph[(2, 1)] or (2, 1) not in graph._graph[(2, 0)]


def test_parse_string_to_state_minimal():
    state_string = [
        "num_players=2",
        "current_player_id=0",
        "board_size=5",
        "num_walls=10",
        "blitz=False",
        "players=",
        "player_position=2,0",
        "player_walls=5",
        "player_id=0",
        "player_position=2,4",
        "player_walls=5",
        "player_id=1",
        "board =",
        "    1   2   3   4   5",
        "  +---+---+---+---+---+",
        "a |                   |",
        "  +   +   +   +   +   +",
        "b |                   |",
        "  +   +   +   +   +   +",
        "c | 1               2 |",
        "  +   +   +   +   +   +",
        "d |                   |",
        "  +   +   +   +   +   +",
        "e |                   |",
        "  +---+---+---+---+---+",
    ]

    state = parse_string_to_state(state_string)

    assert state.num_players == 2
    assert state.current_player.id == 0
    assert state.size == 5
    assert state.game_mode == GameMode.NORMAL
    assert len(state.players) == 2
    assert state.players[0].position == (2, 0)
    assert state.players[1].position == (2, 4)
    assert state.players[0].walls_remaining == 5
    assert state.players[1].walls_remaining == 5


def test_parse_string_to_state_with_blitz():
    state_string = [
        "num_players=2",
        "current_player_id=1",
        "board_size=5",
        "num_walls=10",
        "blitz=True",
        "players=",
        "player_position=2,0",
        "player_walls=5",
        "player_id=0",
        "player_position=2,4",
        "player_walls=5",
        "player_id=1",
        "board =",
        "    1   2   3   4   5",
        "  +---+---+---+---+---+",
        "a |                   |",
        "  +   +   +   +   +   +",
        "b |                   |",
        "  +   +   +   +   +   +",
        "c | 1               2 |",
        "  +   +   +   +   +   +",
        "d |                   |",
        "  +   +   +   +   +   +",
        "e |                   |",
        "  +---+---+---+---+---+",
    ]

    state = parse_string_to_state(state_string)

    assert state.game_mode == GameMode.BLITZ
    assert state.current_player.id == 1
    assert state.players[0].position == (2, 0)
    assert state.players[1].position == (2, 4)


def test_print_empty_graph(capsys):
    graph = Graph()  # Graphe vide
    _print_graph(graph)

    captured = capsys.readouterr()
    assert captured.out.strip() == "Graph is empty."


def test_print_simple_graph(capsys):
    graph = Graph()
    # Graphe avec un seul noeud (0, 0) sans arêtes
    graph._graph = {(0, 0): set()}

    _print_graph(graph)

    captured = capsys.readouterr()
    expected_output = "O"
    assert captured.out.strip() == expected_output


def test_print_2x1_graph(capsys):
    graph = Graph()
    # Deux noeuds : (0, 0) connecté à (1, 0)
    graph._graph = {(0, 0): {(1, 0)}, (1, 0): {(0, 0)}}

    _print_graph(graph)

    captured = capsys.readouterr()
    expected_output = """O 
 |  
 O"""
    assert captured.out.strip() == expected_output


def test_parse_state_to_string_basic():
    # Création de joueurs simples
    player0 = Player(id=0, position=(4, 0), size=9, walls_remaining=10)
    player1 = Player(id=1, position=(4, 8), size=9, walls_remaining=10)

    # Création de l'état de jeu
    state = GameState(
        size=9,
        current_player_id=0,
        players=[player0, player1],
        num_players=2,
        num_walls=10,
        blitz_time=60,
    )

    result = parse_state_to_string(state)

    expected_output = (
        "num_players = 2\n"
        "current_player_id = 0\n"
        "board_size = 9\n"
        "initial_num_walls = 10\n"
        "blitz = 60\n\n"
        "players =\n\n"
        "player_position = 4, 0\n"
        "player_walls = 10\n"
        "player_id = 0\n\n"
        "player_position = 4, 8\n"
        "player_walls = 10\n"
        "player_id = 1\n\n"
        "board =\n" + get_string_from_board(state) + "\n"
        "history =\n" + parse_history_to_str(state.history, state.num_players)
    )

    assert result == expected_output
