import pytest
from quoridor.cliengine import CLIEngine
from quoridor.command import (
    UndoCommand,
    RedoCommand,
    QuitCommand,
    SaveAndQuitCommand,
    RestartCommand,
    AbandonCommand,
    SaveCommand,
    PassCommand,
    TimeCommand,
    HistoryCommand,
    HelpCommand,
    MovePawnCommand,
    PlaceWallCommand
)
from quoridor.direction import Direction
from quoridor.exceptions import InvalidCommandError, InvalidMoveError, QuitApp
from quoridor.gamemode import GameMode
from quoridor.gamestate import GameState
from unittest.mock import MagicMock

from quoridor.player import Player

@pytest.fixture
def game_state():
    # Création d'un véritable GameState avec des données minimales
    player1 = Player(id=0, position=(4, 0), walls_remaining=10, size=9)
    player2 = Player(id=1, position=(4, 8), walls_remaining=10, size=9)
    players = [player1, player2]
    
    game_state = GameState(
        size=9,
        current_player_id=0,
        players=players,
        num_players=2,
        num_walls=10,
        game_mode=GameMode.NORMAL
    )
    return game_state


@pytest.fixture
def engine(game_state):
    # Création de l'instance de CLIEngine avec l'état du jeu mocké
    engine = CLIEngine(game_state)
    engine.get_input_from_human_player = MagicMock()
    return engine


def test_execute_place_wall(engine):
    command = PlaceWallCommand(engine.state, (5,5), Direction.H)
    result = command.execute()

    assert result is True
    assert engine.state.wall_exist(5,5,Direction.H)

    command = PlaceWallCommand(engine.state, (6,6), Direction.V)
    result = command.execute()

    assert result is True
    assert engine.state.wall_exist(6,6,Direction.V)

    
    command = PlaceWallCommand(engine.state, (5,5), Direction.V)
    with pytest.raises(InvalidMoveError):
        result = command.execute()
    assert not engine.state.wall_exist(5,5,Direction.V)


def test_execute_move_pawn(engine):
    assert engine.state.current_player.position == (4, 0)
    assert engine.state.current_player.id == 0
    command = MovePawnCommand(engine.state, (4, 0), (4, 1))
    result = command.execute()

    assert result is True
    assert engine.state.players[0].position == (4, 1)


def test_execute_abandon(engine):
    command = AbandonCommand(engine.state, engine.state.current_player.id)
    result = command.execute()

    assert result is True
    assert engine.state.players[0].is_dead is True


@pytest.mark.parametrize("input_str,expected", [
    ("a1", (0, 0)),
    ("c3", (2, 2)),
    ("i9", (8, 8))
])
def test_translate_move_valid(engine, input_str, expected):
    assert engine.translate_move(input_str) == expected

@pytest.mark.parametrize("input_str,expected", [
    ("a1v", (0, 0, Direction.V)),
    ("c3h", (2, 2, Direction.H)),
    ("i9v", (8, 8, Direction.V))
])
def test_translate_wall_valid(engine, input_str, expected):
    # Test pour des entrées valides
    assert engine.translate_wall(input_str) == expected


@pytest.mark.parametrize("input_str", ["z9", "a0", "foo", "12"])
def test_translate_move_invalid(engine, input_str):
    with pytest.raises(ValueError):
        engine.translate_move(input_str)

def test_get_string_from_board(game_state):
    engine = CLIEngine(game_state)
    
    # Test que la fonction retourne une chaîne non vide
    board_str = engine.get_string_from_board()
    assert len(board_str) > 0

def test_get_string_from_board(game_state):
    engine = CLIEngine(game_state)
    # Test pour vérifier la sortie d'un plateau vide
    board_string = engine.get_string_from_board()
    expected = (
        "    1   2   3   4   5   \n"
        "  +---+---+---+---+---+\n"
        "a |   |   |   |   |   |\n"
        "  +---+---+---+---+---+\n"
        "b |   |   |   |   |   |\n"
        "  +---+---+---+---+---+\n"
        "c |   |   |   |   |   |\n"
        "  +---+---+---+---+---+\n"
        "d |   |   |   |   |   |\n"
        "  +---+---+---+---+---+\n"
        "e |   |   |   |   |   |\n"
        "  +---+---+---+---+---+"
    )
    assert board_string.strip() == expected.strip()

def test_get_string_from_board_with_players(game_state):
    engine = CLIEngine(game_state)
    # Test pour vérifier que les joueurs sont bien positionnés
    engine.state.players[0].position = (0, 0)  # Le joueur 1 est en (0, 0)
    engine.state.players[1].position = (2, 2)  # Le joueur 2 est en (2, 2)
    
    board_string = engine.get_string_from_board()
    expected = (
        "    1   2   3   4   5   \n"
        "  +---+---+---+---+---+\n"
        "a | 1 |   |   |   |   |\n"
        "  +---+---+---+---+---+\n"
        "b |   |   |   |   |   |\n"
        "  +---+---+---+---+---+\n"
        "c |   |   | 2 |   |   |\n"
        "  +---+---+---+---+---+\n"
        "d |   |   |   |   |   |\n"
        "  +---+---+---+---+---+\n"
        "e |   |   |   |   |   |\n"
        "  +---+---+---+---+---+"
    )
    assert board_string.strip() == expected.strip()

def test_get_string_from_board_with_walls(engine):
    # Test pour vérifier que les murs sont correctement affichés
    board = engine.state.board
    board.edge_exists.return_value = False  # Aucune liaison entre les cases, donc des murs entre chaque case
    board_string = engine.get_string_from_board()
    # Le plateau généré devrait contenir des murs horizontaux et verticaux
    assert "---" in board_string  # Vérification de la présence de murs horizontaux
    assert "|" in board_string    # Vérification de la présence de murs verticaux


def test_start_game_quit(engine):
    # Mocking des méthodes utilisées dans start_game
    engine.render_board = MagicMock()
    engine.print_remaining_walls = MagicMock()
    engine.start_blitz_turn = MagicMock()
    engine.end_blitz_turn = MagicMock()

    # Simuler la commande "quit" de l'utilisateur
    engine.get_command_from_human_player = MagicMock(return_value=QuitCommand(engine.state))

    # Vérifier que QuitApp est levée et que la boucle se termine
    with pytest.raises(QuitApp):
        engine.start_game()

def test_get_command_undo(engine):
    engine.get_input_from_human_player.return_value = "undo"
    command = engine.get_command_from_human_player()
    assert isinstance(command, UndoCommand)


def test_get_command_redo(engine):
    engine.get_input_from_human_player.return_value = "redo"
    command = engine.get_command_from_human_player()
    assert isinstance(command, RedoCommand)


def test_get_command_quit(engine):
    engine.get_input_from_human_player.return_value = "quit"
    command = engine.get_command_from_human_player()
    assert isinstance(command, QuitCommand)


def test_get_command_save_and_quit(engine):
    engine.get_input_from_human_player.return_value = "quit savefile.txt"
    command = engine.get_command_from_human_player()
    assert isinstance(command, SaveAndQuitCommand)
    assert command.file == "savefile.txt"


def test_get_command_restart(engine):
    engine.get_input_from_human_player.return_value = "restart"
    command = engine.get_command_from_human_player()
    assert isinstance(command, RestartCommand)


def test_get_command_abandon(engine):
    engine.get_input_from_human_player.return_value = "abandon"
    command = engine.get_command_from_human_player()
    assert isinstance(command, AbandonCommand)


def test_get_command_save(engine):
    engine.get_input_from_human_player.return_value = "save"
    command = engine.get_command_from_human_player()
    assert isinstance(command, SaveCommand)


def test_get_command_pass(engine):
    engine.get_input_from_human_player.return_value = "pass"
    command = engine.get_command_from_human_player()
    assert isinstance(command, PassCommand)


def test_get_command_time_blitz(engine):
    engine.get_input_from_human_player.return_value = "time"
    engine.state.game_mode = GameMode.BLITZ
    command = engine.get_command_from_human_player()
    assert isinstance(command, TimeCommand)


def test_get_command_time_non_blitz(engine):
    engine.get_input_from_human_player.return_value = "time"
    engine.state.game_mode = GameMode.NORMAL
    with pytest.raises(InvalidCommandError):
        engine.get_command_from_human_player()


def test_get_command_history(engine):
    engine.get_input_from_human_player.return_value = "history"
    command = engine.get_command_from_human_player()
    assert isinstance(command, HistoryCommand)


def test_get_command_help(engine):
    engine.get_input_from_human_player.return_value = "h"
    command = engine.get_command_from_human_player()
    assert isinstance(command, HelpCommand)

    engine.get_input_from_human_player.return_value = "help"
    command = engine.get_command_from_human_player()
    assert isinstance(command, HelpCommand)


def test_get_command_invalid(engine):
    engine.get_input_from_human_player.return_value = "invalidcommand"
    with pytest.raises(InvalidCommandError):
        engine.get_command_from_human_player()


def test_get_command_pawn_move(engine):
    engine.get_input_from_human_player.return_value = "a1-b2"
    engine.well_formed_pawn_move = MagicMock(return_value=True)
    engine.translate_move = MagicMock(return_value=(1, 2))
    engine.state.players = {0: MagicMock(position=(0, 0))}
    
    command = engine.get_command_from_human_player()
    assert isinstance(command, MovePawnCommand)
    assert command.from_position == (0, 0)
    assert command.to_position == (1, 2)


def test_get_command_wall_placement(engine):
    engine.get_input_from_human_player.return_value = "b2v"
    engine.well_formed_wall_placement = MagicMock(return_value=True)
    engine.translate_wall = MagicMock(return_value=(1, 2, 'V'))
    
    command = engine.get_command_from_human_player()
    assert isinstance(command, PlaceWallCommand)
    assert command.position == (1, 2)
    assert command.orientation == 'V'


def test_get_command_invalid_format(engine):
    engine.get_input_from_human_player.return_value = "invalid move format"
    with pytest.raises(InvalidCommandError):
        engine.get_command_from_human_player()