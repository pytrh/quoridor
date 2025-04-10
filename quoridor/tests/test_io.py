import os
import pytest

from pathlib import Path
from quoridor.command import AbandonCommand, MovePawnCommand, PassCommand, PlaceWallCommand
from quoridor.gamestate import GameState
from quoridor.io import ReadWriteHistory
from quoridor.player import Player
from unittest.mock import patch, mock_open

current_dir = Path(__file__).resolve().parent
path_to_history_dir = current_dir / "io"


def test_read_history_from_file():
    history = ReadWriteHistory.read_history(path_to_history_dir / "test_history1.txt")
    expected = [[(1, 'e1-e2'), (2, 'e8v')], [(1, 'e2-d2'), (-1, '')]]

    assert expected == history

    history = ReadWriteHistory.read_history(path_to_history_dir / "test_history2.txt")
    expected = [[(1, 'e1-e2'), (2, 'a10-a9'), (3, 'e2-e3'), (4, 'a9v')], 
                [(1, 'a6h'), (2, 'a9-a8'), (3, 'e4-e5'), (4, 'a8-a7')]]

    assert expected == history

    history = ReadWriteHistory.read_history(
        path_to_history_dir / "test_history_skip.txt"
    )
    expected = [[(1, 'c1-c2'), (2, 'b3h'), (3, 'a3-b3'), (4, 'c2v')], [(1, 'SURRENDER'), (2, 'c5-b5'), (-1, ''), (-1, '')]]

    assert expected == history

    history = ReadWriteHistory.read_history(
        path_to_history_dir / "test_history_with_two_players.txt"
    )
    expected = [[(1, 'e1-e2'), (2, 'a10-a9')], [(1, 'a6v'), (2, 'a9-a8')]]

    assert expected == history

def test_write_history_into_file():
    filename = "output_history.txt"
    turns_to_write = [
        ["1 e1-e2", "2 a10-a9", "3 e2-e3", "4 a9v"],
        ["1 a6v", "2 a9-a8", "3 e4-e5", "4 a8-a7"],
        ["1 e3-e4", "2 a7-a6", "3 e5-e6", "4 a6-a5"],
    ]
    expected_turns = [[(1, 'e1-e2'), (2, 'a10-a9'), (3, 'e2-e3'), (4, 'a9v')], [(1, 'a6v'), (2, 'a9-a8'), (3, 'e4-e5'), (4, 'a8-a7')], [(1, 'e3-e4'), (2, 'a7-a6'), (3, 'e5-e6'), (4, 'a6-a5')]]
    ReadWriteHistory.write_history(path_to_history_dir / filename, turns_to_write)

    history = ReadWriteHistory.read_history(path_to_history_dir / filename)
    assert expected_turns == history

    filename = "output_history2.txt"
    turns_to_write = [
        ["1 e1-e2", "2 a10-a9", "3 e2-e3", "4 a9v"],
        ["1 e3-e4", "2 SURRENDER"],
    ]
    expected_turns = [[(1, 'e1-e2'), (2, 'a10-a9'), (3, 'e2-e3'), (4, 'a9v')], [(1, 'e3-e4'), (2, 'SURRENDER'), (-1, ''), (-1, '')]]
    ReadWriteHistory.write_history(path_to_history_dir / filename, turns_to_write)

    history = ReadWriteHistory.read_history(path_to_history_dir / filename)
    assert expected_turns == history


def test_read_history_from_empty_file():
    history = ReadWriteHistory.read_history(path_to_history_dir / "empty_file.txt")
    expected = []

    assert history == expected


def test_file_not_found_read(capsys):
    ReadWriteHistory.read_history("invalid_file.txt")
    captured = capsys.readouterr()
    assert "Error: The file 'invalid_file.txt' was not found." in captured.out


def test_read_value_error(capsys):
    mock_data = "random data"

    with patch("builtins.open", mock_open(read_data=mock_data)):
        with patch(
            "quoridor.io.ReadWriteHistory._get_game_info_from_file",
            side_effect=ValueError("Invalid file format"),
        ):
            ReadWriteHistory.read_history("fake_file.txt")

    captured = capsys.readouterr()
    assert "Invalid file format" in captured.out


def test_read_io_error(capsys):
    mock_data = "random data"

    with patch("builtins.open", mock_open(read_data=mock_data)):
        with patch(
            "quoridor.io.ReadWriteHistory._get_game_info_from_file",
            side_effect=IOError("IO Error"),
        ):
            ReadWriteHistory.read_history("fake_file.txt")

    captured = capsys.readouterr()
    assert "IO Error" in captured.out


def test_write_io_error(capsys):
    mock_data = "random data"

    with patch("builtins.open", mock_open(read_data=mock_data)) as mock_file:
        mock_file.return_value.write.side_effect = IOError("IO Error")
        ReadWriteHistory.write_history("fake_file.txt", [])

    captured = capsys.readouterr()
    assert "Error: Could not write to file 'fake_file.txt'" in captured.out


def test_error_read_invalid_format(capsys):
    mock_data = "invalid data"

    with patch("builtins.open", mock_open(read_data=mock_data)):
        ReadWriteHistory.read_history("fake_file.txt")

    captured = capsys.readouterr()
    assert "Invalid line for turn: 1" in captured.out


def test_get_game_info_indexerror_valueerror(capsys):
    mock_data = "1. 2"

    with patch("builtins.open", mock_open(read_data=mock_data)):
        game_info = ReadWriteHistory.read_history("fake_file.txt")

    captured = capsys.readouterr()
    assert "Warning: Skipping invalid move None at turn 1" in captured.out
    assert game_info == [[]]


def test_get_game_info_valueerror(capsys):
    mock_data = "TurnOne. 1 A"

    with patch("builtins.open", mock_open(read_data=mock_data)):
        game_info = ReadWriteHistory.read_history("fake_file.txt")

    captured = capsys.readouterr()
    assert "Error processing game data" in captured.out
    assert not game_info

@pytest.fixture
def mock_state():
    # Simuler un GameState avec 2 joueurs placés
    state = GameState(num_players=2)
    state.players = [
        Player(id=0, position=(4, 0), walls_remaining=10, size=9),
        Player(id=1, position=(4, 8), walls_remaining=10, size=9)
    ]
    return state

def test_parse_list_of_str_to_history_surrender(mock_state):
    turns = [[(1, "SURRENDER")]]
    result = ReadWriteHistory.parse_list_of_str_to_history(mock_state, turns)
    
    assert len(result) == 1
    player_id, command = result[0]
    assert player_id == 0  # 1 - 1
    assert isinstance(command, AbandonCommand)

def test_parse_list_of_str_to_history_move(mock_state):
    turns = [[(1, "e1-e2")]]
    result = ReadWriteHistory.parse_list_of_str_to_history(mock_state, turns)
    
    assert len(result) == 1
    player_id, command = result[0]
    assert player_id == 0
    assert isinstance(command, MovePawnCommand)

def test_parse_list_of_str_to_history_wall(mock_state):
    turns = [[(2, "e5h")]]
    result = ReadWriteHistory.parse_list_of_str_to_history(mock_state, turns)
    
    assert len(result) == 1
    player_id, command = result[0]
    assert player_id == 1
    assert isinstance(command, PlaceWallCommand)

def test_parse_list_of_str_to_history_pass(mock_state):
    turns = [[(1, "Pass")]]
    result = ReadWriteHistory.parse_list_of_str_to_history(mock_state, turns)

    assert len(result) == 1
    player_id, command = result[0]
    assert player_id == 0
    assert isinstance(command, PassCommand)