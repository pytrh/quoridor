"""
Exceptions module.

This module defines custom exception classes for the Quoridor game.

Classes:
    NodeNotFoundError: Raised when trying to access a node that is not in the graph.
    EdgeNotFoundError: Raised when trying to access an edge that is not in the graph.
    PathNotFoundError: Raised when there is no path between two nodes.
    InvalidMoveError: Raised when an invalid move is attempted in the game.
    GameOver: Raised when the game is over.
    NoUndoableCommand: Raised when there is no command to undo.
"""

class NodeNotFoundError(Exception):
    """Exception raised when a node is not found in the graph."""
    pass

class EdgeNotFoundError(Exception):
    """Exception raised when an edge is not found in the graph."""
    pass

class PathNotFoundError(Exception):
    """Exception raised when there is no path between two nodes."""
    pass

class InvalidMoveError(Exception):
    """Exception raised when an invalid move is attempted in the game."""
    pass 

class InvalidCommandError(Exception):
    """Exception raised when an invalid command is attempted in the game."""
    pass

class GameOver(Exception):
    """Exception raised when the game is over."""
    pass

class NoUndoableCommand(Exception):
    """Exception raised when there is no command to undo."""
    pass

class NoRedoableCommand(Exception):
    """Exception raised when there is no command to redo."""
    pass