from quoridor.gamemode import GameMode

"""
Centralized configuration module for the Quoridor game.
IE: Board size, number of players, number of walls, etc.
"""
DEFAULT_GRID_SIZE = 9
DEFAULT_NUM_PLAYERS = 2
DEFAULT_NUM_WALLS = 20

# Board size limits
MIN_GRID_SIZE = 3
MAX_GRID_SIZE = 15

# Player limits
MIN_NUM_PLAYERS = 2
MAX_NUM_PLAYERS = 4
NOT_RECOMMENDED_NUM_PLAYERS = 3

DEFAULT_SIZE = 9
DEFAULT_NUM_PLAYERS = 2
DEFAULT_NUM_WALLS = 20
DEFAULT_BLITZ_TIME = 15

# Game Mode
DEFAULT_GAME_MODE = GameMode.NORMAL

# AI color
DEFAULT_AI_COLOR = 2

# TODO: Parse the defaults from .quoridorrc
