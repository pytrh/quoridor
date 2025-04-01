"""
GameState module.
"""

from copy import deepcopy
import logging
from typing import List, TYPE_CHECKING
from quoridor.ai import AI, GreedyAI, EasyAI
from quoridor.config import (
    DEFAULT_SIZE,
    DEFAULT_NUM_PLAYERS,
    DEFAULT_NUM_WALLS,
    DEFAULT_GAME_MODE,
    DEFAULT_BLITZ_TIME,
    GameMode,
)
from quoridor.direction import Direction
from quoridor.graph import Graph
from quoridor.player import Player
from quoridor.timer import Timer

if TYPE_CHECKING:
    from quoridor.command import Command


class GameState:
    """
    GameState class encapsulating the current player,
    the board, the players and the history of moves.
    """

    def __init__(
        self,
        size: int = DEFAULT_SIZE,
        current_player_id: int = 0,
        players: list[Player] = None,
        num_players: int = DEFAULT_NUM_PLAYERS,
        board: Graph = None,
        num_walls: int = DEFAULT_NUM_WALLS,
        history: List["Command"] = None,
        blitz_mode: GameMode = DEFAULT_GAME_MODE,
        blitz_time: int = DEFAULT_BLITZ_TIME,
        ai_ids: set = [],
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
        logging.debug("Creating GameState :")
        logging.debug(f"number of players : {num_players}")
        logging.debug(f"board size : {size}")
        logging.debug(f"number of walls : {num_walls}")
        logging.debug(f"blitz mode activated : {blitz_mode}")
        logging.debug(f"blitz timer : {blitz_time}")
        logging.debug(f"ai ids : {ai_ids}")

        self.board = board if board is not None else self.create_board(size)
        self.size = size
        self.num_players = num_players
        self.num_players_remaining = num_players
        self.initial_num_walls = num_walls
        self.ai_ids = ai_ids

        if players is None:
            middle_board = size // 2

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
        self.blitz_mode = blitz_mode
        self.history = [] if history is None else history
        self.redo_stack = []

        self.blitz_time = blitz_time

        if blitz_mode == GameMode.BLITZ:
            # conversion in seconds
            blitz_time = blitz_time * 60
            for i in range(num_players):
                self.players[i].timer = Timer(blitz_time, blitz_mode, i)

        if len(ai_ids) > 0:
            self.ai_controllers = {id: GreedyAI(0) for id in ai_ids}
        else:
            self.ai_controllers = {}

        logging.debug(f"List ai : {self.ai_controllers}")

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

    def temp_board(self) -> Graph:
        """
        Create a new graph that add and remove edges based on the position
        of players: Players next to each other can jump over the other.
        If the jump lead to a wall, border, or another player, the straight
        jump is replaced with two possible diagonal jump to the side of
        the other player. If those two diagonal jump are impossible, it's
        not possible to jump over the other player.
        :return: The modified board as an undirected graph.
        :rtype: Graph
        """
        board = deepcopy(self.board)
        p = [(), (), (), ()]
        for i in range(self.num_players):
            p[i] = self.players[i].position
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        x, y = p[self.current_player.id]
        for dx, dy in directions:
            adj = (x + dx, y + dy)
            jump = (x + 2 * dx, y + 2 * dy)

            if adj in p and board.edge_exists((x, y), adj):
                board.remove_edge((x, y), adj)

                if board.node_exists(jump) and board.edge_exists(adj, jump):
                    # Straight jump
                    board.add_edge((x, y), jump)
                else:
                    # Diagonal jump
                    side_directions = [(dy, dx), (-dy, -dx)]

                    for pdx, pdy in side_directions:
                        side_jump = (x + dx + pdx, y + dy + pdy)
                        if board.edge_exists(side_jump, adj):
                            board.add_edge((x, y), side_jump)

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

        if self.num_players_remaining == 1:
            return True
        return False

    def switch_player(self):
        """
        Change the current player to the next one
        If current player is the last one, the next one will the first
        """
        new_player_id = (self.current_player.id + 1) % self.num_players
        self.current_player = self.players[new_player_id]
        max = 4

        while self.current_player.is_dead or max <= 0:
            new_player_id = (new_player_id + 1) % self.num_players
            self.current_player = self.players[new_player_id]
            max -= 1

    def copy_state(self):
        """
        copy game state
        """
        new_list_players = [
            Player(
                player.id,
                player.position,
                self.size,
                player.walls_remaining,
                None,
                player.goal_line,
            )
            for player in self.players
        ]

        cloned_state = GameState(
            size=self.size,
            current_player_id=self.current_player.id,
            players=new_list_players,
            num_players=self.num_players,
            board=deepcopy(self.board),
            num_walls=self.initial_num_walls,
            history=deepcopy(self.history),
            blitz_mode=self.blitz_mode,
            blitz_time=self.blitz_time,
            ai_ids=deepcopy(self.ai_ids),
        )
        return cloned_state

    def set_state(self, state: "GameState"):  # type: ignore
        new_list_players = [
            Player(player.id, player.position, state.size, player.walls_remaining, None)
            for player in state.players
        ]

        self.size = state.size
        self.current_player_id = state.current_player.id
        self.current_player = state.players[self.current_player_id]
        self.players = new_list_players
        self.num_players = state.num_players
        self.num_players_remaining = state.num_players_remaining
        self.board = deepcopy(state.board)
        self.num_walls = state.initial_num_walls
        self.history = deepcopy(state.history)
        self.blitz_mode = state.blitz_mode
        self.blitz_time = state.blitz_time
        self.ai_ids = deepcopy(state.ai_ids)
        self.ai_controllers = deepcopy(state.ai_controllers)

    def backward_player(self):
        """
        Change the current player to the previous one
        If current player is the first one, the previous one will the last
        """
        self.current_player.id = (self.current_player.id - 1) % self.num_players
