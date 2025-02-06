class GameState:
    def __init__(self, num_players=2, board_size=9, num_walls=20, blitz_time=None):

        self.num_players = num_players
        self.current_player = 1  
        self.board_size = board_size
        self.num_walls = {i: num_walls for i in range(1, num_players + 1)}
        self.board = self._initialize_board()
        self.history = []  
        self.time_left = {i: blitz_time * 60 for i in range(1, num_players + 1)} if blitz_time else None

    def _initialize_board(self):

        board = [["_" for _ in range(self.board_size)] for _ in range(self.board_size)]
        middle = self.board_size // 2
        if self.num_players == 2:
            board[0][middle] = "1" 
            board[-1][middle] = "2"

        if self.num_players == 3:
            board[0][middle] = "1" 
            board[-1][middle] = "2"
            board[middle][0] = "3"

        if self.num_players == 4:
            board[0][middle] = "1" 
            board[-1][middle] = "2"
            board[middle][0] = "3"
            board[middle][-1] = "4"

        return board

    def make_move(self, player, move):
        self.history.append((player, move))  # Ajout à l'historique
        # TODO: Appliquer le coup au plateau

        # Passer au joueur suivant
        self.current_player = (self.current_player % self.num_players) + 1

    def print_board(self):
       return



