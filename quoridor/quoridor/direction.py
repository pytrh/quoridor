from enum import Enum


class Direction(Enum):
    """
    Represent the two direction on which a wall can be placed
    'H'orizontal and 'V'ertical
    """

    H = 0
    V = 1

    def inverse(self):
        """
        Return the opposition direction of the current one
        :return: Direction.H if used on Direction.V and vice-versa
        :rtype: Direction
        """
        return Direction.H if self == Direction.V else Direction.V
