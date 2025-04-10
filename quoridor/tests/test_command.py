import pytest
from quoridor.gamestate import GameState, AiMode
from quoridor.ai import GreedyAI, MinimaxAI, AlphaBetaAI
from quoridor.command import MovePawnCommand, PlaceWallCommand, Command
from quoridor.direction import Direction
from quoridor.exceptions import InvalidMoveError, PathNotFoundError, InvalidMoveError



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


def test_place_wall_success():
    basic_game_state = GameState(size=7, num_players=2, num_walls=10)
    cmd = PlaceWallCommand(basic_game_state, position=(1, 1), orientation=Direction.H)
    success = cmd.execute()
    assert success
    assert basic_game_state.players[0].walls_remaining == 9  # car un mur a été utilisé

def test_place_wall_out_of_bounds():
    basic_game_state = GameState(size=7, num_players=2, num_walls=10)
    cmd = PlaceWallCommand(basic_game_state, position=(6, 6), orientation=Direction.H)
    with pytest.raises(InvalidMoveError):
        cmd.execute()

def test_place_wall_no_walls_left():
    basic_game_state = GameState(size=7, num_players=2, num_walls=10)
    player = basic_game_state.players[0]
    player.walls_remaining = 0
    cmd = PlaceWallCommand(basic_game_state, position=(1, 1), orientation=Direction.H)
    with pytest.raises(InvalidMoveError):
        cmd.execute()
