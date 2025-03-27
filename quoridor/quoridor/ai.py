"""
AI Module contains a list of functions that takes a GameState and returns a move.
The utility functions that they use could be moved elsewhere in the future.
"""

from quoridor.graph import Graph
from quoridor.command import Command, PlaceWallCommand, MovePawnCommand
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quoridor.gamestate import GameState

class AI(ABC):
    """
    Abstract base class for AI classes.
    """

    @abstractmethod
    def suggest_move(self, state: "GameState") -> Command:
        """
        Suggest a move.
        :param state: The current game state
        :return: A command to execute
        """
        pass

class GreedyAI(AI):
    """
    Returns a pawn move that has the shortest path to a winning position.
    """
    def suggest_move(self, state: "GameState") -> MovePawnCommand:
        """
        :param state: The current game state
        :return: A MovePawnCommand.
        """
        player = state.players[state.current_player.id]
        current_pos = player.position
        best_path = None
        for goal in player.goal_line:
            path = state.board.a_star(current_pos, goal)
            if best_path is None or len(path) < len(best_path):
                best_path = path
        
        return MovePawnCommand(state, current_pos, best_path[1])
