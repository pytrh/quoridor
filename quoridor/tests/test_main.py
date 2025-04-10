import configparser
import importlib
import logging
import os
import sys
import pytest
from unittest import mock
from unittest.mock import patch
from quoridor.main import (
    load_default_config,
    main,
    restore_default_config_file,
    setup_logging,
    update_config_file,
    update_default_config,
    configure_game,
    parse_args,
    initialize_game_state,
    open_file,
)
from quoridor.config import DEFAULT_AI_HEURISTIC, DEFAULT_AI_MODE, DEFAULT_GAME_MODE
from quoridor.gamemode import GameMode, AiHeuristic, AiMode
from quoridor.io import ReadWriteHistory

DEFAULT_CONFIG_FILE = ".quoridorrc_test"
CONFIG_FILE = "config_test.py"

# Begin test - configparser


@pytest.fixture
def mock_config_files():
    if os.path.exists(DEFAULT_CONFIG_FILE):
        os.remove(DEFAULT_CONFIG_FILE)
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)

    with open(DEFAULT_CONFIG_FILE, "w") as f:
        f.write(
            "[Default]\nsize=9\nplayers=2\nwalls=10\nmode=normal\ntime=15\nai=None\nai-mode=minimax\nai-depth=1\nai-heuristic=default\n"
        )
    with open(CONFIG_FILE, "w") as f:
        f.write(
            """
from quoridor.gamemode import GameMode, AiMode, AiHeuristic

DEFAULT_GRID_SIZE = 9
DEFAULT_NUM_PLAYERS = 2
DEFAULT_NUM_WALLS = 10
DEFAULT_BLITZ_TIME = 15
DEFAULT_GAME_MODE = GameMode.NORMAL
DEFAULT_AI_COLOR = None
DEFAULT_AI_COLOR_ID = 2
DEFAULT_AI_MODE = AiMode.MINIMAX
DEFAULT_AI_DEPTH = 1
DEFAULT_AI_HEURISTIC = AiHeuristic.DEFAULT

MIN_GRID_SIZE = 3
MAX_GRID_SIZE = 15
MIN_NUM_PLAYERS = 2
MAX_NUM_PLAYERS = 4
NOT_RECOMMENDED_NUM_PLAYERS = 3

GRID_SIZE = 9
NUM_WALLS = 10
NUM_PLAYERS = 2
GAME_MODE = GameMode.BLITZ
BLITZ_TIME = 15
AI_COLOR = set()
AI_MODE = AiMode.MINIMAX
AI_DEPTH = 1
AI_HEURISTIC = AiHeuristic.DEFAULT
"""
        )

    yield

    if os.path.exists(DEFAULT_CONFIG_FILE):
        os.remove(DEFAULT_CONFIG_FILE)
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)


def test_setup_logging_verbose():
    """
    Test for setup_logging with verbose
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logging.shutdown()
    setup_logging(verbose=True, debug=False)
    logger = logging.getLogger()
    assert logger.level == logging.INFO


def test_setup_logging_debug():
    """
    Test for setup_logging with debug
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logging.shutdown()
    setup_logging(verbose=False, debug=True)
    logger = logging.getLogger()
    assert logger.level == logging.DEBUG


def test_setup_logging_warning():
    """
    Test for setup_logging with nothing
    """
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    logging.shutdown()
    setup_logging(verbose=False, debug=False)
    logger = logging.getLogger()
    assert logger.level == logging.WARNING


@pytest.fixture
def create_config_file():
    """Fixture to create the .quoridorrc_test config file with dynamic values"""

    def _create_config_file(config_content):
        with open(DEFAULT_CONFIG_FILE, "w") as f:
            f.write(config_content)

    yield _create_config_file

    # Cleanup after tests
    if os.path.exists(DEFAULT_CONFIG_FILE):
        os.remove(DEFAULT_CONFIG_FILE)


def test_load_default_config_mode(create_config_file):
    # Test with 'normal' mode
    config_content = """
[Default]
size = 9
players = 2
walls = 10
mode = normal
time = 15
ai = None
ai-mode = minimax
ai-depth = 1
ai-heuristic = default
"""
    create_config_file(config_content)
    size, players, walls, mode, time, ai_color, ai_mode, ai_depth, ai_heuristic = (
        load_default_config(DEFAULT_CONFIG_FILE)
    )
    assert mode == GameMode.NORMAL

    # Test with 'blitz' mode
    config_content = """
[Default]
size = 9
players = 2
walls = 10
mode = blitz
time = 15
ai = None
ai-mode = minimax
ai-depth = 1
ai-heuristic = default
"""
    create_config_file(config_content)
    size, players, walls, mode, time, ai_color, ai_mode, ai_depth, ai_heuristic = (
        load_default_config(DEFAULT_CONFIG_FILE)
    )
    assert mode == GameMode.BLITZ

    # Test with 'wrong' mode
    config_content = """
[Default]
size = 9
players = 2
walls = 10
mode = wrong
time = 15
ai = None
ai-mode = minimax
ai-depth = 1
ai-heuristic = default
"""
    create_config_file(config_content)
    size, players, walls, mode, time, ai_color, ai_mode, ai_depth, ai_heuristic = (
        load_default_config(DEFAULT_CONFIG_FILE)
    )
    assert mode == DEFAULT_GAME_MODE


def test_load_default_config_ai_mode(create_config_file):
    # Test with 'minimax' AI mode
    config_content = """
[Default]
size = 9
players = 2
walls = 10
mode = normal
time = 15
ai = None
ai-mode = minimax
ai-depth = 1
ai-heuristic = default
"""
    create_config_file(config_content)
    size, players, walls, mode, time, ai_color, ai_mode, ai_depth, ai_heuristic = (
        load_default_config(DEFAULT_CONFIG_FILE)
    )
    assert ai_mode == AiMode.MINIMAX

    # Test with 'greedy' AI mode
    config_content = """
[Default]
size = 9
players = 2
walls = 10
mode = normal
time = 15
ai = None
ai-mode = greedy
ai-depth = 1
ai-heuristic = default
"""
    create_config_file(config_content)
    size, players, walls, mode, time, ai_color, ai_mode, ai_depth, ai_heuristic = (
        load_default_config(DEFAULT_CONFIG_FILE)
    )
    assert ai_mode == AiMode.GREEDY

    # Test with 'alphabeta' AI mode
    config_content = """
[Default]
size = 9
players = 2
walls = 10
mode = normal
time = 15
ai = None
ai-mode = ab
ai-depth = 1
ai-heuristic = default
"""
    create_config_file(config_content)
    size, players, walls, mode, time, ai_color, ai_mode, ai_depth, ai_heuristic = (
        load_default_config(DEFAULT_CONFIG_FILE)
    )
    assert ai_mode == AiMode.ALPHABETA

    # Test with 'wrong' AI mode
    config_content = """
[Default]
size = 9
players = 2
walls = 10
mode = normal
time = 15
ai = None
ai-mode = wrong
ai-depth = 1
ai-heuristic = default
"""
    create_config_file(config_content)
    size, players, walls, mode, time, ai_color, ai_mode, ai_depth, ai_heuristic = (
        load_default_config(DEFAULT_CONFIG_FILE)
    )
    assert ai_mode == DEFAULT_AI_MODE


def test_load_default_config_ai_heuristic(create_config_file):
    # Test with 'default' AI heuristic
    config_content = """
[Default]
size = 9
players = 2
walls = 10
mode = normal
time = 15
ai = None
ai-mode = minimax
ai-depth = 1
ai-heuristic = default
"""
    create_config_file(config_content)
    size, players, walls, mode, time, ai_color, ai_mode, ai_depth, ai_heuristic = (
        load_default_config(DEFAULT_CONFIG_FILE)
    )
    assert ai_heuristic == AiHeuristic.DEFAULT

    # Test with 'runner' AI heuristic
    config_content = """
[Default]
size = 9
players = 2
walls = 10
mode = normal
time = 15
ai = None
ai-mode = minimax
ai-depth = 1
ai-heuristic = runner
"""
    create_config_file(config_content)
    size, players, walls, mode, time, ai_color, ai_mode, ai_depth, ai_heuristic = (
        load_default_config(DEFAULT_CONFIG_FILE)
    )
    assert ai_heuristic == AiHeuristic.RUNNER

    # Test with 'aggressive' AI heuristic
    config_content = """
[Default]
size = 9
players = 2
walls = 10
mode = normal
time = 15
ai = None
ai-mode = minimax
ai-depth = 1
ai-heuristic = aggressive
"""
    create_config_file(config_content)
    size, players, walls, mode, time, ai_color, ai_mode, ai_depth, ai_heuristic = (
        load_default_config(DEFAULT_CONFIG_FILE)
    )
    assert ai_heuristic == AiHeuristic.AGGRESSIVE

    # Test with 'central' AI heuristic
    config_content = """
[Default]
size = 9
players = 2
walls = 10
mode = normal
time = 15
ai = None
ai-mode = minimax
ai-depth = 1
ai-heuristic = central
"""
    create_config_file(config_content)
    size, players, walls, mode, time, ai_color, ai_mode, ai_depth, ai_heuristic = (
        load_default_config(DEFAULT_CONFIG_FILE)
    )
    assert ai_heuristic == AiHeuristic.CENTRAL

    # Test with 'wrong' AI heuristic
    config_content = """
[Default]
size = 9
players = 2
walls = 10
mode = normal
time = 15
ai = None
ai-mode = minimax
ai-depth = 1
ai-heuristic = wrong
"""
    create_config_file(config_content)
    size, players, walls, mode, time, ai_color, ai_mode, ai_depth, ai_heuristic = (
        load_default_config(DEFAULT_CONFIG_FILE)
    )
    assert ai_heuristic == DEFAULT_AI_HEURISTIC


def test_load_default_config_ai_color(create_config_file):
    # Test with AI color set to 'None'
    config_content = """
[Default]
size = 9
players = 2
walls = 10
mode = normal
time = 15
ai = None
ai-mode = minimax
ai-depth = 1
ai-heuristic = default
"""
    create_config_file(config_content)
    size, players, walls, mode, time, ai_color, ai_mode, ai_depth, ai_heuristic = (
        load_default_config(DEFAULT_CONFIG_FILE)
    )
    assert ai_color == set()

    # Test with AI color set to a valid set of integers
    config_content = """
[Default]
size = 9
players = 2
walls = 10
mode = normal
time = 15
ai = 1,2
ai-mode = minimax
ai-depth = 1
ai-heuristic = default
"""
    create_config_file(config_content)
    size, players, walls, mode, time, ai_color, ai_mode, ai_depth, ai_heuristic = (
        load_default_config(DEFAULT_CONFIG_FILE)
    )
    assert ai_color == {1, 2}


def test_update_default_config(mock_config_files):
    update_default_config(
        size=15,
        num_players=3,
        num_walls=6,
        game_mode="normal",
        blitz_time=60,
        ai_color={1, 2},
        ai_mode="minimax",
        ai_depth=5,
        ai_heuristic="default",
        config_file_str=DEFAULT_CONFIG_FILE,
    )

    config = configparser.ConfigParser()
    config.read(DEFAULT_CONFIG_FILE)

    assert config["Default"]["size"] == "15"
    assert config["Default"]["players"] == "3"
    assert config["Default"]["walls"] == "6"
    assert config["Default"]["mode"] == "normal"
    assert config["Default"]["time"] == "60"
    assert config["Default"]["ai"] == "1,2"
    assert config["Default"]["ai-mode"] == "minimax"
    assert config["Default"]["ai-depth"] == "5"
    assert config["Default"]["ai-heuristic"] == "default"

    update_default_config(
        size=15,
        num_players=3,
        num_walls=6,
        game_mode="normal",
        blitz_time=60,
        ai_color=3,
        ai_mode="minimax",
        ai_depth=5,
        ai_heuristic="default",
        config_file_str=DEFAULT_CONFIG_FILE,
    )

    config = configparser.ConfigParser()
    config.read(DEFAULT_CONFIG_FILE)
    assert config["Default"]["ai"] == "3"

    update_default_config(
        size=15,
        num_players=3,
        num_walls=6,
        game_mode="normal",
        blitz_time=60,
        ai_color=None,
        ai_mode="minimax",
        ai_depth=5,
        ai_heuristic="default",
        config_file_str=DEFAULT_CONFIG_FILE,
    )

    config = configparser.ConfigParser()
    config.read(DEFAULT_CONFIG_FILE)
    assert config["Default"]["ai"] == "None"


def test_update_config_file(mock_config_files):
    update_config_file(
        size=20,
        num_players=4,
        num_walls=7,
        game_mode=GameMode.NORMAL,
        blitz_time=90,
        ai_color={1, 3},
        ai_mode=AiMode.MINIMAX,
        ai_depth=6,
        ai_heuristic=AiHeuristic.RUNNER,
        config_file_str=CONFIG_FILE,
    )

    with open(CONFIG_FILE, "r") as f:
        content = f.read()

    assert "GRID_SIZE = 20" in content
    assert "NUM_PLAYERS = 4" in content
    assert "NUM_WALLS = 7" in content
    assert "GAME_MODE = GameMode.NORMAL" in content
    assert "BLITZ_TIME = 90" in content
    assert "AI_COLOR = {1, 3}" in content
    assert "AI_MODE = AiMode.MINIMAX" in content
    assert "AI_DEPTH = 6" in content
    assert "AI_HEURISTIC = AiHeuristic.RUNNER" in content

    assert "DEFAULT_GRID_SIZE = 9" in content
    assert "DEFAULT_NUM_PLAYERS = 2" in content
    assert "DEFAULT_NUM_WALLS = 10" in content
    assert "DEFAULT_GAME_MODE = GameMode.NORMAL" in content
    assert "DEFAULT_AI_COLOR = None" in content
    assert "DEFAULT_AI_MODE = AiMode.MINIMAX" in content
    assert "DEFAULT_AI_DEPTH = 1" in content
    assert "DEFAULT_AI_HEURISTIC = AiHeuristic.DEFAULT" in content


def test_restore_default_config_file():
    with mock.patch("quoridor.main.update_default_config") as mock_update:
        restore_default_config_file()
        mock_update.assert_called_once()


# End test - configparser


# Begin test - main


def test_version_option(capsys):
    """
    Test option -V version
    """
    version = importlib.metadata.version("quoridor")
    with mock.patch("sys.argv", ["quoridor.main.py", "--version"]):
        with mock.patch("importlib.metadata.version", return_value=version):
            with pytest.raises(SystemExit) as exitinfo:
                main()

            captured = capsys.readouterr()
            assert captured.out.strip() == f"Quoridor : version {version}"
            assert exitinfo.value.code == 0


def test_init():
    from quoridor import main

    with mock.patch.object(main, "main", return_value=42):
        with mock.patch.object(main, "__name__", "__main__"):
            with mock.patch.object(main.sys, "exit") as mock_exit:
                main.init()
                assert mock_exit.call_args[0][0] == 42


class MockArgs:
    def __init__(
        self,
        size=None,
        players=None,
        walls=None,
        blitz=False,
        time=None,
        ai=None,
        ai_mode=None,
        ai_depth=None,
        ai_heuristic=None,
        replay=None,
    ):
        self.size = size
        self.players = players
        self.walls = walls
        self.blitz = blitz
        self.time = time
        self.ai = ai
        self.ai_mode = ai_mode
        self.ai_depth = ai_depth
        self.ai_heuristic = ai_heuristic
        self.replay = replay


def test_parse_args_version():
    sys.argv = ["quoridor.", "--version"]
    args = parse_args()
    assert args.version is True


def test_parse_args_verbose():
    sys.argv = ["quoridor.", "--verbose"]
    args = parse_args()
    assert args.verbose is True


def test_parse_args_debug():
    sys.argv = ["quoridor.", "--debug"]
    args = parse_args()
    assert args.debug is True


def test_parse_args_size():
    sys.argv = ["quoridor.", "--size", "9"]
    args = parse_args()
    assert args.size == 9


def test_parse_args_invalid_size_not_odd():
    sys.argv = ["quoridor.", "--size", "10"]
    with pytest.raises(SystemExit):  # Expecting a system exit due to invalid size
        args = parse_args()
        configure_game(args)


def test_parse_args_invalid_size():
    sys.argv = ["quoridor", "--size", "19"]
    with pytest.raises(SystemExit):  # Expecting a system exit due to invalid size
        args = parse_args()
        configure_game(args)


from unittest.mock import patch
import pytest


def test_configure_game_valid():
    class Args:
        size = 9
        players = 2
        walls = 20
        blitz = False
        time = 0
        ai = None
        ai_mode = None
        ai_depth = 0
        ai_heuristic = None
        replay = None

    args = Args()

    with patch("quoridor.main.load_default_config") as mock_load:
        mock_load.return_value = (9, 2, 20, "normal", 3, set(), "minimax", 3, "default")
        result = configure_game(args)

    assert result[0] == 9
    assert result[1] == 2
    assert result[2] == 20
    assert result[3] == "normal"
    assert result[4] == 3
    assert result[5] == set()
    assert result[6] == "minimax"
    assert result[7] == 3
    assert result[8] == "default"


def test_configure_game_invalid_players():
    args = parse_args()
    args.players = 5
    with patch("quoridor.main.load_default_config") as mock_load:
        mock_load.return_value = (9, 2, 20, "normal", 3, set(), "minimax", 3, "default")
        with pytest.raises(SystemExit):
            configure_game(args)


def test_initialize_game_state():
    ai_ids = {0, 1}
    state = initialize_game_state(
        size=9,
        num_players=2,
        num_walls=20,
        game_mode=GameMode.NORMAL,
        blitz_time=0,
        ai_ids=ai_ids,
        ai_mode=AiMode.MINIMAX,
        ai_depth=3,
        ai_heuristic=AiHeuristic.DEFAULT,
    )
    assert state.size == 9
    assert state.num_players == 2
    assert state.ai_ids == ai_ids
    assert state.ai_mode == AiMode.MINIMAX


def test_open_file_invalid():
    with pytest.raises(FileNotFoundError):
        open_file("invalid_file.txt")


def test_configure_game_size():
    class Args:
        size = 11
        players = 2
        walls = 20
        blitz = False
        time = 0
        ai = []
        ai_mode = None
        ai_depth = 0
        ai_heuristic = None
        replay = None

    args = Args()

    with patch("quoridor.main.load_default_config") as mock_load:
        mock_load.return_value = (9, 2, 20, "normal", 3, set(), "minimax", 3, "default")
        result = configure_game(args)

    assert result[0] == 11


def test_configure_game_players():
    class Args:
        size = 9
        players = 3
        walls = 20
        blitz = False
        time = 0
        ai = []
        ai_mode = None
        ai_depth = 0
        ai_heuristic = None
        replay = None

    args = Args()

    with patch("quoridor.main.load_default_config") as mock_load:
        mock_load.return_value = (9, 2, 20, "normal", 3, set(), "minimax", 3, "default")
        result = configure_game(args)

    assert result[1] == 3


def test_configure_game_blitz():
    class Args:
        size = 9
        players = 2
        walls = 20
        blitz = True
        time = 5
        ai = []
        ai_mode = None
        ai_depth = 0
        ai_heuristic = None
        replay = None

    args = Args()

    with patch("quoridor.main.load_default_config") as mock_load:
        mock_load.return_value = (9, 2, 20, "normal", 3, set(), "minimax", 3, "default")
        result = configure_game(args)

    assert result[3] == GameMode.BLITZ
    assert result[4] == 5


def test_configure_game_ai():
    class Args:
        size = 9
        players = 2
        walls = 20
        blitz = False
        time = 0
        ai = [True, "A"]
        ai_mode = None
        ai_depth = 3
        ai_heuristic = "runner"
        replay = None

    args = Args()

    with patch("quoridor.main.load_default_config") as mock_load:
        mock_load.return_value = (9, 2, 20, "normal", 3, set(), "minimax", 3, "runner")
        result = configure_game(args)

    assert result[5] == {0, 1, 2, 3}
    assert result[6] == "minimax"
    assert result[7] == 3
    assert result[8] == AiHeuristic.RUNNER


def test_configure_game_invalid_size():
    class Args:
        size = 16
        players = 2
        walls = 20
        blitz = False
        time = 0
        ai = []
        ai_mode = None
        ai_depth = 0
        ai_heuristic = None
        replay = None

    args = Args()

    with patch("quoridor.main.load_default_config") as mock_load:
        mock_load.return_value = (9, 2, 20, "normal", 3, set(), "minimax", 3, "default")
        with pytest.raises(SystemExit):
            configure_game(args)


def test_configure_game_invalid_players():
    class Args:
        size = 9
        players = 5
        walls = 20
        blitz = False
        time = 0
        ai = []
        ai_mode = None
        ai_depth = 0
        ai_heuristic = None
        replay = None

    args = Args()

    with patch("quoridor.main.load_default_config") as mock_load:
        mock_load.return_value = (9, 2, 20, "normal", 3, set(), "minimax", 3, "default")
        with pytest.raises(SystemExit):
            configure_game(args)


def test_configure_game_invalid_ai():
    class Args:
        size = 9
        players = 2
        walls = 20
        blitz = False
        time = 0
        ai = ["4", "5"]
        ai_mode = None
        ai_depth = 0
        ai_heuristic = None
        replay = None

    args = Args()

    with patch("quoridor.main.load_default_config") as mock_load:
        mock_load.return_value = (
            9,
            2,
            20,
            "normal",
            3,
            {4, 5},
            "minimax",
            3,
            "default",
        )
        with pytest.raises(SystemExit):
            configure_game(args)


def test_configure_game_with_ai_mode():
    args = MockArgs(ai_mode="ab")
    _, _, _, _, _, _, ai_mode, _, _ = configure_game(args)
    assert ai_mode == AiMode.ALPHABETA

    args = MockArgs(ai_mode="minimax")
    _, _, _, _, _, _, ai_mode, _, _ = configure_game(args)
    assert ai_mode == AiMode.MINIMAX

    args = MockArgs(ai_mode="greedy")
    _, _, _, _, _, _, ai_mode, _, _ = configure_game(args)
    assert ai_mode == AiMode.GREEDY


def test_configure_game_with_ai_heuristic():
    args = MockArgs(ai_heuristic="default")
    _, _, _, _, _, _, _, _, ai_heuristic = configure_game(args)
    assert ai_heuristic == AiHeuristic.DEFAULT

    args = MockArgs(ai_heuristic="runner")
    _, _, _, _, _, _, _, _, ai_heuristic = configure_game(args)
    assert ai_heuristic == AiHeuristic.RUNNER

    args = MockArgs(ai_heuristic="aggressive")
    _, _, _, _, _, _, _, _, ai_heuristic = configure_game(args)
    assert ai_heuristic == AiHeuristic.AGGRESSIVE

    args = MockArgs(ai_heuristic="central")
    _, _, _, _, _, _, _, _, ai_heuristic = configure_game(args)
    assert ai_heuristic == AiHeuristic.CENTRAL


def test_configure_game_with_replay(monkeypatch):
    def mock_read_history(file_path):
        return ["line1", "line2"]

    def mock_num_players_from_file(lines):
        return 3

    monkeypatch.setattr(ReadWriteHistory, "read_history", mock_read_history)
    monkeypatch.setattr(
        ReadWriteHistory, "num_players_from_file", mock_num_players_from_file
    )

    args = MockArgs(replay="fake_path")
    _, num_players, _, _, _, _, _, _, _ = configure_game(args)
    assert num_players == max(3, load_default_config()[1])
