from enum import Enum


class GameMode(Enum):
    NORMAL = "Normal : no timer"
    TIMER_INCR = "Timer : time for each turn"
    BLITZ = "Blitz : total time for entire game"
    AI = "AI : one or more player are AI"

    def __init__(self, display_name: str):
        self.display_name = display_name
