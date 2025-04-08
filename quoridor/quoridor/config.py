from quoridor.gamemode import GameMode, AiMode, AiHeuristic

"""
Centralized configuration module for the Quoridor game.
IE: Board size, number of players, number of walls, etc.
"""
DEFAULT_GRID_SIZE = 9
DEFAULT_NUM_PLAYERS = 2
DEFAULT_NUM_WALLS = 10
DEFAULT_BLITZ_TIME = 15
DEFAULT_GAME_MODE = GameMode.NORMAL
# AI
DEFAULT_AI_COLOR = None
DEFAULT_AI_COLOR_ID = 2
DEFAULT_AI_MODE = AiMode.MINIMAX
DEFAULT_AI_DEPTH = 1
DEFAULT_AI_HEURISTIC = AiHeuristic.DEFAULT

# Board size limits
MIN_GRID_SIZE = 3
MAX_GRID_SIZE = 15

# Player limits
MIN_NUM_PLAYERS = 2
MAX_NUM_PLAYERS = 4
NOT_RECOMMENDED_NUM_PLAYERS = 3

# Game Parameters
GRID_SIZE = 5
NUM_WALLS = 10
NUM_PLAYERS = 3
GAME_MODE = GameMode.NORMAL
BLITZ_TIME = 15
AI_COLOR = {1}
AI_MODE = AiMode.ALPHABETA
AI_DEPTH = 1
AI_HEURISTIC = AiHeuristic.DEFAULT
