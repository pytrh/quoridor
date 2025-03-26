"""
Entry point for the Quoridor game
Handles command line arguments
"""

import argparse
import configparser
import importlib.metadata
import logging
import sys

from quoridor.cliengine import CLIEngine
from quoridor.gamestate import GameState
from quoridor.guiengine import GUIEngine
from quoridor.config import (
    MIN_GRID_SIZE,
    MAX_GRID_SIZE,
    MIN_NUM_PLAYERS,
    MAX_NUM_PLAYERS,
    NOT_RECOMMENDED_NUM_PLAYERS,
)

DEFAULT_CONFIG_FILE = "quoridor/quoridor/.quoridorrc"
CONFIG_FILE = "quoridor/quoridor/config.py"

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

    return size, players, walls

def update_default_config(size : int, num_players : int, num_walls : int)->None:
    config = configparser.ConfigParser()
    config.read(DEFAULT_CONFIG_FILE)

    config["Default"]["size"] = str(size)
    config["Default"]["players"] = str(num_players)
    config["Default"]["walls"] = str(num_walls)

    print("Updated Config:")
    for section in config.sections():
        print(f"[{section}]")
        for key, value in config.items(section):
            print(f"{key} = {value}")

    with open(DEFAULT_CONFIG_FILE, "w") as default_config:
        config.write(default_config)

def update_config_file(size : int, num_players : int, num_walls : int)->None:
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
            config_file.write(line)

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

    args = parser.parse_args()

    setup_logging(verbose=args.verbose, debug=args.debug)

    if args.version:
        version = importlib.metadata.version("quoridor")
        print(f"Quoridor : version {version}")
        sys.exit(0)

    if args.file:
        logging.debug("File found in arguments")
        # game = GameState.load_game_from_file(args.file)

    size, num_players, num_walls = load_default_config()
    changed = False # Will be True if default_config needs to be updated

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

    if args.walls:
        num_walls = args.walls
        changed = True

    if changed:
        update_config_file(size, num_players, num_walls)
        update_default_config(size, num_players, num_walls)

    initial_state = GameState(size=size, num_players=num_players, num_walls=num_walls)
    if args.gui:
        engine = GUIEngine(initial_state)
        engine.run()
    else:
        cli_engine = CLIEngine(initial_state)
        cli_engine.start_game()
    sys.exit(0)


def init():
    """
    Fonction initial
    """
    if __name__ == "__main__":
        sys.exit(main())


init()
