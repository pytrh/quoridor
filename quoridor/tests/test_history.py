import os
from unittest.mock import patch, mock_open
from src.history.read_write_history import ReadWriteHistory

path_to_history_dir = "quoridor/src/history/"

def test_load_file():
    pass

def test_read_history_from_file():
    history = ReadWriteHistory.read_history(path_to_history_dir + "test_history1.txt")
    expected = [["e1-e2", "a10-a9", "e2-e3", "a9v"],
              ["a6v", "a9-a8", "e4-e5", "a8-a7"],
              ["e3-e4", "a7-a6", "e5-e6", "a6-a5"]]
    
    assert expected == history

    history = ReadWriteHistory.read_history(path_to_history_dir +"test_history2.txt")
    expected = [["e1-e2", "a10-a9", "e2-e3", "a9v"],
              ["a6h", "a9-a8", "e4-e5", "a8-a7"]]
    
    assert expected == history

    history = ReadWriteHistory.read_history(path_to_history_dir + "test_history_skip.txt")
    expected = [["e1-e2", "a10-a9", "e2-e3", "a9v"],
              ["a6v", "a9-a8", "skip", "a8-a7"],
              ["e3-e4", "a7-a6", "e5-e6", "a6-a5"]]
    
    assert expected == history

    history = ReadWriteHistory.read_history(path_to_history_dir + "test_history_two_player.txt")
    expected = [["e1-e2", "a10-a9"],
              ["a6v", "a9-a8"]]
    
    assert expected == history

def test_write_history_into_file():
    filename = path_to_history_dir+"test_write_history.txt"
    expectedTurns = [["e1-e2", "a10-a9", "e2-e3", "a9v"],
              ["a6v", "a9-a8", "e4-e5", "a8-a7"],
              ["e3-e4", "a7-a6", "e5-e6", "a6-a5"]]
    ReadWriteHistory.write_history(filename, expectedTurns)

    history = ReadWriteHistory.read_history(filename)
    assert expectedTurns == history

    filenameSkip = path_to_history_dir+"test_write_history_skip.txt"
    expectedTurns = [["e1-e2", "a10-a9", "e2-e3", "a9v"],
                 ["a6v", "a9-a8", "skip", "a8-a7"],
                 ["e3-e4", "a7-a6", "e5-e6", "a6-a5"]]
    ReadWriteHistory.write_history(filenameSkip, expectedTurns)

    history = ReadWriteHistory.read_history(filenameSkip)
    assert expectedTurns == history

    try:
        os.remove(filename)
        os.remove(filenameSkip)
    except FileNotFoundError:
        pass

# Test Négatif

def test_read_history_from_empty_file():
    filename = path_to_history_dir + "test_empty_file.txt"
    history = ReadWriteHistory.write_history(filename, [])
    expected = None

    assert history == expected

    try:
        os.remove(filename)
    except FileNotFoundError:
        pass

def test_file_not_found_read(capsys):
    ReadWriteHistory.read_history("invalid_file.txt")
    captured = capsys.readouterr()
    assert "Error: The file 'invalid_file.txt' was not found." in captured.out

def test_value_error_read(capsys):
    mock_data = "invalid data"

    with patch("builtins.open", mock_open(read_data=mock_data)):
        with patch("src.history.read_write_history.ReadWriteHistory.get_game_info_from_file", side_effect=ValueError("Invalid file format")):
            ReadWriteHistory.read_history("fake_file.txt")

    captured = capsys.readouterr()
    assert "Invalid file format" in captured.out
