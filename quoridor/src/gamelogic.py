"""
GameLogic module.
"""
import copy
from src.gamestate import GameState
from src.graph import Graph
from src.exceptions import InvalidMoveError

class GameLogic:
    def __init__(self, gamestate: GameState):
        self.state = gamestate

    def switch_player(self):
        self.state.current_player = (self.state.current_player + 1) % self.state.num_players

    def update_wall(self):
        self.state.players[self.state.current_player].fences_remaining = self.state.players[self.state.current_player].fences_remaining-1

    def temp_board(self) -> Graph:
        board = copy.deepcopy(self.state.board)
        p=[(),(),(),()]
        for i in range(self.state.num_players):
            p[i] = self.state.players[i].position
        directions = [(1,0), (-1,0), (0,1), (0,-1)]

        
        x, y = p[self.state.current_player]
        for dx, dy in directions:
            adj = (x+dx, y+dy)
            jump = (x+2*dx, y+2*dy)
            
            if adj in p and board.edge_exists((x,y),adj):
                board.remove_edge((x,y),adj)
                
                if(board.node_exists(jump) and board.edge_exists(adj,jump)):
                    board.add_edge((x,y), jump)
                else:
                    side_directions = [(dy,dx), (-dy,-dx)]
                    
                    for pdx, pdy in side_directions:
                        side_jump = (x+dx+pdx, y+dy+pdy)
                        if board.edge_exists(side_jump, adj):
                            board.add_edge((x,y), side_jump)

        return board
        

    def make_move(self, start: tuple[int, int], end: tuple[int, int]):
        if(not (self.state.players[self.state.current_player].position[0] == start[0] and self.state.players[self.state.current_player].position[1] == start[1])):
            raise InvalidMoveError
        else:
            board_temp = self.temp_board()
            if(not board_temp.edge_exists(start, end)):
                raise InvalidMoveError
            self.state.players[self.state.current_player].position=end
            self.switch_player()
    
    def place_wall(self, x, y, direction):
        if(self.state.players[self.state.current_player].fences_remaining == 0):
            raise InvalidMoveError
        if direction == 'h' and self.state.players[self.state.current_player].fences_remaining > 0:  # Mur horizontal
            if self.state.board.edge_exists((x, y), (x+1, y)) and self.state.board.edge_exists((x, y+1), (x+1, y+1)):
                self.state.board.remove_edge((x, y), (x+1, y))
                self.state.board.remove_edge((x, y+1), (x+1, y+1))
            else:
                raise InvalidMoveError
            
        elif direction == 'v' and self.state.players[self.state.current_player].fences_remaining > 0:  # Mur vertical
            if self.state.board.edge_exists((x, y), (x, y+1)) and self.state.board.edge_exists((x+1, y), (x+1, y+1)):
                self.state.board.remove_edge((x, y), (x, y+1))
                self.state.board.remove_edge((x+1, y), (x+1, y+1))
            else:
                raise InvalidMoveError
        self.update_wall()
        self.switch_player()

