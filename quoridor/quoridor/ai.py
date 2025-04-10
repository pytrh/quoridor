"""
AI Module contains a list of functions that takes a GameState and returns a move.
The utility functions that they use could be moved elsewhere in the future.
"""

from quoridor.command import Command, PassCommand, PlaceWallCommand, MovePawnCommand
from quoridor.direction import Direction

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable


if TYPE_CHECKING:
    from quoridor.gamestate import GameState


class AI(ABC):
    """
    Abstract base class for AI classes.
    """

    def __init__(self, depth: int, heuristic: Callable[["GameState"], int]):
        self.depth = depth
        self.heuristic = heuristic

    @abstractmethod
    def suggest_move(self, state: "GameState") -> Command:
        """
        Suggest a move.
        :param state: The current game state
        :return: A command to execute
        """
        pass

    def possible_moves(self, state: "GameState") -> list[tuple[int, int]]:
        return state.possible_moves(state.current_player.id)

    def possible_walls(self, state: "GameState") -> list[tuple[int, int, Direction]]:
        return state.possible_walls(state.current_player.id)


class GreedyAI(AI):
    """
    Returns a pawn move that has the shortest path to a winning position.
    """

    def suggest_move(self, state: "GameState") -> MovePawnCommand:
        """
        :param state: The current game state
        :return: A MovePawnCommand.
        """
        player = state.players[state.current_player.id]
        graph = state.temp_board()

        current_pos = player.position
        best_path = None
        for goal in player.goal_line:
            path = graph.a_star(current_pos, goal)
            if best_path is None or len(path) < len(best_path):
                best_path = path
        return MovePawnCommand(state, current_pos, best_path[1])


class MinimaxAI(AI):
    """
    AI using Minimax algorithm to select the best move.
    """

    def suggest_move(self, state: "GameState") -> Command:
        _, best_move = self._minimax(state, self.depth, True)
        if best_move:
            best_move.state = state
            return best_move
        else:
            moves = self.possible_moves(state)
            if moves:
                command = MovePawnCommand(
                    state, state.current_player.position, moves[0]
                )
                return command

    def _minimax(
        self,
        tmp_state: "GameState",
        depth: int,
        maximizing: bool,
    ):
        state = tmp_state.copy_state_ai()
        if depth == 0 or state.game_over():
            return self.heuristic(state), None

        best_move = None

        best_eval = float("-inf") if maximizing else float("inf")

        commands = [
                MovePawnCommand(state, state.current_player.position, pos) for pos in self.possible_moves(state)
            ] + [
                PlaceWallCommand(state, (x, y), d) for x, y, d in self.possible_walls(state)
                ]

        for command in commands:
            try:
                # execute_command(command)
                command.execute()
                state.switch_player()

                eval, _ = self._minimax(state, depth - 1, False)
                
                command.undo()

                if (maximizing and eval > best_eval) or (not maximizing and eval < best_eval):
                    best_eval = eval
                    best_move = command
                
            except Exception:
                command.undo()
                continue

        return best_eval, best_move


class AlphaBetaAI(AI):
    """
    AI using Minimax algorithm to select the best move.
    """

    def suggest_move(self, state: "GameState") -> Command:
        _, best_move = self._minimax(state, self.depth, True)
        if best_move:
            best_move.state = state
            return best_move
        else:
            moves = self.possible_moves(state)
            if moves:
                command = MovePawnCommand(
                    state, state.current_player.position, moves[0]
                )
                return command

    def _minimax(
        self,
        tmp_state: "GameState",
        depth: int,
        maximizing: bool,
        alpha: float = float("-inf"),
        beta: float = float("inf"),
    ):
        state = tmp_state.copy_state_ai()
        if depth == 0 or state.game_over():
            return self.heuristic(state), None

        best_move = None

        best_eval = float("-inf") if maximizing else float("inf")

        commands = [
                MovePawnCommand(state, state.current_player.position, pos) for pos in self.possible_moves(state)
            ] + [
                PlaceWallCommand(state, (x, y), d) for x, y, d in self.possible_walls(state)
                ]

        for command in commands:
            try:
                command.execute()
                state.switch_player()

                eval, _ = self._minimax(state, depth - 1, False, alpha, beta)

                command.undo()

                if (maximizing and eval > best_eval) or (not maximizing and eval < best_eval):
                    best_eval = eval
                    best_move = command

                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cut-off
            except Exception:
                command.undo()
                continue

        return best_eval, best_move
