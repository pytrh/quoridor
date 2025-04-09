"""
Entry point for the Quoridor game
Handles command line arguments
"""

import argparse
import configparser
import importlib.metadata
import logging
import sys
import os

from quoridor.io import ReadWriteHistory
from quoridor.cliengine import CLIEngine
from quoridor.gamestate import GameState
from quoridor.gamemode import GameMode, AiMode, AiHeuristic
from quoridor.guiengine import GUIEngine
from quoridor.parser import parse_string_to_state
from quoridor.config import (
    DEFAULT_AI_COLOR_ID,
    DEFAULT_AI_DEPTH,
    DEFAULT_AI_HEURISTIC,
    DEFAULT_AI_MODE,
    MIN_GRID_SIZE,
    MAX_GRID_SIZE,
    MIN_NUM_PLAYERS,
    MAX_NUM_PLAYERS,
    NOT_RECOMMENDED_NUM_PLAYERS,
    DEFAULT_GRID_SIZE,
    DEFAULT_NUM_PLAYERS,
    DEFAULT_BLITZ_TIME,
    DEFAULT_NUM_WALLS,
    DEFAULT_GAME_MODE,
    DEFAULT_AI_COLOR,
)
from quoridor.exceptions import QuitApp

dirname = os.path.dirname(__file__)
DEFAULT_CONFIG_FILE = os.path.join(dirname, ".quoridorrc")
CONFIG_FILE = os.path.join(dirname, "config.py")


def setup_logging(verbose, debug):
    """
    Configure the logging system based on the verbose and debug flags.
    """
    log_format = "%(asctime)s - %(levelname)s - %(message)s"  # Default format
    date_format = "%Y-%m-%d %H:%M:%S"  # Default date format

    handler = logging.StreamHandler(sys.stdout)

    if debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format=log_format,
            datefmt=date_format,
            handlers=[handler],
        )
        logging.debug("Debug mode activated: Detailed logs (dev)")
    elif verbose:
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            datefmt=date_format,
            handlers=[handler],
        )
        logging.info("Verbose mode activated: Additional information")
    else:
        logging.basicConfig(
            level=logging.WARNING,
            format=log_format,
            datefmt=date_format,
            handlers=[handler],
        )


def load_default_config():
    config = configparser.ConfigParser()
    config.read(DEFAULT_CONFIG_FILE)

    size = config.getint("Default", "size", fallback=9)
    players = config.getint("Default", "players", fallback=2)
    walls = config.getint("Default", "walls", fallback=10)
    mode_name = config.get("Default", "mode", fallback="normal")
    time = config.getint("Default", "time", fallback=15)
    ai_color_str = config.get("Default", "ai", fallback=None)
    ai_mode_name = config.get("Default", "ai-mode", fallback="minimax")
    ai_depth = config.getint("Default", "ai-depth", fallback=3)
    ai_heuristic_name = config.get("Default", "ai-heuristic", fallback="default")

    mode = None
    if mode_name == GameMode.NORMAL.display_name:
        mode = GameMode.NORMAL
    elif mode_name == GameMode.BLITZ.display_name:
        mode = GameMode.BLITZ

    if not ai_color_str == "None":
        ai_color = set(map(int, ai_color_str.split(","))) if ai_color_str else set()
    else:
        ai_color = set()

    ai_mode = None
    if ai_mode_name == AiMode.MINIMAX.display_name:
        ai_mode = AiMode.MINIMAX
    elif ai_mode_name == AiMode.GREEDY.display_name:
        ai_mode = AiMode.GREEDY
    elif ai_mode_name == AiMode.ALPHABETA.display_name:
        ai_mode = AiMode.ALPHABETA
    else:
        ai_mode = DEFAULT_AI_MODE

    ai_heuristic = None
    if ai_heuristic_name == AiHeuristic.DEFAULT.display_name:
        ai_heuristic = AiHeuristic.DEFAULT
    elif ai_heuristic_name == AiHeuristic.RUNNER.display_name:
        ai_heuristic = AiHeuristic.RUNNER
    elif ai_heuristic_name == AiHeuristic.AGGRESSIVE.display_name:
        ai_heuristic = AiHeuristic.AGGRESSIVE
    elif ai_heuristic_name == AiHeuristic.CENTRAL.display_name:
        ai_heuristic = AiHeuristic.CENTRAL
    else:
        ai_heuristic = DEFAULT_AI_HEURISTIC

    # Todo verify for invalid parameters (if size between 3 and 15 and odd)
    return size, players, walls, mode, time, ai_color, ai_mode, ai_depth, ai_heuristic


def update_default_config(
    size: int,
    num_players: int,
    num_walls: int,
    game_mode: str,
    blitz_time: int,
    ai_color: set,
    ai_mode: str,
    ai_depth: int,
    ai_heuristic: str,
) -> None:
    config = configparser.ConfigParser()
    config.read(DEFAULT_CONFIG_FILE)

    config["Default"]["size"] = str(size)
    config["Default"]["players"] = str(num_players)
    config["Default"]["walls"] = str(num_walls)
    config["Default"]["mode"] = str(game_mode)
    config["Default"]["time"] = str(blitz_time)
    if isinstance(ai_color, (set, list)):
        config["Default"]["ai"] = ",".join(map(str, ai_color))
    elif isinstance(ai_color, int):
        config["Default"]["ai"] = str(ai_color)
    else:
        config["Default"]["ai"] = "None"
    config["Default"]["ai-mode"] = str(ai_mode)
    config["Default"]["ai-depth"] = str(ai_depth)
    config["Default"]["ai-heuristic"] = str(ai_heuristic)

    logging.debug("Updated Config:")
    for section in config.sections():
        logging.debug(f"[{section}]")
        for key, value in config.items(section):
            logging.debug(f"{key} = {value}")

    with open(DEFAULT_CONFIG_FILE, "w") as default_config:
        config.write(default_config)


def update_config_file(
    size: int,
    num_players: int,
    num_walls: int,
    game_mode: GameMode,
    blitz_time: int,
    ai_color: set,
    ai_mode: AiMode,
    ai_depth: int,
    ai_heuristic: AiHeuristic,
) -> None:
    with open(CONFIG_FILE, "r+") as config_file:
        lines = config_file.readlines()
        config_file.seek(0)
        config_file.truncate()

        for line in lines:
            if line.strip().startswith("GRID_SIZE"):
                line = f"GRID_SIZE = {size}\n"
            elif line.strip().startswith("NUM_PLAYERS"):
                line = f"NUM_PLAYERS = {num_players}\n"
            elif line.strip().startswith("NUM_WALLS"):
                line = f"NUM_WALLS = {num_walls}\n"
            elif line.strip().startswith("GAME_MODE"):
                line = f"GAME_MODE = {game_mode}\n"
            elif line.strip().startswith("BLITZ_TIME"):
                line = f"BLITZ_TIME = {blitz_time}\n"
            elif line.strip().startswith("AI_COLOR"):
                line = f"AI_COLOR = {ai_color}\n"
            elif line.strip().startswith("AI_MODE"):
                line = f"AI_MODE = {ai_mode}\n"
            elif line.strip().startswith("AI_DEPTH"):
                line = f"AI_DEPTH = {ai_depth}\n"
            elif line.strip().startswith("AI_HEURISTIC"):
                line = f"AI_HEURISTIC = {ai_heuristic}\n"
            config_file.write(line)
            # TODO: bug when putting more than one param on command line


def restore_default_config_file() -> None:
    update_default_config(
        DEFAULT_GRID_SIZE,
        DEFAULT_NUM_PLAYERS,
        DEFAULT_NUM_WALLS,
        DEFAULT_GAME_MODE.display_name,
        DEFAULT_BLITZ_TIME,
        DEFAULT_AI_COLOR,
        DEFAULT_AI_MODE.display_name,
        DEFAULT_AI_DEPTH,
        DEFAULT_AI_HEURISTIC.display_name,
    )


def main():
    """
    Main function
    Handles command line arguments with argparse
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("file", default=None, nargs="?")

    parser.add_argument(
        "-V",
        "--version",
        help="Display the current program version.",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Enable verbose mode for detailed output.",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--debug",
        help="Enable debug mode (for development).",
        action="store_true",
    )
    parser.add_argument(
        "-g",
        "--gui",
        help="Enable gui (Graphic User Interface)",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--size",
        help="Set the grid size (SIZE × SIZE). Default: 9. "
        "Must be an odd nmber between 3 and 15.",
        type=int,
    )
    parser.add_argument(
        "-w",
        "--walls",
        help="Set the number of walls per player. Default: 20. "
        "Use a negative value for unlimited walls.",
        type=int,
    )
    parser.add_argument(
        "-p",
        "--players",
        help="Set the number of players (2, 3, or 4). "
        "Default: 2. Note: 3-player mode is not recommended.",
        type=int,
    )
    parser.add_argument(
        "-b",
        "--blitz",
        help="Enable blitz (timer mode)",
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--time",
        help="Set the blitz time for the game in minutes (only used in blitz mode). Example: -t 3",
        type=int,
    )
    parser.add_argument(
        "-a",
        "--ai",
        help="Enable AI mode for COLOR (1, 2, 3, 4 or A for all). Default is 2. Can be used multiple times.",
        nargs="?",
        const=True,
        action="append",
    )
    # todo add parameter –-ai-mode/--ai-m --ai-depth/--ai-d --ai-heuristic/--ai-h
    parser.add_argument(
        "--ai-m",
        "--ai-mode",
        dest="ai_mode",
        help="Select the AI algorithm mode. Options: 'minimax' (basic decision tree), 'ab' (alpha-beta pruning for optimized minimax), 'greedy' (choose best move based on immediate gain).",
        type=str,
        required=False,
    )
    parser.add_argument(
        "--ai-d",
        "--ai-depth",
        dest="ai_depth",
        help="Depth of the AI search tree. Higher values mean stronger but slower AI (e.g., 1 to 5).",
        type=int,
        required=False,
    )
    parser.add_argument(
        "--ai-h",
        "--ai-heuristic",
        dest="ai_heuristic",
        help=(
            "Heuristic function for AI evaluation. Available options:\n"
            "'default' - Balanced evaluation,\n"
            "'runner' - Focus on fast piece movement or pathfinding,\n"
            "'aggressive' - Prioritizes blocking and attacking moves,\n"
            "'central' - Rewards control over the center of the board."
        ),
        type=str,
        required=False,
    )
    parser.add_argument(
        "-r",
        "--replay",
        help="replay game from file saved during pending play",
        required=False,
    )

    args = parser.parse_args()
    game_related_args = [
        "players",
        "blitz",
        "time",
        "size",
        "walls",
        "ai",
        "ai_mode",
        "ai_depth",
        "ai_heuristic",
        "replay",
        "file",
    ]

    setup_logging(verbose=args.verbose, debug=args.debug)

    if args.version:
        version = importlib.metadata.version("quoridor")
        print(f"Quoridor : version {version}")
        sys.exit(0)

    initial_state = None
    changed = False

    if args.file:
        changed = True
        logging.debug("File found in arguments")
        with open(args.file, "r", encoding="utf-8") as file:
            initial_state = parse_string_to_state(file)

    (
        size,
        num_players,
        num_walls,
        game_mode,
        blitz_time,
        ai_ids,
        ai_mode,
        ai_depth,
        ai_heuristic,
    ) = load_default_config()

    if args.walls:
        num_walls = args.walls
        if args.walls < 0:
            num_walls = 999
        changed = True

    if args.size:
        error = False
        if args.size not in range(MIN_GRID_SIZE, MAX_GRID_SIZE + 1):
            logging.error("grid size must be between 3 and 15.")
            error = True
        if args.size % 2 == 0:
            logging.error("size must be an odd number.")
            error = True
        if error:
            sys.exit(1)
        size = args.size
        changed = True

    if args.players:
        error = False
        if args.players not in range(MIN_NUM_PLAYERS, MAX_NUM_PLAYERS + 1):
            logging.error("can only have 2, 3 or 4 players.")
            sys.exit(1)
        if args.players == NOT_RECOMMENDED_NUM_PLAYERS:
            logging.warning("it is not recommended to play by 3. Unfair advantage.")
        num_players = args.players
        changed = True

    if args.ai:
        current_ai_color = DEFAULT_AI_COLOR_ID
        for ai in args.ai:
            if ai is True:
                ai_ids.add(current_ai_color - 1)
                current_ai_color += 1
            elif ai == "A":
                ai_ids = {0, 1, 2, 3}
                break
            else:
                color = int(ai)
                if color < 1 or color > 4:
                    logging.error("COLOR must be between 1 and 4 or 'A'")
                    sys.exit(1)
                if color != 1 and color not in ai_ids:
                    current_ai_color += 1
                ai_ids.add(color - 1)

    if args.blitz:
        game_mode = GameMode.BLITZ
        changed = True

    if args.time:
        if game_mode != GameMode.BLITZ:
            logging.warning("blitz mode is not activated. You cannot set a time.")
        else:
            blitz_time = args.time
            changed = True

    if (args.players is not None) and (args.ai is not None):
        if num_players < max(len(ai_ids), max(ai_ids) + 1):
            logging.warning("Warning: -p option ignored due to presence of -a options")
            num_players = max(DEFAULT_AI_COLOR_ID, max(len(ai_ids), max(ai_ids) + 1))
    elif args.ai is not None:
        num_players = max(DEFAULT_AI_COLOR_ID, max(len(ai_ids), max(ai_ids) + 1))
        changed = True

    if args.ai_mode:
        if args.ai_mode == AiMode.ALPHABETA.display_name:
            ai_mode = AiMode.ALPHABETA
        elif args.ai_mode == AiMode.MINIMAX.display_name:
            ai_mode = AiMode.MINIMAX
        elif args.ai_mode == AiMode.GREEDY.display_name:
            ai_mode = AiMode.GREEDY
        changed = True

    if args.ai_depth:
        ai_depth = args.ai_depth
        changed = True

    if args.ai_heuristic:
        print(args.ai_heuristic)
        if args.ai_heuristic == AiHeuristic.DEFAULT.display_name:
            ai_heuristic = AiHeuristic.DEFAULT
        elif args.ai_heuristic == AiHeuristic.RUNNER.display_name:
            ai_heuristic = AiHeuristic.RUNNER
        elif args.ai_heuristic == AiHeuristic.AGGRESSIVE.display_name:
            ai_heuristic = AiHeuristic.AGGRESSIVE
        elif args.ai_heuristic == AiHeuristic.CENTRAL.display_name:
            ai_heuristic = AiHeuristic.CENTRAL
        changed = True

    if changed:
        update_config_file(
            size,
            num_players,
            num_walls,
            game_mode,
            blitz_time,
            ai_ids,
            ai_mode,
            ai_depth,
            ai_heuristic,
        )
        update_default_config(
            size,
            num_players,
            num_walls,
            game_mode.display_name,
            blitz_time,
            ai_ids,
            ai_mode.display_name,
            ai_depth,
            ai_heuristic.display_name,
        )

    if args.replay:
        lines = ReadWriteHistory.read_history(args.replay)
        new_num_players = ReadWriteHistory.num_players_from_file(lines)
        num_players = max(new_num_players, num_players)

    if not initial_state:
        initial_state = GameState(
            size=size,
            num_players=num_players,
            num_walls=num_walls,
            game_mode=game_mode,
            blitz_time=blitz_time,
            ai_ids=ai_ids,
            ai_mode=ai_mode,
            ai_depth=ai_depth,
            ai_heuristic=ai_heuristic,
        )

    if args.replay:
        lines = ReadWriteHistory.read_history(args.replay)
        ReadWriteHistory.parse_list_of_str_to_history(initial_state, lines)

    try:
        if args.gui:
            if args.gui and not any(getattr(args, arg) for arg in game_related_args):
                engine = GUIEngine(None)
            else:
                engine = GUIEngine(initial_state)
            if args.replay:
                engine.load_game_from_history()
            elif args.file:
                engine.load_game_from_file()
            engine.run()
        else:
            cli_engine = CLIEngine(initial_state)
            cli_engine.start_game()
    except QuitApp:
        pass

    # not run if exited using ctrl-C or ctrl-Z
    restore_default_config_file()
    sys.exit(0)


def init():
    """
    Fonction initial
    """
    if __name__ == "__main__":
        sys.exit(main())


init()
