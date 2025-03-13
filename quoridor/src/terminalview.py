"""
GameView module.
"""

from src.gamestate import GameState
from src.gamelogic import GameLogic
from src.exceptions import InvalidMoveError, PathNotFoundError
from src.direction import Direction


class TerminalView:

    rows = "abcdefghi"
    columns = "123456789"

    def __init__(self, gamestate: GameState):
        """
        TerminalClient manage the application from the terminal.
        Parse the terminal input and update the board by printing it on
        the terminal.
        :param gamestate: The current state of the board.
        :type gamestate: GameState
        """
        self.state = gamestate
        self.logic = GameLogic(gamestate)

    def translate_move(self, case: str) -> tuple[int, int]:
        """
        Transform a string input into a position tuple that can be read
        by GameLogic
        :param case: String in format 'letter''number'
        :type case: str
        :return: a position
        :rytpe: tuple[int,int]
        """
        x = TerminalView.rows.rfind(case[0])
        y = TerminalView.columns.rfind(case[1])
        if x == -1 or y == -1:
            raise InvalidMoveError
        return (x, y)

    def translate_wall(case: str) -> tuple[int, int, Direction]:
        """
        Transform a string input into a position tuple + a direction
        that can be read by GameLogic
        :param case: String in format 'letter''number''direction'
        :type case: str
        :return: a position + a direction
        :rytpe: tuple[int,int, Direction]
        """
        x = TerminalView.rows.rfind(case[0])
        y = TerminalView.columns.rfind(case[1])
        direction = None
        if case[2] == "v":
            direction = Direction.V
        elif case[2] == "h":
            direction = Direction.H
        if x == -1 or y == -1 or direction == None:
            raise InvalidMoveError
        return (x, y, direction)

    def invalid_move(start: str, end: str) -> bool:
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
                TerminalView.rows.rfind(start[0]) == -1
                or TerminalView.rows.rfind(end[0]) == -1
                or TerminalView.columns.rfind(start[1]) == -1
                or TerminalView.columns.rfind(end[1]) == -1
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
            "    " + horizontal_space.join(str(i + 1) for i in range(self.state.size))
        )
        print(big_space + interstice + (horizontal_wall + interstice) * self.state.size)
        for row in range(self.state.size):
            print(f"{TerminalView.rows[row]}" + small_space + vertical_wall, end="")
            for columns in range(self.state.size):
                case = "   "
                for player in range(self.state.num_players):
                    if (
                        self.state.players[player].position[0] == row
                        and self.state.players[player].position[1] == columns
                    ):
                        case = " " + str(self.state.players[player].id + 1) + " "
                if columns == self.state.size - 1 or not self.state.board.edge_exists(
                    (row, columns), (row, columns + 1)
                ):
                    print(case + vertical_wall, end="")
                else:
                    print(case + " ", end="")
            print("")
            print(big_space + interstice, end="")
            for columns in range(self.state.size):
                if row == self.state.size - 1 or not self.state.board.edge_exists(
                    (row, columns), (row + 1, columns)
                ):
                    print(horizontal_wall, end="")
                else:
                    print(horizontal_space, end="")
                print(interstice, end="")
            print("")

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
                    x, y, direction = TerminalView.translate_wall(move)
                    self.logic.place_wall(x, y, direction)
                else:
                    move = move.split("-")
                    if len(move) != 2:
                        raise InvalidMoveError
                    if TerminalView.invalid_move(move[0], move[1]):
                        raise InvalidMoveError
                    start = self.translate_move(move[0])
                    end = self.translate_move(move[1])
                    self.logic.make_move(start, end)
                self.print_board()
                if self.state.game_over():
                    print(
                        "Player "
                        + str(self.state.current_player + 1)
                        + " has won the game!"
                    )
                    exit()
                self.logic.switch_player()
            except (InvalidMoveError, PathNotFoundError):
                print("Invalid move!")
