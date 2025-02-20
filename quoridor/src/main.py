"""
Entry point for the Quoridor game
Handles command line arguments
"""

import argparse
import importlib.metadata
import logging
import sys

from src.gamestate import GameState
from src.config import MIN_GRID_SIZE, MAX_GRID_SIZE
from src.config import DEFAULT_GRID_SIZE, DEFAULT_NUM_PLAYERS, DEFAULT_BLITZ_TIME, DEFAULT_NUM_WALLS

def setup_logging(verbose, debug):
    """
    Configure le système de logger en fonction des options --verbose et --debug.
    """
    log_format = '%(asctime)s - %(levelname)s - %(message)s'  # Format par défaut
    date_format = '%Y-%m-%d %H:%M:%S'  #

    if debug:
        logging.basicConfig(level=logging.DEBUG, format=log_format, datefmt=date_format)
        logging.debug("Mode debug activé : Affichage des logs détaillés (dev)")
    elif verbose:
        logging.basicConfig(level=logging.INFO, format=log_format, datefmt=date_format)
        logging.info("Mode verbose activé : Affichage des informations supplémentaires")
    else:
        logging.basicConfig(level=logging.WARNING, format=log_format, datefmt=date_format)

def main():
    """
    Fonction principal
    Gestion des arguments avec argparse
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('file', default=None, nargs='?')
    parser.add_argument("-V", "--version", help="affiche la version du programme",
        action="store_true")
    parser.add_argument("-v", "--verbose", help="active le mode verbose",
        action="store_true")
    parser.add_argument("-d", "--debug", help="active le mode debug (dev)",
        action="store_true")
    parser.add_argument("-s", "--size", help="fixer la taille du plateau: size*size", type=int)
    parser.add_argument("-w", "--walls", help="parametrer le nombre de mur par joueur", type=int)

    args = parser.parse_args()

    setup_logging(verbose=args.verbose, debug=args.debug)

    if args.version :
        version = importlib.metadata.version("quoridor")
        print(f"Quoridor : version {version}")
        sys.exit(0)

    if args.file:
        logging.debug("Fichier en argument trouvé")
        # game = GameState.load_game_from_file(args.file)

    if args.walls:
        num_walls = args.walls
    # game = GameState.start_Game(size, num_players, blitz_time, num_walls)

    if args.size:
        error = False
        if args.size not in range(MIN_GRID_SIZE, MAX_GRID_SIZE + 1):
            print("ERROR: grid size must be between 3 and 15")
            error = True
        if args.size % 2 == 0:
            print("ERROR: size must be an odd number")
            error = True
        if error:
            sys.exit(1)
        size = args.size

    # DEFAULT
    size = DEFAULT_GRID_SIZE
    num_players = DEFAULT_NUM_PLAYERS
    blitz_time = DEFAULT_BLITZ_TIME
    num_walls = DEFAULT_NUM_WALLS
    sys.exit(0)

def init():
    """
    Fonction initial
    """
    if __name__ == "__main__":
        sys.exit(main())

init()
