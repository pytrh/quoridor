"""
GameState module.
"""
from src.graph import Graph
from src.player import Player

class GameState:
    """
    GameState class encapsulating the current player,
    the board, the players and the history of moves.
    """
    def __init__(self, size: int = 9, current_player: int = None, players: list[Player] = [[]],
                 blitz_mode: bool = False, history: list[list[str]] = [[]]):
        """
        Initialize a new game state.
        :param size: The size of the board, default is 9.
        :type size: int
        :param current_player: The current player, default is None.
        :type current_player: int
        :param players: The players in the game, default is an empty list.
        :type players: list[Player]
        :param blitz_mode: Whether the game is in blitz mode, default is False.
        :type blitz_mode: bool
        :param history: The history of moves, default is an empty list.
        :type history: list[list[str]]
        """
        self.board = self.create_board(size)
        self.current_player = current_player
        self.players = players
        self.blitz_mode = blitz_mode
        self.history = history
        self.move_count = 0

    def create_board(self, size: int = 9) -> Graph:
        """
        Create a board represented by an undirected graph.
        :param size: The size of the board, default is 9.
        :type size: int
        :return: The board as an undirected graph.
        :rtype: Graph
        """
        board = Graph()
        for i in range(size):
            for j in range(size):
                board.add_node((i, j))
        for i in range(size):
            for j in range(size):
                if i < size - 1:
                    board.add_edge((i, j), (i + 1, j))
                if j < size - 1:
                    board.add_edge((i, j), (i, j + 1))
        return board
