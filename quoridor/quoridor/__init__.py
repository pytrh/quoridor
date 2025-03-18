"""Quoridor game package"""

import quoridor.main
import quoridor.graph
import quoridor.gamestate
import quoridor.player
import quoridor.exceptions

# Version info
__version__ = "0.2.0"

# Import main classes/functions that should be available at package level
from quoridor.gamestate import GameState
from quoridor.gamestatemanager import GameStateManager
from quoridor.player import Player
from quoridor.graph import Graph
from quoridor.gameengine import GameEngine
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