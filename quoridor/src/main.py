"""
Point d'entrée principal du programme
Gestion des arguments en ligne de commande
"""

import argparse
import importlib.metadata
import sys

def main():
    """
    Fonction principal
    Gestion des arguments avec argparse
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-V", "--version", help="affiche la version du programme",
        action="store_true")
    args = parser.parse_args()
    if args.version :
        version = importlib.metadata.version("quoridor")
        print(f"Quoridor : version {version}")
    sys.exit(0)

if __name__ == "__main__":
    main()
