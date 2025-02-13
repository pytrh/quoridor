import time
from graph import Graph

class GameState:

    
    def __init__(self, size, num_players, blitz_time, num_walls ):
        self.size = size
        self.num_players = num_players
        self.current_player = 1
        self.time_remaining = {i: blitz_time * 60 for i in range(1, num_players + 1)} if blitz_time==0 else None
        self.board = self._init_board()
        self.history = []
        self.players_walls_num = { num_walls for _ in range(num_players)}
        

        
        
        
    def _init_board(self):
        board_graph = Graph()
        for x in range(self.size):
            for y in range(self.size):
                node = (x, y)
                board_graph.add_node(node)
                if x > 0: board_graph.add_edge(node, (x-1, y))  # Nord
                if x < self.size - 1: board_graph.add_edge(node, (x+1, y))  # Sud
                if y > 0: board_graph.add_edge(node, (x, y-1))  # Ouest
                if y < self.size - 1: board_graph.add_edge(node, (x, y+1))  # Est
        return board_graph

    def switch_player(self):
        self.current_player = (self.current_player % self.num_players) + 1

    

    def switch_time(self):
        pass

    def update_wall(self):
        self.players_walls_num[self.current_player-1] = self.players_walls_num[self.current_player-1] -1

    def record_move(self, move):
        self.history.append(move)
        
    def place_wall(self, x, y, direction):
        if direction == 'H' and self.players_walls_num[self.current_player-1] > 0:  # Mur horizontal
            if self.board.edge_exists((x, y), (x+1, y)) :
                self.board.remove_edge((x, y), (x+1, y))

            if self.board.edge_exists((x, y+1), (x+1, y+1)) :
                self.board.remove_edge((x, y+1), (x+1, y+1))
            self.update_wall(self)
            
        elif direction == 'V' and self.players_walls_num[self.current_player-1] > 0:  # Mur vertical
            if self.board.edge_exists((x, y), (x, y+1)):
                self.board.remove_edge((x, y), (x, y+1))

            if self.board.edge_exists((x+1, y), (x+1, y+1)):
                self.board.remove_edge((x+1, y), (x+1, y+1))
            self.update_wall(self)

    def display_board(self):
        pass


    def start_Game(self, size, num_players, blitz_time, walls_num ):
        self.set_size(self, size, num_players, blitz_time, walls_num )
        

    def load_game_from_file(self):
        pass
        

    
