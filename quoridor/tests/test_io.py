import os
from unittest.mock import patch, mock_open
from quoridor.io import ReadWriteHistory

from pathlib import Path

current_dir = Path(__file__).resolve().parent
path_to_history_dir = current_dir / "/io"


def test_read_history_from_file():
    history = ReadWriteHistory.read_history(path_to_history_dir / "test_history1.txt")
    expected = [
        ["e1-e2", "a10-a9", "e2-e3", "a9v"],
        ["a6v", "a9-a8", "e4-e5", "a8-a7"],
        ["e3-e4", "a7-a6", "e5-e6", "a6-a5"],
    ]

    assert expected == history

    history = ReadWriteHistory.read_history(path_to_history_dir / "test_history2.txt")
    expected = [["e1-e2", "a10-a9", "e2-e3", "a9v"], ["a6h", "a9-a8", "e4-e5", "a8-a7"]]

    assert expected == history

    history = ReadWriteHistory.read_history(
        path_to_history_dir / "test_history_skip.txt"
    )
    expected = [
        ["e1-e2", "a10-a9", "e2-e3", "a9v"],
        ["a6v", "a9-a8", "skip", "a8-a7"],
        ["e3-e4", "a7-a6", "e5-e6", "a6-a5"],
    ]

    assert expected == history

    history = ReadWriteHistory.read_history(
        path_to_history_dir / "test_history_two_players.txt"
    )
    expected = [["e1-e2", "a10-a9"], ["a6v", "a9-a8"]]

    assert expected == history


def test_write_history_into_file():
    filename = "output_history.txt"
    expected_turns = [
        ["e1-e2", "a10-a9", "e2-e3", "a9v"],
        ["a6v", "a9-a8", "e4-e5", "a8-a7"],
        ["e3-e4", "a7-a6", "e5-e6", "a6-a5"],
    ]
    ReadWriteHistory.write_history(filename, expected_turns)

    history = ReadWriteHistory.read_history(filename)
    assert expected_turns == history

    expected_turns = [
        ["e1-e2", "a10-a9", "e2-e3", "a9v"],
        ["a6v", "a9-a8", "skip", "a8-a7"],
        ["e3-e4", "a7-a6", "e5-e6", "a6-a5"],
    ]
    ReadWriteHistory.write_history(filename, expected_turns)

    history = ReadWriteHistory.read_history(filename)
    assert expected_turns == history

    try:
        os.remove(filename)
    except FileNotFoundError:
        pass


# Test Négatif


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
