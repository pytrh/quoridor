"""
Parser module
"""

import logging

from quoridor.gamestate import GameState
from quoridor.graph import Graph
from quoridor.player import Player
from quoridor.gamemode import GameMode
from quoridor.io import ReadWriteHistory


def parse_string_to_graph(board_string: str) -> Graph:
    """
    Parse a string representation into a Graph object

    :param board_string: The text that can be translated into a graph
    :type board_string: str
    :return: A graph that represent an ongoing game
    :rtype: Graph
    """
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


def parse_string_to_state(state_string: str) -> GameState:
    """
    Parse a string representation into a GameState object

    :param state_string: The text that can be translated into the state of a game
    :type state_string: str
    :return: A state that represent an ongoing game
    :rtype: GameState
    """
    from quoridor.io import ReadWriteHistory

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
    history_to_string = None

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
        elif line.startswith("game_mode"):
            g_mode = line.split("=")[1].strip()
            if g_mode == "GameMode.BLITZ":
                game_mode = GameMode.BLITZ
            else:
                game_mode = GameMode.NORMAL
        elif line.startswith("blitz"):
            blitz = int(line.split("=")[1].strip())
        elif line.startswith("players"):
            players = []
            i += 1

            # Loop for each player in the savefile
            while i < len(state_lines) and state_lines[i].startswith("player_"):
                key, value = state_lines[i].split("=")
                key, value = key.strip(), value.strip()

                if key == "player_id":
                    player_id = int(value)
                    if game_mode == GameMode.NORMAL:
                        players.append(
                            Player(
                                id=player_id,
                                position=player_data.get("position", (0, 0)),
                                size=size,
                                walls_remaining=player_data.get("walls", 0),
                            )
                        )
                    else:
                        from quoridor.timer import Timer

                        timer = Timer(blitz, game_mode, player_id)
                        timer.set_time_remaining(
                            player_data.get("timer_time", blitz * 60)
                        )
                        players.append(
                            Player(
                                id=player_id,
                                position=player_data.get("position", (0, 0)),
                                size=size,
                                walls_remaining=player_data.get("walls", 0),
                                time_remaining_blitz=timer,
                            )
                        )
                    player_data = {}
                elif key == "player_position":
                    player_data["position"] = tuple(map(int, value.split(",")))
                elif key == "player_walls":
                    player_data["walls"] = int(value)
                elif key == "player_timer":
                    player_data["timer_time"] = int(value)

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
            state_temp = GameState(size=size, num_players=num_players)
            history_to_string = ReadWriteHistory._get_game_info_from_file(
                state_lines[i + 1 :]
            )
            history = ReadWriteHistory.parse_list_of_str_to_history(
                state_temp, history_to_string
            )
            break
        i += 1

    kwargs = {
        "size": size,
        "current_player_id": current_player_id,
        "players": players,
        "num_players": num_players,
        "board": board,
        "num_walls": num_walls,
        "history": history,
        "game_mode": game_mode,
        "blitz_time": blitz,
        # ai_ids ?
    }
    filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
    state = GameState(**filtered_kwargs)
    for pid, cmd in state.history:
        cmd.state = state
    return state


def parse_state_to_string(state: GameState) -> str:
    """
    Parse a GameObject into a string representation

    :param state: A state that represent an ongoing game
    :type state: GameState
    :return: A text that represent the state of a game
    :rtype: str
    """
    state_string = f"num_players = {state.num_players}\n"
    state_string += f"current_player_id = {state.current_player.id}\n"
    state_string += f"board_size = {state.size}\n"
    state_string += f"initial_num_walls = {state.initial_num_walls}\n"
    state_string += f"game_mode = {state.game_mode}\n"
    state_string += f"blitz = {state.blitz_time}\n\n"

    state_string += f"players =\n\n"

    for i in range(state.num_players):
        state_string += f"player_position = {state.players[i].position[0]}, {state.players[i].position[1]}\n"
        state_string += f"player_walls = {state.players[i].walls_remaining}\n"
        if state.game_mode == GameMode.BLITZ:
            state_string += f"player_timer = {state.players[i].timer.current_time}\n"
        state_string += f"player_id = {state.players[i].id}\n\n"

    # Add the board representation
    state_string += f"board =\n"
    state_string += get_string_from_board(state) + "\n"

    state_string += f"history =\n"
    state_string += parse_history_to_str(state.history, state.num_players)
    return state_string


def parse_history_to_str(turns: list[list[str]], num_players: int) -> str:
    """
    Writes the history of game moves to text format.

    :param turns: A list of tuple (int, command) which we use as a list of list of string
    :type turns: list[list[str]
    :param num_players: The number of players of the game
    :type num_players: int
    :return: A text that represent the history of a game
    :rtype: str
    """
    history_string = ""
    turn_nb = 0
    turn_str = ""
    for move_nb, turn in enumerate(turns):
        turn_str += f"{turn[0]+1} {turn[1]} "
        if turn[0] == num_players - 1:
            history_string += f"\n{turn_nb + 1}. {turn_str} "
            turn_nb = turn_nb + 1
            turn_str = ""

    if len(turns) % num_players != 0:
        history_string += f"\n{turn_nb + 1}. {turn_str} "

    history_string += "\n"
    return history_string


def get_string_from_board(state: GameState) -> str:
    """
    Return the board in string format
    :param state: The state of an ongoing game
    :type state: GameState
    :return: A string that represent the board of a game
    :rtype: str
    """
    rows = [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
    ]
    horizontal_wall = "---"
    vertical_wall = "|"
    interstice = "+"
    horizontal_space = "   "  # Must be of the same size than horizontal_wall
    big_space = "  "
    small_space = " "  # Must be of the size of big_space -1
    "  +" + "---+" * state.size

    result = "    " + horizontal_space.join(str(i + 1) for i in range(state.size))
    result += "\n"
    result += big_space + interstice + (horizontal_wall + interstice) * state.size
    for row in range(state.size):
        result += f"\n{rows[row]}" + small_space + vertical_wall
        for columns in range(state.size):
            case = "   "
            for player in range(state.num_players):
                if (
                    state.players[player].position[0] == row
                    and state.players[player].position[1] == columns
                ):
                    # case = " " + str(self.state.players[player].id + 1) + " "
                    case = " " + str(player + 1) + " "
            if columns == state.size - 1 or not state.board.edge_exists(
                (row, columns), (row, columns + 1)
            ):
                result += case + vertical_wall
            else:
                result += case + " "
        result += "\n" + big_space + interstice
        for columns in range(state.size):
            if row == state.size - 1 or not state.board.edge_exists(
                (row, columns), (row + 1, columns)
            ):
                result += horizontal_wall
            else:
                result += horizontal_space
            result += interstice
    return result
