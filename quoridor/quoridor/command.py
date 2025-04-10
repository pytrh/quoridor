"""
Command module handling both game operations and undo/redo/restart/quit etc.
List of commands:
Commands of which execute() return True:
- PlaceWallCommand
- MovePawnCommand
- PassCommand
Commands of which execute() return False:
- UndoCommand
- RedoCommand
- RestartCommand Never started
- AbandonCommand Lucas is working on it
- SaveCommand in progress
- QuitCommand
"""

from abc import ABC, abstractmethod
from copy import deepcopy
import logging
from typing import Optional, Tuple, List, TYPE_CHECKING
import os

from quoridor.io import ReadWriteHistory
from quoridor.graph import Graph
from quoridor.direction import Direction
from quoridor.exceptions import (
    InvalidMoveError,
    PathNotFoundError,
    GameOver,
    NoUndoableCommand,
    NoRedoableCommand,
    QuitApp,
)
from quoridor.translations import T_

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

    def update_wall(self):
        """
        Decrement the walls remaining of the current player
        """
        self.state.players[self.state.current_player.id].walls_remaining = (
            self.state.players[self.state.current_player.id].walls_remaining - 1
        )

    # def get_string_from_board(self) -> str: # NOTE: never used implemented elsewhere
    #     """
    #     Return the board in string format
    #     """
    #     horizontal_wall = "---"
    #     vertical_wall = "|"
    #     interstice = "+"
    #     horizontal_space = "   "  # Must be of the same size than horizontal_wall
    #     big_space = "  "
    #     small_space = " "  # Must be of the size of big_space -1
    #     "  +" + "---+" * self.state.size

    #     result = "    " + horizontal_space.join(str(i + 1) for i in range(self.size))
    #     result += "\n"
    #     result += big_space + interstice + (horizontal_wall + interstice) * self.size
    #     for row in range(self.size):
    #         result += f"\n{self.rows[row]}" + small_space + vertical_wall
    #         for columns in range(self.size):
    #             case = "   "
    #             for player in range(self.state.num_players):
    #                 if (
    #                     self.state.players[player].position[0] == row
    #                     and self.state.players[player].position[1] == columns
    #                 ):
    #                     # case = " " + str(self.state.players[player].id + 1) + " "
    #                     case = " " + str(player + 1) + " "
    #             if columns == self.size - 1 or not self.state.board.edge_exists(
    #                 (row, columns), (row, columns + 1)
    #             ):
    #                 result += case + vertical_wall
    #             else:
    #                 result += case + " "
    #         result += "\n" + big_space + interstice
    #         for columns in range(self.size):
    #             if row == self.size - 1 or not self.state.board.edge_exists(
    #                 (row, columns), (row + 1, columns)
    #             ):
    #                 result += horizontal_wall
    #             else:
    #                 result += horizontal_space
    #             result += interstice
    #     return result

    rows = [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
    ]


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
        except (InvalidMoveError, PathNotFoundError) as e:
            raise e
        return True

    # Directly from legacy gamestatemanager.py
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
        self.player.walls_remaining += 1
        if self.orientation == Direction.H:
            self.state.board.add_edge(
                self.position, (self.position[0] + 1, self.position[1])
            )
            self.state.board.add_edge(
                (self.position[0], self.position[1] + 1),
                (self.position[0] + 1, self.position[1] + 1),
            )
        else:
            self.state.board.add_edge(
                self.position, (self.position[0], self.position[1] + 1)
            )
            self.state.board.add_edge(
                (self.position[0] + 1, self.position[1]),
                (self.position[0] + 1, self.position[1] + 1),
            )
        self.state.backward_player()

    def redo(self) -> None:
        """Re-place the wall that was removed."""
        self.player.walls_remaining -= 1
        if self.orientation == Direction.H:
            self.state.board.remove_edge(
                self.position, (self.position[0] + 1, self.position[1])
            )
            self.state.board.remove_edge(
                (self.position[0], self.position[1] + 1),
                (self.position[0] + 1, self.position[1] + 1),
            )
        else:
            self.state.board.remove_edge(
                self.position, (self.position[0], self.position[1] + 1)
            )
            self.state.board.remove_edge(
                (self.position[0] + 1, self.position[1]),
                (self.position[0] + 1, self.position[1] + 1),
            )
        self.state.switch_player()

    def __str__(self) -> str:
        return f"{self.rows[self.position[0]]}{self.position[1] + 1}{self.orientation.name.lower()}"


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
            raise InvalidMoveError(f"Try to move from {start} to {end}")
        else:
            board_temp = self.state.temp_board()
            if not board_temp.edge_exists(start, end):
                raise InvalidMoveError(f"Try to move from {start} to {end}")
            self.state.players[self.state.current_player.id].position = end

    def undo(self) -> None:
        """Move the pawn back to its previous position."""
        self.player = self.state.players[self.player.id]
        self.player.position = self.from_position
        self.state.backward_player()

    def redo(self) -> None:
        """Move the pawn to its new position again."""
        self.player = self.state.players[self.player.id]
        self.player.position = self.to_position
        self.state.switch_player()

    def __str__(self) -> str:
        return f"{self.rows[self.from_position[0]]}{self.from_position[1] + 1}-{self.rows[self.to_position[0]]}{self.to_position[1] + 1}"


class UndoCommand(Command):
    """Command to undo the last game action."""

    def __init__(self, state: "GameState"):
        super().__init__(state)

    def execute(self) -> bool:
        """Undo the last command in the command history."""
        # print(f"Len of history: {len(self.state.history)}")
        if not self.state.history:
            raise NoUndoableCommand

        # Normal undo
        if len(self.state.history) > 0:
            player_id, last_command = self.state.history.pop()
            self.state.redo_stack.append((player_id, last_command))
            logging.debug(f"Last command: {last_command}")
            logging.debug(f"Size of redo stack: {len(self.state.redo_stack)}")
            last_command.undo()

        # While the current player is an ai
        # We keep undo-ing a move until we found an human player
        while (
            self.state.current_player.id in self.state.ai_ids
            and len(self.state.history) > 0
        ):
            player_id, last_command = self.state.history.pop()
            self.state.redo_stack.append((player_id, last_command))
            logging.debug(f"Last command: {last_command}")
            logging.debug(f"Size of redo stack: {len(self.state.redo_stack)}")
            last_command.undo()
        return False

    def __str__(self) -> str:
        return "Undo last move"


class RedoCommand(Command):
    """Command to redo a previously undone action."""

    def __init__(self, state: "GameState"):
        super().__init__(state)

    def execute(self) -> bool:
        """Redo the last undone command."""
        logging.debug(
            f"Size of redo stack right before bug: {len(self.state.redo_stack)}"
        )
        if not self.state.redo_stack:
            raise NoRedoableCommand

        player_id, command = self.state.redo_stack.pop()
        logging.debug(f"Command to redo: {command}")
        command.redo()
        self.state.history.append((player_id, command))
        return False

    def __str__(self) -> str:
        return "Redo previously undone move"


class RestartCommand(Command):
    """Command to restart the game."""

    def __init__(self, state: "GameState", initial_state: "GameState"):
        super().__init__(state)
        self.restart_state = initial_state.copy_state()

    def execute(self) -> bool:
        """Restart the game to its initial state."""
        self.state.set_state(self.restart_state)
        self.state.redo_stack.clear()
        self.state.history.clear()
        for player in self.state.players:
            if player.timer:
                player.timer.end_turn()
        return False

    def __str__(self) -> str:
        return "Restart game"


class AbandonCommand(Command):
    """Command to abandon the current game."""

    def __init__(self, state: "GameState", player_id: int):
        super().__init__(state)
        self.player = self.state.players[player_id]

    def execute(self) -> bool:
        """Abandon the current game, declaring the opponent as winner if only one player is left"""
        if len(self.state.players) == 1:
            raise GameOver
        else:
            """Simply remove the current player from the game"""
            self.state.num_players_remaining -= 1
            self.player.is_dead = True

            from quoridor.gamemode import GameMode

            if self.state.game_mode.display_name == GameMode.BLITZ:
                if self.player.timer.turn_start_time is not None:
                    self.player.timer.end_turn()
                    self.player.timer.display_lock.clear()
        return True

    def undo(self) -> None:
        """Append the abandonned player into players list"""
        self.state.num_players_remaining += 1
        self.player.is_dead = False
        self.state.backward_player()

    def redo(self) -> None:
        self.state.num_players_remaining -= 1
        self.player.is_dead = True

        from quoridor.gamemode import GameMode

        if self.state.game_mode.display_name == GameMode.BLITZ:
            if self.player.timer.turn_start_time is not None:
                self.player.timer.end_turn()
                self.player.timer.display_lock.clear()

        self.state.switch_player()

    def __str__(self) -> str:
        return f"Abandon game (Player {self.state.current_player.id} surrenders)"


class QuitCommand(Command):
    """Command to quit the application."""

    def __init__(self, state: "GameState"):
        super().__init__(state)

    def execute(self) -> bool:
        """Quit the application."""
        raise QuitApp

    def __str__(self) -> str:
        return "Quit application"


class SaveAndQuitCommand(Command):
    """Command to quit the application."""

    def __init__(self, state: "GameState", file: str):
        super().__init__(state)
        self.file = file

    def execute(self) -> bool:
        from quoridor.parser import parse_state_to_string
        from quoridor.io import write_to_file

        """Quit the application."""
        # demander à l'utilisateur s'il veut sauvegarder la partie ou non dans un fichier
        FileContent = parse_state_to_string(self.state)
        write_to_file(self.file, FileContent)
        raise QuitApp

    def __str__(self) -> str:
        return "Quit application"


class TimeCommand(Command):
    """Command to display the time remaining on the player's timer."""

    def __init__(self, state: "GameState"):
        super().__init__(state)

    def execute(self) -> bool:
        """Display the time remaining on the player's timer"""
        print(
            "\r" + T_("[⏳ Remaining: {seconds}]").format(
                seconds=f"{self.state.current_player.timer.remaining}s"
            )
        )
        return False

    def __str__(self) -> str:
        return "Time player"


class HelpCommand(Command):
    """Command to display the list of available commands."""

    def __init__(self, state: "GameState"):
        super().__init__(state)

    def execute(self) -> bool:
        """Display the help menu with all available commands"""
        print("\n--- Available Commands ---")
        print(" undo       : Undo the last move")
        print(" redo       : Redo the last undone move")
        print(" quit       : Quit the game")
        print(" restart    : Restart the game from the beginning")
        print(" abandon    : Abandon the game")
        print(" time       : Show elapsed time")
        print(" help or h  : Show this help menu")
        print(" save       : save history")
        print(" history    : display history")
        print()
        print("To move     : type a direction followed by a number (e.g. 'e4')")
        print()
        print("To place a wall:")
        print("   - Horizontal wall → e.g. 'e4h'")
        print("   - Vertical wall   → e.g. 'e4v'")
        print("--------------------------\n")
        return False

    def __str__(self) -> str:
        return "Help"


class SaveCommand(Command):
    """Command to save history."""

    def __init__(self, state: "GameState", filename: str):
        super().__init__(state)
        self.filename = filename

    def execute(self) -> bool:
        """Command to save history"""
        ReadWriteHistory.write_history(
            self.filename,
            ReadWriteHistory.parse_history_to_list_of_str(
                self.state.history, self.state
            ),
        )
        return False

    def __str__(self) -> str:
        return "Save history"


class HistoryCommand(Command):
    """Command to display the history of the current game."""

    def __init__(self, state: "GameState"):
        super().__init__(state)

    def execute(self) -> bool:
        """Display the history of the current game"""
        history = ReadWriteHistory.parse_history_to_list_of_str(
            self.state.history, self.state
        )
        for turn_index, turn in enumerate(history, start=1):
            print(f"Turn {turn_index}:", end=" ")
            for move in turn:
                print(move, end=" ")
            print()
        return False

    def __str__(self) -> str:
        return "Display History"


class PassCommand(Command):
    """Command to pass the player's turn."""

    def __init__(self, state: "GameState"):
        super().__init__(state)

    def execute(self) -> bool:
        """Command to pass the player's turn."""
        return self.state.check_pass_player(self.state.current_player.id)

    def __str__(self) -> str:

        return "Pass"

    def undo(self) -> None:
        self.state.backward_player()

    def redo(self) -> None:
        self.state.switch_player()
