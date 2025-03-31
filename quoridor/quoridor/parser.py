import logging

from quoridor.cliengine import CLIEngine
from quoridor.direction import Direction
from quoridor.gamestate import GameState
from quoridor.graph import Graph
from quoridor.command import PlaceWallCommand
from quoridor.player import Player


def parse_string_to_graph(board_string: str) -> Graph:
    graph = Graph()

    lines = board_string.splitlines()
    lines = lines[2:-1]

    size = len(lines) // 2 + 1
    for i in range(size):
        for j in range(size):
            graph.add_node((i, j))
    for i in range(size):
        for j in range(size):
            if i < size - 1:
                graph.add_edge((i, j), (i + 1, j))
            if j < size - 1:
                graph.add_edge((i, j), (i, j + 1))

    row = 0
    for line in lines:
        start = 0
        inline = 5
        col = 0
        # line number even
        if row % 2 == 0:
            for char in line:
                if start < 6:
                    start += 1
                elif inline < 3:
                    inline += 1
                else:
                    real_row = row // 2
                    if char == "|" and col < size - 1:
                        graph.remove_edge((real_row, col), (real_row, col + 1))
                    col += 1
                    inline = 0
        # line number odd
        elif row % 2 == 1:
            for char in line:
                if start < 4:
                    start += 1
                elif inline < 3:
                    inline += 1
                else:
                    real_row = row // 2
                    if char == "-":
                        graph.remove_edge((real_row, col), (real_row + 1, col))
                    col += 1
                    inline = 0
        row += 1

    return graph


def _print_graph(graph: Graph):
    if not graph._graph:
        print("Graph is empty.")
        return
    max_x = max(node[0] for node in graph._graph)
    max_y = max(node[1] for node in graph._graph)

    for row in range(max_x + 1):
        node_line = ""
        edge_line = ""
        for col in range(max_y + 1):
            if (row, col) in graph._graph:
                node_line += " O "
                if (row, col + 1) in graph._graph and (row, col + 1) in graph._graph[
                    (row, col)
                ]:
                    node_line += "-"
                elif col < max_y:
                    node_line += "V"
            else:
                node_line += "   "
        print(node_line)
        if row < max_x:
            edge_line = ""
            for col in range(max_y + 1):
                if (
                    (row, col) in graph._graph
                    and (row + 1, col) in graph._graph
                    and (row + 1, col) in graph._graph[(row, col)]
                ):
                    edge_line += " |  "
                else:
                    edge_line += " H  "
            print(edge_line)


def _test_parse_string_to_graph():
    state = GameState(size=5)
    place1 = PlaceWallCommand(state, (2, 2), Direction.V)
    place2 = PlaceWallCommand(state, (1, 1), Direction.V)
    place3 = PlaceWallCommand(state, (1, 0), Direction.H)

    cli = CLIEngine(state)
    cli.execute_command(place1)
    cli.execute_command(place2)
    cli.execute_command(place3)
    string_board = cli.get_string_from_board()
    print(string_board)

    print("")
    graph = parse_string_to_graph(string_board)
    _print_graph(graph)


def parse_string_to_state(state_string: str) -> GameState:
    size = None
    current_player_id = None
    players = None
    num_players = None
    board = None
    blitz = None
    num_walls = None
    history = None

    # player info
    player_data = {}

    state_lines = [
        line for line in state_string if not line.startswith("#") and line.strip()
    ]
    if state_lines == []:
        logging.debug("Input file path is empty.")

    i = 0
    while i < len(state_lines):
        line = state_lines[i]

        if line.startswith("num_players"):
            num_players = int(line.split("=")[1].strip())
        elif line.startswith("current_player_id"):
            current_player_id = int(line.split("=")[1].strip())
        elif line.startswith("board_size"):
            size = int(line.split("=")[1].strip())
        elif line.startswith("num_walls"):
            num_walls = int(line.split("=")[1].strip())
        elif line.startswith("blitz"):
            t_blitz = line.split("=")[1].strip()
            if t_blitz == "False" or t_blitz == "F":
                blitz = False
            else:
                blitz = bool(line.split("=")[1].strip())
        elif line.startswith("players"):
            players = []
            i += 1
            while i < len(state_lines) and state_lines[i].startswith("player_"):
                key, value = state_lines[i].split("=")
                key, value = key.strip(), value.strip()

                if key == "player_id":
                    player_id = int(value)
                    players.append(
                        Player(
                            id=player_id,
                            position=player_data.get("position", (0, 0)),
                            size=size,
                            walls_remaining=player_data.get("walls", 0),
                        )
                    )
                    player_data = {}
                elif key == "player_position":
                    player_data["position"] = tuple(map(int, value.split(",")))
                elif key == "player_walls":
                    player_data["walls"] = int(value)

                i += 1
            continue
        elif line.startswith("board"):
            if size is not None:
                board_string = "".join(state_lines[i + 1 : i + 3 + (size * 2)])
                board = parse_string_to_graph(board_string)
                i += size * 2
            else:
                logging.warning("Impossible to parse board before initializing size")
        elif line.startswith("history"):
            history_string = "".join(state_lines[i + 1 :])
            # history = parse_list_of_str_to_history(history_string) # TODO : mohamad
            break
        i += 1

    # TODO check error after parsing
    # example num_players should match players[] length

    kwargs = {
        "size": size,
        "current_player_id": current_player_id,
        "players": players,
        "num_players": num_players,
        "board": board,
        "blitz": blitz,
        "num_walls": num_walls,
        "history": history,
    }
    filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
    return GameState(**filtered_kwargs)


def _print_state(state: GameState):
    print("--- State ---")
    print(f"Board size : {state.size}")
    print(f"Current player id : {state.current_player.id}")
    print(f"Number of players : {state.num_players}")
    print(f"Blitz mode : {state.blitz}")
    print(f"Number of walls per players : {state.initial_num_walls}")

    # Players
    print("- Players -")
    for player in state.players:
        print(f"Id : {player.id}")
        print(f"Position : {player.position}")
        print(f"Walls remaining : {player.walls_remaining}")

    # Board
    _print_graph(state.board)

    # History


def _test_parse_string_to_state():
    input_file_path = "quoridor/state.txt"
    try:
        # open file
        with open(input_file_path, "r", encoding="utf-8") as input_file:
            state = parse_string_to_state(input_file)
            _print_state(state)

    except FileNotFoundError:
        print(f"Error: The file '{input_file_path}' was not found.")
        return []


if __name__ == "__main__":
    _test_parse_string_to_state()
