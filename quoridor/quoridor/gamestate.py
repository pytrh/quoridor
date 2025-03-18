"""
GameState module.
"""

from quoridor.graph import Graph
from quoridor.player import Player
from quoridor.direction import Direction


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

        # Players placement
        middle_board = size // 2
        print(middle_board)
        players = [
            Player(0, (middle_board, 0), size, num_walls),
            Player(1, (middle_board, size - 1), size, num_walls),
        ]
        if num_players > 2:
            players.append(Player(2, (0, middle_board), size, num_walls))
        if num_players > 3:
            players.append(Player(3, (size - 1, middle_board), size, num_walls))
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
        """
        Check if a wall exist in this position (that both path that should be
        blocked by that wall does not exist)
        :param x: Horizontal position.
        :type x: int
        :param y: Vertical position.
        :type y: int
        :param direction: The orientation of the wall
        :type direction: Direction
        :return: Whether or not the wall exist
        :rtype: bool
        """
        if direction == Direction.H:
            edges = [((x, y), (x + 1, y)), ((x, y + 1), (x + 1, y + 1))]
        elif direction == Direction.V:
            edges = [((x, y), (x, y + 1)), ((x + 1, y), (x + 1, y + 1))]
        return not (
            self.board.edge_exists(edges[0][0], edges[0][1])
            or self.board.edge_exists(edges[1][0], edges[1][1])
        )

    def game_over(self) -> bool:
        """
        Check if the game is in a winning position for a player
        :return: Is the game finished?
        :rtype: bool
        """
        match self.current_player:
            case 0:
                if self.players[self.current_player].position[1] == self.size - 1:
                    return True
            case 1:
                if self.players[self.current_player].position[1] == 0:
                    return True
            case 2:
                if self.players[self.current_player].position[0] == self.size - 1:
                    return True
            case 3:
                if self.players[self.current_player].position[0] == 0:
                    return True
        return False
