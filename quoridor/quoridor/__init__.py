"""Quoridor game package"""

# Version info
__version__ = "0.2.0"

# Import main classes/functions that should be available at package level
from quoridor.gamestate import GameState
from quoridor.player import Player
from quoridor.graph import Graph
from quoridor.cliengine import CLIEngine
from quoridor.exceptions import (
    NodeNotFoundError,
    EdgeNotFoundError,
    PathNotFoundError,
    InvalidMoveError
)

# Define what should be available when someone does 'from src import *'
__all__ = [
    'GameState',
    'GameStateManager',
    'GameEngine',
    'CLIEngine',
    'Player',
    'Graph',
    'NodeNotFoundError',
    'EdgeNotFoundError',
    'PathNotFoundError',
    'InvalidMoveError',
]