from quoridor.gamestate import GameState


def total_heuristic(state: GameState) -> int:
    return (
        0.5 * aggressive_blocking_heuristic(state)
        + 0.4 * runner_heuristic(state)
        + 0.1 * central_control_heuristic(state)
    )


# def heuristic(state: GameState) -> int:
#     """Heuristic based on the shortest path to the goal for both players."""
#     graph = state.temp_board()

#     player = state.players[(state.current_player.id - 1) % state.num_players]
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

#     return  score


def runner_heuristic(state: GameState) -> float:
    """Runner heuristic: focus entirely on reaching goal quickly."""
    graph = state.temp_board()
    player = state.players[(state.current_player.id - 1) % state.num_players]

    min_path = float("inf")
    for goal in player.goal_line:
        path = graph.a_star(player.position, goal)
        if path:
            min_path = min(min_path, len(path))

    if min_path == float("inf"):
        return float("-inf")
    if state.game_over():
        min_path -= 100000000000

    return -min_path  # Lower path length = better


def central_control_heuristic(state: GameState) -> float:
    """Heuristic that rewards central control and short goal distance."""
    graph = state.temp_board()
    board_center = (state.size // 2, state.size // 2)

    def dist(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    player = state.players[(state.current_player.id - 1) % state.num_players]
    opponent = state.players[(state.current_player.id) % state.num_players]

    def shortest_path_length(p):
        best = state.size**2
        for goal in p.goal_line:
            path = graph.a_star(p.position, goal)
            if path:
                best = min(best, len(path))
        return best

    player_path = shortest_path_length(player)
    opponent_path = shortest_path_length(opponent)

    player_center_dist = dist(player.position, board_center)
    return (opponent_path - player_path) - 0.3 * player_center_dist


def aggressive_blocking_heuristic(state: GameState) -> float:
    """Aggressive heuristic: focus on blocking opponent more than advancing self."""
    graph = state.temp_board()
    player = state.players[(state.current_player.id - 1) % state.num_players]
    opponent = state.players[(state.current_player.id) % state.num_players]

    def shortest_path_length(p):
        best = float("inf")
        for goal in p.goal_line:
            path = graph.a_star(p.position, goal)
            if path:
                best = min(best, len(path))
        return best

    player_path = shortest_path_length(player)
    opponent_path = shortest_path_length(opponent)

    if player_path == float("inf"):
        return float("-inf")
    if opponent_path == float("inf"):
        return float("inf")

    return 2 * opponent_path - player_path
