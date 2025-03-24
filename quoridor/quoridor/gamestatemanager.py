"""
Deprecated GameStateManager module.
"""

import copy
from quoridor.gamestate import GameState
from quoridor.exceptions import InvalidMoveError, PathNotFoundError
from quoridor.command import (
    Command, MovePawnCommand, PlaceWallCommand, UndoCommand,
    RedoCommand, RestartCommand, QuitCommand
)

class GameStateManager:
    """
    GameStateManager manage the functionality of the application:
    the treatment that can be applied to the board
    """

    def __init__(self, gamestate: GameState):
        self.state = gamestate
