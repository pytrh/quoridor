"""
GameState module.
"""

from src.graph import Graph
from src.player import Player
from src.direction import Direction


class GameState:
    """
    GameState class encapsulating the current player,
    the board, the players and the history of moves.
    """

    def __init__(
        self,
        size: int = 9,
        num_players: int = 2,
        blitz_mode: bool = False,
        num_walls: int = 10,
        history: list[list[str]] = [[]],
    ):
        """
        Initialize a new game state.
        :param size: The size of the board, default is 9.
        :type size: int
        :param num_players: The number of players, default is 2.
        :type num_players: int
        :param blitz_mode: Whether the game is in blitz mode, default is False.
        :type blitz_mode: bool
        :param history: The history of moves, default is an empty list.
        :type history: list[list[str]]
        """
        self.board = self.create_board(size)
        self.size = size
        self.current_player = 0
        self.num_players = num_players
        players = [Player(0, (4, 0), num_walls), Player(1, (4, 8), num_walls)]
        if num_players > 2:
            players.append(Player(2, (0, 4), num_walls))
        if num_players > 3:
            players.append(Player(3, (4, 8), num_walls))
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

    def wall_exist(self, x: int, y: int, direction: Direction) -> bool:
        if direction == Direction.H:
            edges = [((x, y), (x + 1, y)), ((x, y + 1), (x + 1, y + 1))]
        elif direction == Direction.V:
            edges = [((x, y), (x, y + 1)), ((x + 1, y), (x + 1, y + 1))]
        return not (
            self.board.edge_exists(edges[0][0], edges[0][1])
            or self.board.edge_exists(edges[1][0], edges[1][1])
        )
