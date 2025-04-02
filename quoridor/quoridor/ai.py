"""
AI Module contains a list of functions that takes a GameState and returns a move.
The utility functions that they use could be moved elsewhere in the future.
"""

from quoridor.graph import Graph
from quoridor.command import Command, PlaceWallCommand, MovePawnCommand
from quoridor.direction import Direction

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable

from quoridor.exceptions import PathNotFoundError


if TYPE_CHECKING:
    from quoridor.gamestate import GameState


class AI(ABC):
    """
    Abstract base class for AI classes.
    """

    def __init__(self, depth: int):
        self.depth = depth

    @abstractmethod
    def suggest_move(
        self, state: "GameState", heuristic: Callable[["GameState"], int]
    ) -> Command:
        """
        Suggest a move.
        :param state: The current game state
        :return: A command to execute
        """
        pass

    def possible_moves(self, state: "GameState") -> list[tuple[int, int]]:
        pos = state.players[state.current_player.id].position
        return list(state.temp_board()._graph[pos])

    def possible_walls(self, state: "GameState") -> list[tuple[int, int, Direction]]:
        walls = []
        for x in range(state.size - 1):
            for y in range(state.size - 1):
                for direction in [Direction.H, Direction.V]:
                    try:
                        temp_state = state.copy_state()
                        if temp_state.current_player.walls_remaining == 0:
                            continue
                        if not temp_state.wall_exist(x, y, direction.inverse()):
                            if direction == Direction.H:
                                temp_state.board.remove_edge((x, y), (x + 1, y))
                                temp_state.board.remove_edge((x, y + 1), (x + 1, y + 1))
                            elif direction == Direction.V:
                                temp_state.board.remove_edge((x, y), (x, y + 1))
                                temp_state.board.remove_edge((x + 1, y), (x + 1, y + 1))
                            for player in temp_state.players:
                                temp_state.board.a_star(
                                    player.position, player.goal_line[0]
                                )
                            walls.append((x, y, direction))
                    except:
                        continue
        return walls

    def minimax(self, state: "GameState", depth: int, maximizing: bool) -> int:
        if depth <= 0 or state.game_over():
            return self.evaluate(state)

        moves = self.possible_moves(state)
        walls = self.possible_walls(state)

        if maximizing:
            max_eval = float("-inf")
            for move in moves:
                new_state = state.copy_state()
                new_state.current_player.position = move
                new_state.switch_player()
                eval = self.minimax(new_state, depth - 1, False)
                max_eval = max(max_eval, eval)

            print(walls)
            for x, y, direction in walls:
                try:
                    new_state = state.copy_state()
                    if direction == Direction.H:
                        new_state.board.remove_edge((x, y), (x + 1, y))
                        new_state.board.remove_edge((x, y + 1), (x + 1, y + 1))
                    elif direction == Direction.V:
                        new_state.board.remove_edge((x, y), (x, y + 1))
                        new_state.board.remove_edge((x + 1, y), (x + 1, y + 1))
                    new_state.current_player.walls_remaining -= 1
                    new_state.switch_player()
                    eval = self.minimax(new_state, depth - 1, False)
                    max_eval = max(max_eval, eval)
                except:
                    continue
            return max_eval
        else:
            min_eval = float("inf")
            for move in moves:
                new_state = state.copy_state()
                new_state.current_player.position = move
                new_state.switch_player()
                eval = self.minimax(new_state, depth - 1, True)
                min_eval = min(min_eval, eval)

            for x, y, direction in walls:
                try:
                    new_state = state.copy_state()
                    if direction == Direction.H:
                        new_state.board.remove_edge((x, y), (x + 1, y))
                        new_state.board.remove_edge((x, y + 1), (x + 1, y + 1))
                    elif direction == Direction.V:
                        new_state.board.remove_edge((x, y), (x, y + 1))
                        new_state.board.remove_edge((x + 1, y), (x + 1, y + 1))
                    new_state.current_player.walls_remaining -= 1
                    new_state.switch_player()
                    eval = self.minimax(new_state, depth - 1, True)
                    min_eval = min(min_eval, eval)
                except:
                    continue
            return min_eval


class GreedyAI(AI):
    """
    Returns a pawn move that has the shortest path to a winning position.
    """

    def suggest_move(
        self, state: "GameState", heuristic: Callable[["GameState"], int]
    ) -> MovePawnCommand:
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


class EasyAI(AI):
    """
    Returns a pawn move that has the shortest path to a winning position.
    """

    def suggest_move(
        self, state: "GameState", heuristic: Callable[["GameState"], int]
    ) -> MovePawnCommand:
        """
        :param state: The current game state
        :return: A MovePawnCommand.
        """
        self.evaluate = heuristic
        return self.best_action_minimax(state)

    def best_action_minimax(self, state: "GameState") -> Command:
        player = state.players[state.current_player.id]
        current_pos = player.position
        best_val = float("-inf")
        best_action = None

        for move in self.possible_moves(state):
            new_state = state.copy_state()
            new_state.players[state.current_player.id].position = move
            new_state.switch_player()
            val = self.minimax(new_state, self.depth - 1, False)
            if val > best_val:
                best_val = val
                best_action = MovePawnCommand(state, current_pos, move)

        for x, y, direction in self.possible_walls(state):
            try:
                new_state = state.copy_state()
                if direction == Direction.H:
                    new_state.board.remove_edge((x, y), (x + 1, y))
                    new_state.board.remove_edge((x, y + 1), (x + 1, y + 1))
                elif direction == Direction.V:
                    new_state.board.remove_edge((x, y), (x, y + 1))
                    new_state.board.remove_edge((x + 1, y), (x + 1, y + 1))
                new_state.current_player.walls_remaining -= 1
                new_state.switch_player()
                val = self.minimax(new_state, self.depth - 1, False)
                if val > best_val:
                    best_val = val
                    best_action = PlaceWallCommand(state, (x, y), direction)
            except:
                continue

        return best_action


def heuristic(state: "GameState") -> int:
    me = state.current_player
    id_next_opn = state.current_player.id + 1 % state.num_players
    opn = state.players[id_next_opn]
    try:
        my_path = state.board.a_star(me.position, me.goal_line[0])
        adv_path = state.board.a_star(opn.position, opn.goal_line[0])
        return len(adv_path) - len(my_path)
    except PathNotFoundError:
        return -9999
