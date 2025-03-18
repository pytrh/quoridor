"""
An abstract base class for game engines.
"""

from abc import ABC, abstractmethod
from quoridor.command import Command

class GameEngine(ABC):
    @abstractmethod
    def render_board(self):
        """
        Render the board.
        """
        pass

    @abstractmethod
    def get_command_from_human_player(self) -> Command:
        """
        Get the player command.
        """
        pass

    def print_remaining_fences(self):
        """
        Print the remaining fences for each player.
        """
        pass

    def render_game_over(self):
        """
        Render the game over screen.
        """
        pass