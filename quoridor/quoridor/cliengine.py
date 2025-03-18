"""
CLI Game Engine.
"""

from quoridor.gameengine import GameEngine
from quoridor.gamestate import GameState
from quoridor.direction import Direction
from quoridor.exceptions import InvalidMoveError, InvalidCommandError
from quoridor.command import Command, CommandType


class CLIEngine(GameEngine):
    """
    CLIEngine handles the CLI interface of the quoridor game.
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

        # Create rows and columns based on the board size (from 3 to 15)
        self.rows = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o'][:self.size]
        self.columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15'][:self.size]

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

    def render_board(self):
        """
        Print the board on the terminal
        """
        horizontal_wall = "---"
        vertical_wall = "|"
        interstice = "+"
        horizontal_space = "   "  # Must be of the same size than horizontal_wall
        big_space = "  "
        small_space = " "  # Must be of the size of big_space -1
        "  +" + "---+" * self.state.size

        print(
            "    " + horizontal_space.join(str(i + 1) for i in range(self.size))
        )
        print(big_space + interstice + (horizontal_wall + interstice) * self.size)
        for row in range(self.size):
            print(f"{self.rows[row]}" + small_space + vertical_wall, end="")
            for columns in range(self.size):
                case = "   "
                for player in range(self.state.num_players):
                    if (
                        self.state.players[player].position[0] == row
                        and self.state.players[player].position[1] == columns
                    ):
                        case = " " + str(self.state.players[player].id + 1) + " "
                if columns == self.size - 1 or not self.state.board.edge_exists(
                    (row, columns), (row, columns + 1)
                ):
                    print(case + vertical_wall, end="")
                else:
                    print(case + " ", end="")
            print("")
            print(big_space + interstice, end="")
            for columns in range(self.size):
                if row == self.size - 1 or not self.state.board.edge_exists(
                    (row, columns), (row + 1, columns)
                ):
                    print(horizontal_wall, end="")
                else:
                    print(horizontal_space, end="")
                print(interstice, end="")
            print("")

    def print_remaining_fences(self):
        """
        Print the remaining fences for each player.
        """
        print("Remaining fences: " + str(self.state.players[self.state.current_player].fences_remaining))

    def get_input_from_human_player(self) -> str:
        """
        Get an input from the human player.
        """
        return input("Player " + str(self.state.current_player + 1) + " will play?")

    def well_formed_pawn_move(self, input: str) -> bool:
        """
        Check if the input is a well-formed pawn move.
        """
        return len(input) == 2 and input[0] in self.rows and input[1] in self.columns
    
    def well_formed_wall_placement(self, input: str) -> bool:
        """
        Check if the input is a well-formed wall placement.
        """
        return len(input) == 3 and input[0] in self.rows and input[1] in self.columns and input[2] in ["v", "h"]

    def get_command_from_human_player(self) -> Command:
        """
        Get a command from the human player.
        """
        input = self.get_input_from_human_player()
        if input == "undo":
            return Command.create_simple_command(CommandType.UNDO)
        elif input == "redo":
            return Command.create_simple_command(CommandType.REDO)
        elif input == "quit":
            return Command.create_simple_command(CommandType.QUIT)
        elif input == "restart":
            return Command.create_simple_command(CommandType.RESTART)
        elif self.well_formed_pawn_move(input):
            return Command.create_move_command(self.translate_move(input))
        elif self.well_formed_wall_placement(input):
            return Command.create_wall_command(self.translate_wall(input))
        else:
            raise InvalidCommandError

    def render_game_over(self):
        """
        Render the game over screen.
        """
        print(f"Player {self.state.current_player + 1} has won the game!")