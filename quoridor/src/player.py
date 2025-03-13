class Player:
    """
    Player class to represent a player in the game.
    """

    def __init__(
        self,
        id: int,
        position: tuple[int, int],
        fences_remaining: int = 10,
        time_remaining: int = None,
        size: int = 9,
    ) -> None:
        """
        Initialize a new player.

        :param id: The id of the player either 1 or 2 or 3 or 4.
        :type id: int
        :param position: The position of the player represented as a tuple of two integers.
        :type position: tuple[int, int]
        :param fences: The number of fences the player has, default is 10.
        :type fences: int
        :param time_remaining: The time remaining in seconds for the player in blitz mode, default is None.
        :type time_remaining: int
        """
        self.id = id
        self.position = position
        self.fences_remaining = fences_remaining
        self.time_remaining = time_remaining
        self.winning_position = self.__list_winning_position(size)

    def __list_winning_position(self, size: int) -> list[(int, int)]:
        """
        Create a list of winning position for the player using the size of the board
        :param size: size of the board
        :type size: int
        :return: list of winning position
        :rtype: list(int, int)]
        """
        list = []
        posX_win = 0
        posY_win = 0
        if self.id == 1:
            posX_win = size - 1
        if self.id in (0, 1):
            for i in range(size):
                list.append((posX_win, i))
            return list

        if self.id == 3:
            posY_win = size - 1
        if self.id in (2, 3):
            for i in range(size):
                list.append((i, posY_win))
            return list
        return list
