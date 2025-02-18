"""
exceptions.py

This module defines custom exception classes for the Quoridor game.

Classes:
    NodeNotFoundError: Raised when trying to access a node that is not in the graph.
    EdgeNotFoundError: Raised when trying to access an edge that is not in the graph.
    PathNotFoundError: Raised when there is no path between two nodes.
    InvalidMoveError: Raised when an invalid move is attempted in the game.
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