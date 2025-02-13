import argparse
import importlib.metadata

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-V", "--version", help="display the version of the program", action="store_true")
    args = parser.parse_args()
    if args.version :
        version = importlib.metadata.version("quoridor")
        print(f"Quoridor : version {version}")
    
### Main
if __name__ == "__main__":
    main()
