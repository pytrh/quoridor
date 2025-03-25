from quoridor.cliengine import CLIEngine
from quoridor.direction import Direction
from quoridor.gamestate import GameState
from quoridor.graph import Graph
from quoridor.command import PlaceWallCommand


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


def test_parse_string_to_graph():
    state = GameState(size=5)
    place1 = PlaceWallCommand(state, (2, 2), Direction.V)
    place2 = PlaceWallCommand(state, (1, 1), Direction.V)
    place3 = PlaceWallCommand(state, (1, 0), Direction.H)

    cli = CLIEngine(state)
    cli.execute_command(place1)
    cli.execute_command(place2)
    cli.execute_command(place3)
    string_board = cli.get_board_to_string()
    print(string_board)

    print("")
    graph = parse_string_to_graph(string_board)
    _print_graph(graph)


if __name__ == "__main__":
    test_parse_string_to_graph()
