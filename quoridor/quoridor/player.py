"""
Player module
"""

from quoridor.timer import Timer


class Player:
    """
    Player class to represent a player in the game.
    """

    def __init__(
        self,
        id: int,
        position: tuple[int, int],
        size: int,
        walls_remaining: int = 10,
        time_remaining_blitz: Timer = None,
        goal_line: list[tuple[int, int]] = None,
    ) -> None:
        """
        Initialize a new player.

        :param id: The id of the player either 1 or 2 or 3 or 4.
        :type id: int
        :param position: The position of the player represented as a tuple of two integers.
        :type position: tuple[int, int]
        :param size: The size of the board. Find a less ugly way to do this.
        :type size: int
        :param walls: The number of walls the player has, default is 10.
        :type walls: int
        :param time_remaining_blitz: A timer that counts down the remaining seconds for the player in blitz mode, default is None.
        :type time_remaining_blitz: Timer
        :param goal_line: The list of all winning position (the line opposed to the player starting line)
        :type goal_line: list[tuple[int, int]]
        """
        self.id = id
        self.position = position
        self.walls_remaining = walls_remaining
        self.timer = time_remaining_blitz
        self.start_position = position
        self.is_dead = False

        if goal_line is not None:
            self.goal_line = goal_line
        else:
            if self.id == 0:
                self.goal_line = [(i, size - 1) for i in range(size)]
            elif self.id == 1:
                self.goal_line = [(i, 0) for i in range(size)]
            elif self.id == 2:
                self.goal_line = [(size - 1, i) for i in range(size)]
            elif self.id == 3:
                self.goal_line = [(0, i) for i in range(size)]
            else:
                raise ValueError(f"Invalid player id{self.id}")

    def is_winning(self) -> bool:
        """
        Check if the player has won the game.
        :return: Wether or not the player is on one of their winning position
        :rtype:
        """
        return self.position in self.goal_line
