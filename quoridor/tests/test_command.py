import pytest
from quoridor.gamestate import GameState, AiMode
from quoridor.ai import GreedyAI, MinimaxAI, AlphaBetaAI
from quoridor.command import MovePawnCommand, PlaceWallCommand, Command
from quoridor.direction import Direction
from quoridor.exceptions import InvalidMoveError, PathNotFoundError


@pytest.fixture
def basic_game_state():
    return GameState(size=7, num_players=2, num_walls=10)



def test_place_horizontal_wall_valid():
    cmd = PlaceWallCommand(basic_game_state(), (2, 2), Direction.H)
    success = cmd.execute()
    assert success
    assert basic_game_state().players[0].walls_remaining == 9


def test_place_vertical_wall_valid():
    cmd = PlaceWallCommand(basic_game_state(), (2, 2), Direction.V)
    success = cmd.execute()
    assert success
    assert basic_game_state().players[0].walls_remaining == 9


def test_place_wall_out_of_bounds():
    cmd = PlaceWallCommand(basic_game_state(), (6, 6), Direction.H)  # out of bounds
    with pytest.raises(InvalidMoveError):
        cmd.execute()


def test_place_wall_on_existing_wall():
    # Place once
    cmd1 = PlaceWallCommand(basic_game_state(), (2, 2), Direction.H)
    cmd1.execute()

    # Try to place on the same spot again
    cmd2 = PlaceWallCommand(basic_game_state(), (2, 2), Direction.H)
    with pytest.raises(InvalidMoveError):
        cmd2.execute()


def test_undo_wall():
    cmd = PlaceWallCommand(basic_game_state(), (2, 2), Direction.H)
    cmd.execute()
    cmd.undo()
    assert basic_game_state().players[0].walls_remaining == 10


def test_redo_wall():
    cmd = PlaceWallCommand(basic_game_state(), (2, 2), Direction.H)
    cmd.execute()
    cmd.undo()
    cmd.redo()
    assert basic_game_state().players[0].walls_remaining == 9