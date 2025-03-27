"""
Run the quoridor game in the terminal.
"""

import copy
from quoridor.gamestate import GameState
from quoridor.direction import Direction
from quoridor.command import (
    Command,
    PlaceWallCommand,
    MovePawnCommand,
    UndoCommand,
    RedoCommand,
    RestartCommand,
    QuitCommand,
    AbandonCommand,
)
from quoridor.exceptions import (
    InvalidMoveError,
    InvalidCommandError,
    PathNotFoundError,
    NoUndoableCommand,
    NoRedoableCommand,
    GameOver,
)


class CLIEngine:
    """
    Handles the CLI interface and launches the quoridor game.
    """

    def __init__(self, gamestate: GameState):
        """
        TerminalClient manage the application from the terminal.
        Parse the terminal input and update the board by printing it on
        the terminal.
        :param gamestate: The current state of the board.
        :type gamestate: GameState
        """
        self.state = gamestate
        self.size = gamestate.size
        self.initial_state = copy.deepcopy(gamestate)

        # Create rows and columns based on the board size (from 3 to 15)
        self.rows = [
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
        ][: self.size]
        self.columns = [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
        ][: self.size]

    def execute_command(self, command: Command) -> bool:
        """
        Execute a command and add it to the command history.
        """
        result = command.execute()
        # print(f"Executed command: {command}")
        # print(f"result: {result}")
        if result:
            self.state.history.append(command)
            print(f"Executed command: {command}")
            self.state.redo_stack.clear()  # Clear redo stack when new command is executed
            if self.state.game_over():
                self.render_game_over()
            else:
                self.state.switch_player()
        return result

    def translate_move(self, case: str) -> tuple[int, int]:
        """
        Transform a string input into a position tuple that can be read
        by GameLogic
        :param case: String in format 'letter''number'
        :type case: str
        :return: a position
        :rytpe: tuple[int,int]
        """
        x = self.rows.index(case[0])
        y = self.columns.index(case[1])
        if x == -1 or y == -1:
            raise InvalidMoveError
        return (x, y)

    def translate_wall(self, case: str) -> tuple[int, int, Direction]:
        """
        Transform a string input into a position tuple + a direction
        that can be read by GameLogic
        :param case: String in format 'letter''number''direction'
        :type case: str
        :return: a position + a direction
        :rytpe: tuple[int,int, Direction]
        """
        x = self.rows.index(case[0])
        y = self.columns.index(case[1])
        direction = None
        if case[2] == "v":
            direction = Direction.V
        elif case[2] == "h":
            direction = Direction.H
        if x == -1 or y == -1 or direction == None:
            raise InvalidMoveError
        return (x, y, direction)

    def invalid_move(self, start: str, end: str) -> bool:
        """
        Check if either of the two string that compose a move are invalid.
        :param start: String in format 'letter''number'
        :type case: str
        :param end: String in format 'letter''number'
        :type case: str
        :return: true if the move is invalid, false if the move is valid
        :rytpe: bool
        """
        if len(start) == 2 and len(end) == 2:
            if (
                self.rows.index(start[0]) == -1
                or self.rows.index(end[0]) == -1
                or self.columns.index(start[1]) == -1
                or self.columns.index(end[1]) == -1
            ):
                return True
            return False
        return True

    def get_string_from_board(self) -> str:
        """
        Return the board in string format
        """
        horizontal_wall = "---"
        vertical_wall = "|"
        interstice = "+"
        horizontal_space = "   "  # Must be of the same size than horizontal_wall
        big_space = "  "
        small_space = " "  # Must be of the size of big_space -1
        "  +" + "---+" * self.state.size

        result = "    " + horizontal_space.join(str(i + 1) for i in range(self.size))
        result += "\n"
        result += big_space + interstice + (horizontal_wall + interstice) * self.size
        for row in range(self.size):
            result += f"\n{self.rows[row]}" + small_space + vertical_wall
            for columns in range(self.size):
                case = "   "
                for player in range(self.state.num_players):
                    if (
                        self.state.players[player].position[0] == row
                        and self.state.players[player].position[1] == columns
                    ):
                        # case = " " + str(self.state.players[player].id + 1) + " "
                        case = " " + str(player + 1) + " "
                if columns == self.size - 1 or not self.state.board.edge_exists(
                    (row, columns), (row, columns + 1)
                ):
                    result += case + vertical_wall
                else:
                    result += case + " "
            result += "\n" + big_space + interstice
            for columns in range(self.size):
                if row == self.size - 1 or not self.state.board.edge_exists(
                    (row, columns), (row + 1, columns)
                ):
                    result += horizontal_wall
                else:
                    result += horizontal_space
                result += interstice
        return result

    def render_board(self):
        """
        Print the board on the terminal
        """
        print(self.get_string_from_board())

    def print_remaining_walls(self):
        """
        Print the remaining walls for each player.
        """
        print(
            "Remaining walls: "
            + str(self.state.players[self.state.current_player.id].walls_remaining)
        )

    def get_input_from_human_player(self) -> str:
        """
        Get an input from the human player.
        """
        return input("Player " + str(self.state.current_player.id + 1) + " will play?")

    def well_formed_pawn_move(self, input: str) -> bool:
        """
        Check if the input is a well-formed pawn move.
        """
        return len(input) == 2 and input[0] in self.rows and input[1] in self.columns

    def well_formed_wall_placement(self, input: str) -> bool:
        """
        Check if the input is a well-formed wall placement.
        """
        return (
            len(input) == 3
            and input[0] in self.rows
            and input[1] in self.columns
            and input[2] in ["v", "h"]
        )

    def render_game_over(self):
        """
        Render the game over screen.
        """
        print(f"Player {self.state.current_player.id + 1} has won the game!")

    def get_command_from_human_player(self) -> Command:
        """
        Get a command from the human player.
        """
        input = self.get_input_from_human_player()
        if input == "undo":
            return UndoCommand(self.state)
        elif input == "redo":
            return RedoCommand(self.state)
        elif input == "quit":
            return QuitCommand(self.state)
        elif input == "restart":
            return RestartCommand(self.state, self.initial_state)
        elif input == "abandon":
            return AbandonCommand(self.state)
        elif self.well_formed_pawn_move(input):
            x, y = self.translate_move(input)
            a, b = self.state.players[self.state.current_player.id].position
            return MovePawnCommand(self.state, (a, b), (x, y))
        elif self.well_formed_wall_placement(input):
            x, y, direction = self.translate_wall(input)
            return PlaceWallCommand(self.state, (x, y), direction)
        else:
            raise InvalidCommandError("Invalid command format")

    def start_game(self):
        """
        Start the game loop.
        """
        self.render_board()
        while True:
            try:
                self.print_remaining_walls()
                if self.state.current_player.id not in self.state.ai_controllers:
                    command = self.get_command_from_human_player()
                else:
                    command = self.state.ai_controllers[self.state.current_player.id].suggest_move()
                print(f"Command: {command}")

                # Execute the command directly
                self.execute_command(command)

                self.render_board()
                if self.state.game_over():
                    raise GameOver
                    # self.render_game_over()
                    # exit()

            except InvalidMoveError as e:
                print(f"Invalid move: {str(e)}")
            except PathNotFoundError:
                print("Cannot place wall: it would block a player's path to goal")
            except NoUndoableCommand:
                print("No move to undo")
            except NoRedoableCommand:
                print("No command to redo")
            except InvalidCommandError as e:
                print(f"Invalid command: {str(e)}")
            except GameOver:
                self.render_game_over()
                exit()
