"""
Entry point for the Quoridor game
Handles command line arguments
"""

import argparse
import importlib.metadata
import logging
import sys

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
    DEFAULT_SIZE,
    DEFAULT_NUM_PLAYERS,
    DEFAULT_BLITZ_TIME,
    DEFAULT_NUM_WALLS,
    DEFAULT_GAME_MODE,
    DEFAULT_AI_COLOR,
)


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

    setup_logging(verbose=args.verbose, debug=args.debug)

    if args.version:
        version = importlib.metadata.version("quoridor")
        print(f"Quoridor : version {version}")
        sys.exit(0)

    if args.file:
        logging.debug("File found in arguments")
        # game = GameState.load_game_from_file(args.file)

    size = DEFAULT_SIZE
    num_players = DEFAULT_NUM_PLAYERS
    num_walls = DEFAULT_NUM_WALLS
    blitz_time = DEFAULT_BLITZ_TIME
    blitz_mode = DEFAULT_GAME_MODE
    ai_mode = DEFAULT_GAME_MODE
    current_ai_color = DEFAULT_AI_COLOR
    ai_colors = set()

    if args.walls:
        num_walls = args.walls

    if args.size:
        error = False
        size = args.size
        if size not in range(MIN_GRID_SIZE, MAX_GRID_SIZE + 1):
            logging.error("grid size must be between 3 and 15.")
            error = True
        if size % 2 == 0:
            logging.error("size must be an odd number.")
            error = True
        if error:
            sys.exit(1)

    if args.players:
        error = False
        num_players = args.players
        if num_players not in range(MIN_NUM_PLAYERS, MAX_NUM_PLAYERS + 1):
            logging.error("can only have 2, 3 or 4 players.")
            sys.exit(1)
        if num_players == NOT_RECOMMENDED_NUM_PLAYERS:
            logging.warning("it is not recommended to play by 3. Unfair advantage.")

    if args.ai:
        for ai in args.ai:
            if ai is True:
                ai_colors.add(current_ai_color)
                current_ai_color += 1
            elif ai == "A":
                ai_colors = {1, 2, 3, 4}
                break
            else:
                color = int(ai)
                if color < 1 or color > 4:
                    logging.error("COLOR must be between 1 and 4 or 'A'")
                    sys.exit(1)
                if color != 1 and color not in ai_colors:
                    current_ai_color += 1
                ai_colors.add(color)
        ai_mode = GameMode.AI

    if args.blitz:
        blitz_mode = GameMode.BLITZ

    if args.time:
        if blitz_mode != GameMode.BLITZ:
            logging.warning("blitz mode is not activated. You cannot set a time.")
        else:
            blitz_time = args.time

    if (args.players is not None) and (args.ai is not None):
        if num_players < max(ai_colors):
            logging.warning("Warning: -p option ignored due to presence of -a options")
            num_players = max(DEFAULT_AI_COLOR, max(ai_colors))
    elif args.ai is not None:
        num_players = max(DEFAULT_AI_COLOR, max(ai_colors))

    initial_state = GameState(
        size=size,
        num_players=num_players,
        num_walls=num_walls,
        blitz_mode=blitz_mode,
        blitz_time=blitz_time,
        ai_mode=ai_mode,
        ai_colors=ai_colors,
    )
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
