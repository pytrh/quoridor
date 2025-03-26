"""
Command module handling both game operations and undo/redo/restart/quit etc.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, List, TYPE_CHECKING
from copy import deepcopy

from quoridor.graph import Graph
from quoridor.direction import Direction
from quoridor.exceptions import InvalidMoveError, PathNotFoundError, GameOver

if TYPE_CHECKING:
    from quoridor.gamestate import GameState


class Command(ABC):
    """Abstract base class for all commands in the game."""

    def __init__(self, state: "GameState"):
        """Initialize the command with the game state."""
        self.state = state

    @abstractmethod
    def execute(self) -> bool:
        """Execute the command."""
        pass

    def undo(self) -> None:
        """
        Undo the command execution.
        By default, commands cannot be undone.
        Override this method for commands that support undo.
        """
        raise NotImplementedError("This command cannot be undone")

    def redo(self) -> None:
        """
        Redo the command execution.
        By default, commands cannot be redone.
        Override this method for commands that support redo.
        """
        raise NotImplementedError("This command cannot be redone")

    @abstractmethod
    def __str__(self) -> str:
        """Return a string representation of the command."""
        pass

    # TODO: Very ugly code, fix these 2 functions below
    def switch_player(self):
        """
        Change the current player to the next one
        If current player is the last one, the next one will the first
        """
        self.state.switch_player()

    def update_wall(self):
        """
        Remove one fence to the walls counter of the current player
        """
        self.state.players[self.state.current_player.id].walls_remaining = (
            self.state.players[self.state.current_player.id].walls_remaining - 1
        )


class PlaceWallCommand(Command):
    """Command to place a wall on the board."""

    def __init__(
        self, state: "GameState", position: Tuple[int, int], orientation: Direction
    ):
        super().__init__(state)
        self.position = position
        self.orientation = orientation
        self.player = self.state.players[self.state.current_player.id]

    def execute(self) -> bool:
        """Execute the command to place a wall."""
        try:
            self.place_wall(self.position[0], self.position[1], self.orientation)
            return True
        except (InvalidMoveError, PathNotFoundError) as e:
            raise e
        return False

    # Directly from legacy gamestatemanager.py
    # TODO: Move to PlaceWallCommand.execute()?
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
        if self.state.players[self.state.current_player.id].walls_remaining == 0:
            raise InvalidMoveError

        # Check that the wall is placed within the board
        if x >= self.state.size - 1 or y >= self.state.size - 1:
            raise InvalidMoveError

        # Check if we are trying to put a wall inside of another wall
        if self.state.wall_exist(x, y, direction.inverse()):
            raise InvalidMoveError

        # Create a temporary board
        temp_board = deepcopy(self.state.board)

        if (
            direction == Direction.H
            and self.state.players[self.state.current_player.id].walls_remaining > 0
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
            and self.state.players[self.state.current_player.id].walls_remaining > 0
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
            for j in range(0, len(self.state.players[i].goal_line)):
                try:
                    temp_board.a_star(
                        self.state.players[i].position,
                        self.state.players[i].goal_line[j],
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

    def undo(self) -> None:
        """Remove the wall that was placed."""
        self.state.board.remove_wall(self.position, self.orientation)
        self.player.walls_remaining += 1
        self.switch_player()

    def redo(self) -> None:
        """Re-place the wall that was removed."""
        self.execute()

    def __str__(self) -> str:
        return f"Place {self.orientation.name} wall at {self.position}"


class MovePawnCommand(Command):
    """Command to move a player's pawn on the board."""

    def __init__(
        self,
        state: "GameState",
        from_position: Tuple[int, int],
        to_position: Tuple[int, int],
    ):
        super().__init__(state)
        self.player = self.state.players[self.state.current_player.id]
        self.from_position = from_position
        self.to_position = to_position

    def execute(self) -> bool:
        """Move the current player's pawn in the specified direction."""
        try:
            self.make_move(self.from_position, self.to_position)
            return True
        except InvalidMoveError as e:
            raise e

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
        board = deepcopy(self.state.board)
        p = [(), (), (), ()]
        for i in range(self.state.num_players):
            p[i] = self.state.players[i].position
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        x, y = p[self.state.current_player.id]
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
        if not (self.state.players[self.state.current_player.id].position == start):
            raise InvalidMoveError
        else:
            board_temp = self.temp_board()
            if not board_temp.edge_exists(start, end):
                raise InvalidMoveError
            self.state.players[self.state.current_player.id].position = end

    def undo(self) -> None:
        """Move the pawn back to its previous position."""
        self.player.position = self.from_position
        self.switch_player()

    def redo(self) -> None:
        """Move the pawn to its new position again."""
        self.execute()

    def __str__(self) -> str:
        return f"Move pawn from {self.from_position} to {self.to_position}"


class UndoCommand(Command):
    """Command to undo the last game action."""

    def __init__(self, state: "GameState", history: List[Command] = None):
        super().__init__(state)
        # Allow an external history to be passed, but default to using state's history
        self.history = history if history is not None else state.history

    def execute(self) -> bool:
        """Undo the last command in the command history."""
        if self.history:
            last_command = self.history.pop()
            last_command.undo()
            self.state.redo_stack.append(last_command)
            return True
        return False

    def __str__(self) -> str:
        return "Undo last move"


class RedoCommand(Command):
    """Command to redo a previously undone action."""

    def __init__(self, state: "GameState", redo_stack: List[Command] = None):
        super().__init__(state)
        # Allow an external redo_stack to be passed, but default to using state's redo_stack
        self.redo_stack = redo_stack if redo_stack is not None else state.redo_stack

    def execute(self) -> bool:
        """Redo the last undone command."""
        if self.redo_stack:
            command = self.redo_stack.pop()
            result = command.execute()
            if result:
                self.state.history.append(command)
            return result
        return False

    def __str__(self) -> str:
        return "Redo previously undone move"


class RestartCommand(Command):
    """Command to restart the game."""

    def __init__(self, state: "GameState", initial_state: "GameState"):
        super().__init__(state)
        self.initial_state = deepcopy(initial_state)

    def execute(self) -> bool:
        """Restart the game to its initial state."""
        self.state = deepcopy(self.initial_state)
        return True

    def __str__(self) -> str:
        return "Restart game"


class AbandonCommand(Command):
    """Command to abandon the current game."""

    def __init__(self, state: "GameState"):
        super().__init__(state)

    def execute(self) -> bool:
        """Abandon the current game, declaring the opponent as winner if only one player is left"""
        if len(self.state.players) == 1:
            self.state.winner = self.state.players[
                1 if self.state.current_player.id == 0 else 0
            ]
            raise GameOver
        else:
            """Simply remove the current player from the game"""
            self.state.players.pop(self.state.current_player.id)
        return True

    def __str__(self) -> str:
        return f"Abandon game (Player {self.state.current_player.id} surrenders)"


class QuitCommand(Command):
    """Command to quit the application."""

    def __init__(self, state: "GameState"):
        super().__init__(state)

    def execute(self) -> bool:
        """Quit the application."""
        exit(0)

    def __str__(self) -> str:
        return "Quit application"
