"""
CLI Game Engine.
"""

from quoridor.gameengine import GameEngine
from quoridor.gamestate import GameState
from quoridor.direction import Direction
from quoridor.exceptions import InvalidMoveError


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

    def print_board(self):
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
