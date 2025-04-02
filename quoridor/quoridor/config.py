from quoridor.gamemode import GameMode

"""
Centralized configuration module for the Quoridor game.
IE: Board size, number of players, number of walls, etc.
"""
DEFAULT_GRID_SIZE = 9
DEFAULT_NUM_PLAYERS = 2
DEFAULT_NUM_WALLS = 10
DEFAULT_BLITZ_TIME = 15
DEFAULT_GAME_MODE = GameMode.NORMAL

# Board size limits
MIN_GRID_SIZE = 3
MAX_GRID_SIZE = 15

# Player limits
MIN_NUM_PLAYERS = 2
MAX_NUM_PLAYERS = 4
NOT_RECOMMENDED_NUM_PLAYERS = 3

GRID_SIZE = 9
NUM_WALLS = 10
NUM_PLAYERS = 2
GAME_MODE = GameMode.NORMAL
BLITZ_TIME = 15

# Game Mode

# AI color
DEFAULT_AI_COLOR = 2
