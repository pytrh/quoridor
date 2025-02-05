# quoridor/quoridor.py

import argparse
import importlib.metadata

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-V", "--version", help="affiche la version du programme", action="store_true")
    args = parser.parse_args()
    if args.version :
        version = importlib.metadata.version("quoridor")
        print(f"Quoridor : version {version}")
    
### Main
if __name__ == "__main__":
    main()
