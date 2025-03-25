"""
AI Module contains a list of functions that takes a GameState and returns a move.
The utility functions that they use could be moved elsewhere in the future.
"""

from quoridor.gamestate import GameState
from quoridor.graph import Graph
from quoridor.command import Command, PlaceWallCommand, MovePawnCommand
from abc import ABC, abstractmethod


class AI(ABC):
    """
    Abstract base class for AI classes.
    """

    @abstractmethod
    def suggest_move(self) -> Command:
        """
        Suggest a move.
        """
        pass

class GreedyAI(AI):
    """
    Returns a pawn move that has the shortest path to a winning position.
    """
    def __init__(self, state: GameState):
        """
        :param state: The current game state.
        """
        self.state = state
        self.player = state.players[state.current_player.id]
        self.graph = state.board

    # def __init__(self, game_manger: GameManager):
    #     """
    #     Initialize the AI with a player and the game graph.
        
    #     :param player: The player controlled by the AI.
    #     :param graph: The graph representing the game board.
    #     """
    #     self.player = game_manger._state._players[game_manger._state._current_player]
    #     self.graph = game_manger._temp_board()

    def suggest_move(self) -> MovePawnCommand:
        """
        :return: A MovePawnCommand.
        """
        current_pos = self.player.position
        best_path = None
        for goal in self.player.winning_position:
            path = self.graph.a_star(current_pos, goal)
            if best_path is None or len(path) < len(best_path):
                best_path = path
        
        return MovePawnCommand(self.state, current_pos, best_path[1])
        