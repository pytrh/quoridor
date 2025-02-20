"""
Entry point for the Quoridor game
Handles command line arguments
"""

import argparse
import importlib.metadata
import logging
import sys

from src.gamestate import GameState
from src.gamelogic import GameLogic
from src.terminalview import TerminalView

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

    size = 9
    num_players = 2
    blitz_mode = False
    num_walls = 20
    if args.walls:
       num_walls = args.walls
    
    game = GameState(size, num_players, blitz_mode, num_walls)
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

