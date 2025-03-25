class Player:
    """
    IMPORTANT: Blitz time is interpreted as the traditional sense ie total time for the game.
    Different from E Fleury's requirements. Will justify in the report.
    Player class to represent a player in the game.
    """
    def __init__(self, id: int, position: tuple[int, int], size: int, walls_remaining: int = 10,
                  time_remaining_blitz: int = None) -> None:
        """
        Initialize a new player.

        :param id: The id of the player either 1 or 2 or 3 or 4.
        :type id: int
        :param position: The position of the player represented as a tuple of two integers.
        :type position: tuple[int, int]
        :param walls: The number of walls the player has, default is 10.
        :type walls: int
        :param time_remaining_blitz: The time remaining in seconds for the player in blitz mode, default is None.
        :type time_remaining_blitz: int
        """
        self.id = id
        self.position = position
        self.walls_remaining = walls_remaining
        self.time_remaining_blitz = time_remaining_blitz
        self.start_position = position

        if self.start_position[1] == 0:
            self.goal_line = [(i, size - 1) for i in range(size)]
        elif self.start_position[1] == size - 1:
            self.goal_line = [(i, 0) for i in range(size)]
        elif self.start_position[0] == 0:
            self.goal_line = [(size - 1, i) for i in range(size)]
        elif self.start_position[0] == size - 1:
            self.goal_line = [(0, i) for i in range(size)]

    def is_winning(self) -> bool:
        """
        Check if the player has won the game.
        """
        return self.position in self.goal_line
