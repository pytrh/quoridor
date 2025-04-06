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
        return state.possible_moves(state.current_player.id)

    def possible_walls(self, state: "GameState") -> list[tuple[int, int, Direction]]:
        return state.possible_walls(state.current_player.id)

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

class MinimaxAI(AI):
    """
    AI using Minimax algorithm to select the best move.
    """

    def suggest_move(
        self, state: "GameState", heuristic: Callable[["GameState"], int]
    ) -> Command:
        _, best_move = self._minimax(state, self.depth, True, heuristic)
        if best_move:
            best_move.state = state
            return best_move

    def _minimax(self, state: "GameState", depth: int, maximizing: bool, heuristic: Callable[["GameState"], int]):
        from quoridor.cliengine import CLIEngine

        if depth == 0 or state.game_over():
            return heuristic(state), None  

        best_move = None
        if maximizing:
            max_eval = float('-inf')
            for pos in self.possible_moves(state):
                command = MovePawnCommand(state, state.current_player.position, pos)
                try:
                    # execute_command(command)
                    command.execute()
                    state.history.append((state.current_player.id, command))
                    state.redo_stack.clear()
                    state.switch_player()

                    eval, _ = self._minimax(state, depth - 1, False, heuristic)
                    command.undo()
                    if eval > max_eval:
                        max_eval = eval
                        best_move = command
                except Exception:
                    command.undo()
                    continue
            
            for (x, y, d) in self.possible_walls(state):
                command = PlaceWallCommand(state, (x, y), d)
                try:
                    # execute_command(command)
                    command.execute()
                    state.history.append((state.current_player.id, command))
                    state.redo_stack.clear()
                    state.switch_player()
                    
                    eval,_ = self._minimax(state, depth - 1, False, heuristic)
                    command.undo()
                    if eval > max_eval:
                        max_eval = eval
                        best_move = command
                except Exception:
                    command.undo()
                    continue

            return max_eval, best_move

        else:  # Minimizing player
            min_eval = float('inf')
            for new_x, new_y in self.possible_moves(state):
                command = MovePawnCommand(state, state.current_player.position, (new_x, new_y))
                try:
                    command.execute()
                    state.history.append((state.current_player.id, command))
                    state.redo_stack.clear()
                    state.switch_player()

                    eval, _ = self._minimax(state, depth - 1, True, heuristic)
                    command.undo()

                    if eval < min_eval:
                        min_eval = eval
                        best_move = command
                except Exception:
                    command.undo()
                    continue

            for (x, y, d) in self.possible_walls(state):
                command = PlaceWallCommand(state, (x, y), d)
                try:
                    command.execute()
                    state.history.append((state.current_player.id, command))
                    state.redo_stack.clear()
                    state.switch_player()

                    eval,_ = self._minimax(state, depth - 1, True, heuristic)
                    if eval < min_eval:
                        min_eval = eval
                        best_move = command
                    command.undo()
                except Exception:
                    command.undo()
                    continue
            return min_eval, best_move




# def heuristic(state: "GameState") -> int:
#     """Heuristic based on the shortest path to the goal for both players."""
#     graph = state.temp_board()
    
#     player = state.players[(state.current_player.id + 1) % state.num_players]
#     current_pos = player.position

#     best_path_for_player = None
#     for goal in player.goal_line:
#         path = graph.a_star(current_pos, goal)
#         if best_path_for_player is None or len(path) < len(best_path_for_player):
#             best_path_for_player = path

#     opponent = state.players[(state.current_player.id)% state.num_players ] 
#     current_pos = opponent.position

#     best_path_for_opponent = None
#     for goal in opponent.goal_line:
#         path = graph.a_star(current_pos, goal)
#         if best_path_for_opponent is None or len(path) < len(best_path_for_opponent):
#             best_path_for_opponent = path
#     score = len(best_path_for_opponent) - len(best_path_for_player) 
#     # if state.game_over():
#     #     score +=100 
#     return  score

def heuristic(state: "GameState") -> int:
    return 0.5 * aggressive_blocking_heuristic(state) + 0.3 * runner_heuristic(state) + 0.2 * central_control_heuristic(state)
   


def runner_heuristic(state: "GameState") -> float:
    """Runner heuristic: focus entirely on reaching goal quickly."""
    graph = state.temp_board()
    player = state.players[(state.current_player.id -1) %  state.num_players]

    min_path = float('inf')
    for goal in player.goal_line:
        path = graph.a_star(player.position, goal)
        if path:
            min_path = min(min_path, len(path))

    if min_path == float('inf'):
        return float('-inf')
    # if state.game_over():
    #     min_path +=100
    #     print(min_path)

    return -min_path  # Lower path length = better


def central_control_heuristic(state: "GameState") -> float:
    """Heuristic that rewards central control and short goal distance."""
    graph = state.temp_board()
    board_center = (state.size//2, state.size//2)

    def dist(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    player = state.players[(state.current_player.id - 1 ) % state.num_players]
    opponent = state.players[(state.current_player.id) % state.num_players]

    def shortest_path_length(p):
        best = float('inf')
        for goal in p.goal_line:
            path = graph.a_star(p.position, goal)
            if path:
                best = min(best, len(path))
        return best

    player_path = shortest_path_length(player)
    opponent_path = shortest_path_length(opponent)

    player_center_dist = dist(player.position, board_center)

    return (opponent_path - player_path) - 0.3 * player_center_dist


def aggressive_blocking_heuristic(state: "GameState") -> float:
    """Aggressive heuristic: focus on blocking opponent more than advancing self."""
    graph = state.temp_board()
    player = state.players[(state.current_player.id - 1) % state.num_players]
    opponent = state.players[(state.current_player.id) % state.num_players]

    def shortest_path_length(p):
        best = float('inf')
        for goal in p.goal_line:
            path = graph.a_star(p.position, goal)
            if path:
                best = min(best, len(path))
        return best

    player_path = shortest_path_length(player)
    opponent_path = shortest_path_length(opponent)

    if player_path == float('inf'):
        return float('-inf')
    if opponent_path == float('inf'):
        return float('inf')

    return 2 * opponent_path - player_path

