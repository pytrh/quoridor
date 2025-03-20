"""
GameStateManager module.
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
        self.initial_state = copy.deepcopy(gamestate)
        self.history = []
        self.redo_stack = []

    def execute_command(self, command: Command) -> None:
        """
        Execute a command and add it to the command history.
        """
        if command.execute():
            self.history.append(command)
            self.redo_stack.clear()  # Clear redo stack when new command is executed
