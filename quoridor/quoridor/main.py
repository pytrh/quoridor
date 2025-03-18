"""
Entry point for the Quoridor game
Handles command line arguments
"""

import argparse
import importlib.metadata
import logging
import sys

from quoridor.gamestate import GameState
from quoridor.gamelogic import GameStateManager
from quoridor.cliengine import CLIEngine


def setup_logging(verbose, debug):
    """
    Configure le système de logger en fonction des options --verbose et --debug.
    """
    log_format = "%(asctime)s - %(levelname)s - %(message)s"  # Format par défaut
    date_format = "%Y-%m-%d %H:%M:%S"  #

    if debug:
        logging.basicConfig(level=logging.DEBUG, format=log_format, datefmt=date_format)
        logging.debug("Mode debug activé : Affichage des logs détaillés (dev)")
    elif verbose:
        logging.basicConfig(level=logging.INFO, format=log_format, datefmt=date_format)
        logging.info("Mode verbose activé : Affichage des informations supplémentaires")
    else:
        logging.basicConfig(
            level=logging.WARNING, format=log_format, datefmt=date_format
        )


def main():
    """
    Fonction principal
    Gestion des arguments avec argparse
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
        logging.debug("Fichier en argument trouvé")
        # game = GameState.load_game_from_file(args.file)

    # DEFAULT
    size = DEFAULT_GRID_SIZE
    num_players = DEFAULT_NUM_PLAYERS
    blitz_time = DEFAULT_BLITZ_TIME
    num_walls = DEFAULT_NUM_WALLS

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

    game = GameState(size, num_players, False, num_walls)
    terminal = TerminalView(game)
    terminal.start_game()
    sys.exit(0)


def init():
    """
    Fonction initial
    """
    if __name__ == "__main__":
        sys.exit(main())


init()
