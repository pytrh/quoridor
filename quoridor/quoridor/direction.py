from enum import Enum


class Direction(Enum):
    H = 0
    V = 1

    def inverse(self):
        return Direction.H if self == Direction.V else Direction.V
