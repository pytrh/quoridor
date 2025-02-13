"""
Point d'entrée principal du programme
Gestion des arguments en ligne de commande
"""

import argparse
import importlib.metadata
import logging
import sys

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
    parser.add_argument("-V", "--version", help="affiche la version du programme",
        action="store_true")
    parser.add_argument("-v", "--verbose", help="active le mode verbose",
        action="store_true")
    parser.add_argument("-d", "--debug", help="active le mode debug (dev)",
        action="store_true")
    args = parser.parse_args()
    if args.version :
        version = importlib.metadata.version("quoridor")
        print(f"Quoridor : version {version}")
        sys.exit(10)
    setup_logging(verbose=args.verbose, debug=args.debug)
    sys.exit(0)

def init():
    """
    Fonction initial
    """
    if __name__ == "__main__":
        sys.exit(main())

init()
