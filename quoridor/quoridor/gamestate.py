"""
GameState module.
"""

from typing import List, TYPE_CHECKING
from quoridor.graph import Graph
from quoridor.player import Player
from quoridor.direction import Direction
from quoridor.config import (
    GRID_SIZE,
    NUM_PLAYERS,
    NUM_WALLS,
)

if TYPE_CHECKING:
    from quoridor.command import Command


class GameState:
    """
    GameState class encapsulating the current player,
    the board, the players and the history of moves.
    """

    def __init__(
        self,
        size: int = GRID_SIZE,
        current_player_id: int = 0,
        players: list[Player] = None,
        num_players: int = NUM_PLAYERS,
        board: Graph = None,
        blitz: bool = False,
        num_walls: int = NUM_WALLS,
        history: List["Command"] = None,
    ):
        """
         Initialize a new game state.
         :param size: The size of the board, default is 9.
         :type size: int
         :param current_player_id: The current player, default is 0.
         :type current_player_id: int
         :param players: The list of players, default is [Player(0, (0, 0), 0, 0), Player(1, (0, 0), 0, 0)].
         :type players: list[Player]
         :param board: The board, default is a new Graph().
         :type board: Graph
         :param blitz_mode: Whether the game is in blitz mode, default is False.
         :type blitz_mode: bool
         :param num_walls: The number of walls, default is 10.
         :type num_walls: int
         :param history: The history of moves, default is an empty list.
        :type history: list[Command]
        """
        self.board = board if board is not None else self.create_board(size)
        self.size = size
        self.num_players = num_players
        self.initial_num_walls = num_walls

        if players is None:
            middle_board = size // 2
            # print(middle_board)

            self.players = [
                Player(0, (middle_board, 0), size, num_walls),
                Player(1, (middle_board, size - 1), size, num_walls),
            ]
            if self.num_players > 2:
                self.players.append(Player(2, (0, middle_board), size, num_walls))
            if self.num_players > 3:
                self.players.append(
                    Player(3, (size - 1, middle_board), size, num_walls)
                )
        else:
            self.players = players
        self.current_player = (
            self.players[0]
            if current_player_id is None
            else self.players[current_player_id]
        )
        self.blitz = blitz
        self.history = [] if history is None else history
        self.redo_stack = []
        # self.move_count = 0

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
        if self.current_player.id == 0:
            if self.players[self.current_player.id].position[1] == self.size - 1:
                return True
        elif self.current_player.id == 1:
            if self.players[self.current_player.id].position[1] == 0:
                return True
        elif self.current_player.id == 2:
            if self.players[self.current_player.id].position[0] == self.size - 1:
                return True
        elif self.current_player.id == 3:
            if self.players[self.current_player.id].position[0] == 0:
                return True
        return False

    def switch_player(self):
        """
        Change the current player to the next one
        If current player is the last one, the next one will the first
        """
        self.current_player.id = (self.current_player.id + 1) % self.num_players
