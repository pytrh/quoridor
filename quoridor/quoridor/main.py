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

from quoridor.cliengine import CLIEngine
from quoridor.gamestate import GameState
from quoridor.gamemode import GameMode
from quoridor.guiengine import GUIEngine
from quoridor.config import (
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

    if debug:
        logging.basicConfig(level=logging.DEBUG, format=log_format, datefmt=date_format)
        logging.debug("Debug mode activated: Detailed logs (dev)")
    elif verbose:
        logging.basicConfig(level=logging.INFO, format=log_format, datefmt=date_format)
        logging.info("Verbose mode activated: Additional information")
    else:
        logging.basicConfig(
            level=logging.WARNING, format=log_format, datefmt=date_format
        )


def load_default_config():
    config = configparser.ConfigParser()
    config.read(DEFAULT_CONFIG_FILE)

    size = config.getint("Default", "size", fallback=9)
    players = config.getint("Default", "players", fallback=2)
    walls = config.getint("Default", "walls", fallback=20)
    mode_name = config.get("Default", "mode", fallback="default_value")
    time = config.getint("Default", "time", fallback=20)

    mode = None
    if mode_name == "normal":
        mode = GameMode.NORMAL # TODO: check is better way to get game mode from quoridorc
    elif mode_name == "blitz":
        mode = GameMode.BLITZ
    
    return size, players, walls, mode, time


def update_default_config(size: int, num_players: int, num_walls: int, game_mode: str, blitz_time: int) -> None:
    config = configparser.ConfigParser()
    config.read(DEFAULT_CONFIG_FILE)

    config["Default"]["size"] = str(size)
    config["Default"]["players"] = str(num_players)
    config["Default"]["walls"] = str(num_walls)
    config["Default"]["mode"] = str(game_mode)
    config["Default"]["time"] = str(blitz_time)

    logging.debug("Updated Config:")
    for section in config.sections():
        logging.debug(f"[{section}]")
        for key, value in config.items(section):
            logging.debug(f"{key} = {value}")

    with open(DEFAULT_CONFIG_FILE, "w") as default_config:
        config.write(default_config)


def update_config_file(size: int, num_players: int, num_walls: int, game_mode: GameMode, blitz_time: int) -> None:
    with open(CONFIG_FILE, "r+") as config_file:
        lines = config_file.readlines()
        config_file.seek(0)
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
            config_file.write(line)
            # TODO: bug when putting more than one param on command line

def restore_default_config_file() -> None:
    update_default_config(DEFAULT_GRID_SIZE, DEFAULT_NUM_PLAYERS, DEFAULT_NUM_WALLS, DEFAULT_GAME_MODE.display_name, DEFAULT_BLITZ_TIME)


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
        nargs="?",
        const=15,
    )
    parser.add_argument(
        "-a",
        "--ai",
        help="Enable AI mode for COLOR (1, 2, 3, 4 or A for all). Default is 2. Can be used multiple times.",
        nargs="?",
        const=True,
        action="append",
    )

    args = parser.parse_args()
    game_related_args = ["players", "blitz", "time", "size", "walls", "ai"]

    setup_logging(verbose=args.verbose, debug=args.debug)

    if args.version:
        version = importlib.metadata.version("quoridor")
        print(f"Quoridor : version {version}")
        sys.exit(0)

    if args.file:
        logging.debug("File found in arguments")
        # game = GameState.load_game_from_file(args.file)

    size, num_players, num_walls, game_mode, blitz_time = load_default_config()

    current_ai_color = DEFAULT_AI_COLOR # TODO: read from config
    ai_ids = set()

    changed = False

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
            num_players = max(DEFAULT_AI_COLOR, max(len(ai_ids), max(ai_ids) + 1))
    elif args.ai is not None:
        num_players = max(DEFAULT_AI_COLOR, max(len(ai_ids), max(ai_ids) + 1))
        changed = True

    
    if changed:
        update_config_file(size, num_players, num_walls, game_mode, blitz_time)
        update_default_config(size, num_players, num_walls, game_mode.display_name, blitz_time) 

    initial_state = GameState(
        size=size,
        num_players=num_players,
        num_walls=num_walls,
        game_mode=game_mode,
        blitz_time=blitz_time,
        ai_ids=ai_ids,
    )

    try:
        if args.gui and not any(getattr(args, arg) for arg in game_related_args):
            engine = GUIEngine(None)
            engine.run()
        elif args.gui:
            engine = GUIEngine(initial_state)
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
