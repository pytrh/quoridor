import pytest
from quoridor.gamestate import GameState
from quoridor.command import MovePawnCommand, PlaceWallCommand, UndoCommand, RedoCommand
from quoridor.direction import Direction
from quoridor.exceptions import InvalidMoveError, NoUndoableCommand, NoRedoableCommand



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