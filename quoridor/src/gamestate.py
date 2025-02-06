"""
GameState class to represent the game state
"""

from graph import Graph

class GameState:
    def __init__(self, size: int, player_count: int):
        self.board = self.create_board(size)
        self.players = []
        self.current_player = None

    def add_player(self, player):
        self.players.append(player)

    def create_board(self, size: int):
        board = Graph()
        for i in range(size):
            for j in range(size):
                board.add_node((i, j))
        for i in range(size):
            for j in range(size):
                if i < size - 1:
                    board.add_edge((i, j), (i + 1, j))
                if j < size - 1:
                    board.add_edge((i, j), (i, j + 1))
        return board

    def print_board(self):
        columns = "    " + "   ".join(str(i) for i in range(self.size))
        separator = "  +" + "---+" * self.size
        rows = "abcdefghi"

        print(columns)
        for row in rows:
            print(separator)
            print(f"{row} |" + "   |" * self.size)
        print(separator)
