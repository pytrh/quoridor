from enum import Enum


class GameMode(Enum):
    NORMAL = "normal"
    BLITZ = "blitz"

    def __init__(self, display_name: str):
        self.display_name = display_name
