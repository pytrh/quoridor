"""
An abstract base class for game engines.
"""

from abc import ABC, abstractmethod

class GameEngine(ABC):
    @abstractmethod
    def render_board(self):
        """
        Render the board.
        """
        pass

    @abstractmethod
    def get_player_command(self):
        """
        Get the player command.
        """
        pass