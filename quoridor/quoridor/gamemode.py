from enum import Enum
from typing import Callable


class GameMode(Enum):
    NORMAL = "normal"
    BLITZ = "blitz"

    def __init__(self, display_name: str):
        self.display_name = display_name


class AiMode(Enum):
    GREEDY = "greedy"
    MINIMAX = "minimax"
    ALPHABETA = "ab"

    def __init__(self, display_name: str):
        self.display_name = display_name


class AiHeuristic(Enum):
    DEFAULT = ("default", "total")
    RUNNER = ("runner", "runner")
    AGGRESSIVE = ("aggressive", "aggressive")
    CENTRAL = ("central", "central")

    def __init__(self, display_name: str, _key: str):
        self.display_name = display_name
        self._key = _key

    @property
    def func(self) -> Callable:
        from quoridor.heuristic import (
            total_heuristic,
            runner_heuristic,
            aggressive_blocking_heuristic,
            central_control_heuristic,
        )

        return {
            "total": total_heuristic,
            "runner": runner_heuristic,
            "aggressive": aggressive_blocking_heuristic,
            "central": central_control_heuristic,
        }[self._key]
