"""
GameStateManager module.
"""

import copy
from quoridor.gamestate import GameState
from quoridor.graph import Graph
from quoridor.exceptions import InvalidMoveError, PathNotFoundError
from quoridor.direction import Direction
from quoridor.cliengine import CLIEngine

class GameStateManager:
    """
    GameStateManager manage the functionnality of the application:
    the treatment that can be applied to the board
    """

    def __init__(self, gamestate: GameState, engine: CLIEngine):
        self.state = gamestate
        self.engine = engine

    def switch_player(self):
        """
        Change the current player to the next one
        If current player is the last one, the next one will the first
        """
        self.state.current_player = (
            self.state.current_player + 1
        ) % self.state.num_players

    def update_wall(self):
        """
        Remove one fence to the fences counter of the current player
        """
        self.state.players[self.state.current_player].fences_remaining = (
            self.state.players[self.state.current_player].fences_remaining - 1
        )

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
        board = copy.deepcopy(self.state.board)
        p = [(), (), (), ()]
        for i in range(self.state.num_players):
            p[i] = self.state.players[i].position
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        x, y = p[self.state.current_player]
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

    def make_move(self, start: tuple[int, int], end: tuple[int, int]):
        """
        Try to make the current player do the movement between two position.
        Raise an exception if the move is impossible.
        :param start: The initial position of the current player.
        :type start: tuple[int, int]
        :param end: The position of the current player after the move.
        :type end: tuple[int, int]
        :raises InvalidMoveError: if the parameters lead to an invalid move
        """
        if not (self.state.players[self.state.current_player].position == start):
            raise InvalidMoveError
        else:
            board_temp = self.temp_board()
            if not board_temp.edge_exists(start, end):
                raise InvalidMoveError
            self.state.players[self.state.current_player].position = end

    def place_wall(self, x: int, y: int, direction: Direction):
        """
        Try to place a wall in the given position and direction
        :param x: The row of the wall placement
        :type x: int
        :param y: The column of the wall placement
        :type y: int
        :param direction: The direction in which the wall is placed
        :type direction: Direction
        :raises InvalidMoveError: if the parameters lead to an impossible
        wall placement
        """

        # Check that the current player still has wall remaining
        if self.state.players[self.state.current_player].fences_remaining == 0:
            raise InvalidMoveError

        # Check that the wall is placed within the board
        if x >= self.state.size - 1 or y >= self.state.size - 1:
            raise InvalidMoveError

        # Check if we are trying to put a wall inside of another wall
        if self.state.wall_exist(x, y, direction.inverse()):
            raise InvalidMoveError

        # Create a temporary board
        temp_board = copy.deepcopy(self.state.board)

        if (
            direction == Direction.H
            and self.state.players[self.state.current_player].fences_remaining > 0
        ):  # Horizontal wall
            if temp_board.edge_exists((x, y), (x + 1, y)) and temp_board.edge_exists(
                (x, y + 1), (x + 1, y + 1)
            ):
                temp_board.remove_edge((x, y), (x + 1, y))
                temp_board.remove_edge((x, y + 1), (x + 1, y + 1))
            else:
                raise InvalidMoveError

        elif (
            direction == Direction.V
            and self.state.players[self.state.current_player].fences_remaining > 0
        ):  # Vertical wall
            if temp_board.edge_exists((x, y), (x, y + 1)) and temp_board.edge_exists(
                (x + 1, y), (x + 1, y + 1)
            ):
                temp_board.remove_edge((x, y), (x, y + 1))
                temp_board.remove_edge((x + 1, y), (x + 1, y + 1))
            else:
                raise InvalidMoveError

        # Check if all the players can still win
        for i in range(0, self.state.num_players):
            path = False
            for j in range(0, len(self.state.players[i].winning_position)):
                try:
                    temp_board.a_star(
                        self.state.players[i].position,
                        self.state.players[i].winning_position[j],
                    )
                    path = True
                    break
                except PathNotFoundError:
                    continue
            if path == False:
                raise PathNotFoundError

        # If the temporary board is valid, update the original
        self.state.board = temp_board
        self.update_wall()

    def start_game(self):
        self.print_board()
        while True:
            try:
                print(
                    "Remaining fences: "
                    + str(
                        self.state.players[self.state.current_player].fences_remaining
                    )
                )
                move = input(
                    "Player " + str(self.state.current_player + 1) + " will play?"
                )
                if len(move) == 3:
                    x, y, direction = CLIEngine.translate_wall(move)
                    self.place_wall(x, y, direction)
                else:
                    move = move.split("-")
                    if len(move) != 2:
                        raise InvalidMoveError
                    if CLIEngine.invalid_move(move[0], move[1]):
                        raise InvalidMoveError
                    start = self.translate_move(move[0])
                    end = self.translate_move(move[1])
                    self.make_move(start, end)
                self.print_board()
                if self.state.game_over():
                    print(
                        "Player "
                        + str(self.state.current_player + 1)
                        + " has won the game!"
                    )
                    exit()
                self.switch_player()
            except (InvalidMoveError, PathNotFoundError):
                print("Invalid move!")