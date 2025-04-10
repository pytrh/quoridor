from unittest.mock import patch
import pytest
from quoridor.gamestate import GameState
from quoridor.command import (MovePawnCommand
                            ,PlaceWallCommand
                            ,UndoCommand
                            ,RedoCommand
                            ,RestartCommand
                            ,AbandonCommand
                            ,QuitCommand
                            ,SaveAndQuitCommand)
from quoridor.direction import Direction
from quoridor.exceptions import (InvalidMoveError
                                ,NoUndoableCommand
                                ,NoRedoableCommand
                                , GameOver
                                ,QuitApp)



def test_place_horizontal_wall_valid():
    basic_game_state = GameState(size=7, num_players=2, num_walls=10)
    cmd = PlaceWallCommand(basic_game_state, (2, 2), Direction.H)
    success = cmd.execute()
    assert success
    assert basic_game_state.players[0].walls_remaining == 9


def test_place_vertical_wall_valid():
    basic_game_state = GameState(size=7, num_players=2, num_walls=10)
    cmd = PlaceWallCommand(basic_game_state, (2, 2), Direction.V)
    success = cmd.execute()
    assert success
    assert basic_game_state.players[0].walls_remaining == 9


def test_place_wall_out_of_bounds():
    basic_game_state = GameState(size=7, num_players=2, num_walls=10)
    basic_game_state = GameState(size=7, num_players=2, num_walls=10)
    cmd = PlaceWallCommand(basic_game_state, (6, 6), Direction.H)  # out of bounds
    with pytest.raises(InvalidMoveError):
        cmd.execute()


def test_place_wall_on_existing_wall():
    basic_game_state = GameState(size=7, num_players=2, num_walls=10)
    basic_game_state = GameState(size=7, num_players=2, num_walls=10)
    # Place once
    cmd1 = PlaceWallCommand(basic_game_state, (2, 2), Direction.H)
    cmd1.execute()

    # Try to place on the same spot again
    cmd2 = PlaceWallCommand(basic_game_state, (2, 2), Direction.H)
    with pytest.raises(InvalidMoveError):
        cmd2.execute()


def test_undo_wall():
    basic_game_state = GameState(size=7, num_players=2, num_walls=10)
    cmd = PlaceWallCommand(basic_game_state, (2, 2), Direction.H)
    cmd.execute()
    cmd.undo()
    assert basic_game_state.players[0].walls_remaining == 10


def test_redo_wall():
    basic_game_state = GameState(size=7, num_players=2, num_walls=10)
    cmd = PlaceWallCommand(basic_game_state, (2, 2), Direction.H)
    cmd.execute()
    cmd.undo()
    cmd.redo()
    assert basic_game_state.players[0].walls_remaining == 9




################ Test for MovePawnCommand ################


def test_valid_move_pawn():
    game = GameState(size=7, num_players=2)
    player = game.current_player
    start = player.position
    end = (start[0] - 1, start[1])  # move up

    cmd = MovePawnCommand(game, start, end)
    success = cmd.execute()

    assert success
    assert player.position == end


def test_invalid_move_wrong_start_position():
    game = GameState(size=7, num_players=2)
    wrong_start = (0, 0)
    correct_end = (1, 0)

    cmd = MovePawnCommand(game, wrong_start, correct_end)
    with pytest.raises(InvalidMoveError):
        cmd.execute()


def test_invalid_move_illegal_edge():
    game = GameState(size=7, num_players=2)
    start = game.current_player.position
    invalid_end = (start[0], start[1] + 2)

    cmd = MovePawnCommand(game, start, invalid_end)
    with pytest.raises(InvalidMoveError):
        cmd.execute()


def test_undo_move_pawn():
    game = GameState(size=7, num_players=2)
    player = game.current_player
    start = player.position
    end = (start[0] - 1, start[1])  # move up

    cmd = MovePawnCommand(game, start, end)
    cmd.execute()
    cmd.undo()

    assert player.position == start
    assert game.current_player.id == 1


def test_redo_move_pawn():
    game = GameState(size=7, num_players=2)
    player = game.current_player
    start = player.position
    end = (start[0] - 1, start[1])

    cmd = MovePawnCommand(game, start, end)
    cmd.execute()
    cmd.undo()
    cmd.redo()

    assert player.position == end
    assert game.current_player.id == 0

################ Test for UndoCommand ################

def test_undo_move_pawn():
    basic_game_state = GameState(size=7, num_players=2, num_walls=10)
    state = basic_game_state
    initial_pos = state.players[0].position
    next_pos = (initial_pos[0] + 1, initial_pos[1])

    if not state.board.edge_exists(initial_pos, next_pos):
        pytest.skip("Pas de bord valide pour ce mouvement")

    move_cmd = MovePawnCommand(state, initial_pos, next_pos)
    assert move_cmd.execute()
    state.history.append((state.current_player.id, move_cmd))

    assert state.players[0].position == next_pos

    undo_cmd = UndoCommand(state)
    undo_cmd.execute()
    assert state.players[0].position == initial_pos
    assert state.redo_stack[-1][1] == move_cmd

def test_undo_when_history_empty():
    basic_game_state = GameState(size=7, num_players=2, num_walls=10)
    undo_cmd = UndoCommand(basic_game_state)
    with pytest.raises(NoUndoableCommand):
        undo_cmd.execute()


################ Test for redoCommand ################
def test_redo_wall_placement_success():
    game = GameState(size=7, num_players=2, num_walls=10)
    
    cmd = PlaceWallCommand(game, (2, 2), Direction.H)
    cmd.execute()

    cmd.undo()
    game.redo_stack.append((game.current_player.id, cmd))

    redo_cmd = RedoCommand(game)
    redo_cmd.execute()

    assert game.players[0].walls_remaining == 9
    assert (game.players[0].position == (3, 0))
    assert len(game.history) == 1


def test_redo_stack_empty_raises_exception():
    game = GameState(size=7, num_players=2, num_walls=10)
    redo_cmd = RedoCommand(game)

    with pytest.raises(NoRedoableCommand):
        redo_cmd.execute()


def test_redo_adds_to_history():
    game = GameState(size=7, num_players=2, num_walls=10)
    
    cmd = PlaceWallCommand(game, (1, 1), Direction.V)
    cmd.execute()
    cmd.undo()

    game.redo_stack.append((game.current_player.id, cmd))

    redo_cmd = RedoCommand(game)
    redo_cmd.execute()

    assert game.history[-1][1] == cmd


################### Test for RestartCommand ####################

def test_restart_resets_to_initial_state():
    initial_game = GameState(size=7, num_players=2, num_walls=10)
    game = initial_game.copy_state()
    
    wall_cmd = PlaceWallCommand(game, (2, 2), Direction.H)
    wall_cmd.execute()
    
    assert game.players[0].walls_remaining == 9
    restart_cmd = RestartCommand(game, initial_game)
    restart_cmd.execute()

    assert game.players[0].walls_remaining == 10
    assert game.history == []
    assert game.redo_stack == []
    assert game.players[0].position == initial_game.players[0].position


def test_restart_command_clears_history_and_redo():
    initial_game = GameState(size=7, num_players=2, num_walls=10)
    game = initial_game.copy_state()

    wall_cmd = PlaceWallCommand(game, (1, 1), Direction.H)
    wall_cmd.execute()
    game.history.append((game.current_player.id, wall_cmd))
    game.redo_stack.append((game.current_player.id, wall_cmd))

    assert game.history != []
    assert game.redo_stack != []

    restart_cmd = RestartCommand(game, initial_game)
    restart_cmd.execute()

    assert game.history == []
    assert game.redo_stack == []


def test_restart_command_str():
    game = GameState(size=7, num_players=2, num_walls=10)
    restart_cmd = RestartCommand(game, game)
    assert str(restart_cmd) == "Restart game"


################### Test for AbandonCommand ####################

def test_abandon_command_marks_player_dead_and_decreases_player_count():
    game = GameState(size=7, num_players=2, num_walls=10)
    player_id = 0

    cmd = AbandonCommand(game, player_id)
    result = cmd.execute()

    assert result is True
    assert game.players[player_id].is_dead
    assert game.num_players_remaining == 1


def test_abandon_command_undo_restores_player():
    game = GameState(size=7, num_players=2, num_walls=10)
    player_id = 0

    cmd = AbandonCommand(game, player_id)
    cmd.execute()
    cmd.undo()

    assert not game.players[player_id].is_dead
    assert game.num_players_remaining == 2


def test_abandon_command_redo_marks_player_dead_again():
    game = GameState(size=7, num_players=2, num_walls=10)
    player_id = 0

    cmd = AbandonCommand(game, player_id)
    cmd.execute()
    cmd.undo()
    cmd.redo()

    assert game.players[player_id].is_dead
    assert game.num_players_remaining == 1


################### Test for QuitCommand ###############

def test_quit_command_raises_quit_app():
    game = GameState(size=7, num_players=2, num_walls=10)
    cmd = QuitCommand(game)

    with pytest.raises(QuitApp):
        cmd.execute()

################### Test for SaveAndQuitCommand ###############

@patch('quoridor.io.write_to_file')  # Mock write_to_file
@patch('quoridor.parser.parse_state_to_string')  # Mock parse_state_to_string
def test_save_and_quit_command_saves_and_raises_quit(mock_parse_state_to_string, mock_write_to_file):
    game = GameState(size=7, num_players=2, num_walls=10)
    file_name = 'save_file.txt'

    # Mock the parsing function to return a dummy state
    mock_parse_state_to_string.return_value = 'Dummy state content'

    # Mock the file-writing function to simply pass without errors
    mock_write_to_file.return_value = None

    cmd = SaveAndQuitCommand(game, file_name)

    # Ensure the save happens and QuitApp is raised
    with pytest.raises(QuitApp):
        cmd.execute()

    # Check if the functions were called correctly
    mock_parse_state_to_string.assert_called_once_with(game)
    mock_write_to_file.assert_called_once_with(file_name, 'Dummy state content')