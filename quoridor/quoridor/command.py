"""
Command module for easy encapsulation of commands.
"""

from enum import Enum
from typing import Optional, Tuple

class CommandType(Enum):
    MOVE_PAWN = "move_pawn"
    PLACE_WALL = "place_wall"
    UNDO = "undo"
    REDO = "redo"
    QUIT = "quit"
    RESTART = "restart"

class Command:
    """
    Command class to encapsulate different game commands.
    
    Attributes:
        type (CommandType): Type of command (required)
        from_position (tuple, optional): Starting position for pawn moves
        to_position (tuple, optional): Ending position for pawn moves
        wall_position (tuple, optional): Position for wall placement
        wall_orientation (str, optional): Orientation for wall placement ('h' or 'v')
    """
    def __init__(
        self,
        command_type: CommandType,
        from_position: Optional[Tuple[int, int]] = None,
        to_position: Optional[Tuple[int, int]] = None,
        wall_position: Optional[Tuple[int, int]] = None,
        wall_orientation: Optional[str] = None,
    ):
        self.type = command_type
        self.from_position = from_position
        self.to_position = to_position
        self.wall_position = wall_position
        self.wall_orientation = wall_orientation

    @classmethod
    def create_move_command(cls, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> 'Command':
        """Factory method for creating pawn move commands"""
        return cls(
            command_type=CommandType.MOVE_PAWN,
            from_position=from_pos,
            to_position=to_pos
        )

    @classmethod
    def create_wall_command(cls, position: Tuple[int, int], orientation: str) -> 'Command':
        """Factory method for creating wall placement commands"""
        return cls(
            command_type=CommandType.PLACE_WALL,
            wall_position=position,
            wall_orientation=orientation
        )

    @classmethod
    def create_simple_command(cls, command_type: CommandType) -> 'Command':
        """Factory method for creating simple commands (undo, redo, quit, etc)"""
        return cls(command_type=command_type)
