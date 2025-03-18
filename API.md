Questions for E Fleury:
What is contest mode?

Tests for gamestatemanager
1. Move pawn out of bound
2. Place wall out of bound
3. Place wall to block opponent's path to goal line
4. Place wall to encircle a border node
5. Place wall to cross/superimpose/ another wall
6. Move pawn to a node with a wall on it
7. Move pawn to a node with an opponent's pawn on it
8. Exceed the number of walls per player
9. Jump over a wall
10. Jump over an opponent's pawn
11. Diagonal jumps
12. Negative cases for diagonal jumps ie blocked with walls or opponent's pawn

## Choice to make
### How to incorporate AI?
Make a AI player class that inherits from Player class?
No, we want something that return a move knowing the current gamestate and that's it.
Actually yes why not?
The AI have to access all the stuff a human player access anyway.
Acutally no because of composition over inheritance.
And we should be able reuse the same let's say MinimaxAI for multiple AI players.
### How to handle multiple players while some of them are AI?
Here's how you can handle a mix of human and AI players in your Quoridor game:

1. **First, create a player type enum**:
```python
from enum import Enum

class PlayerType(Enum):
    HUMAN = "human"
    RANDOM_AI = "random_ai"
    MINIMAX_AI = "minimax_ai"
```

2. **Modify your GameStateManager initialization**:
```python:quoridor/src/gamestatemanager.py
class GameStateManager:
    def __init__(self, player_types: list[PlayerType], renderer=None):
        self.state = GameState()
        self.renderer = renderer
        self.ai_controllers = {}
        
        # Create players and their controllers
        for i, player_type in enumerate(player_types):
            player = Player(id=i, position=self._get_start_position(i))
            self.state.players.append(player)
            
            # Create AI controller if needed
            if player_type == PlayerType.RANDOM_AI:
                self.ai_controllers[i] = RandomAI()
            elif player_type == PlayerType.MINIMAX_AI:
                self.ai_controllers[i] = MinimaxAI()

    def get_move(self) -> str:
        """Get move from current player (human or AI)"""
        current_id = self.state.current_player.id
        
        if current_id in self.ai_controllers:
            # AI move
            return self.ai_controllers[current_id].get_move(self.state)
        else:
            # Human move
            return self.renderer.get_human_move()
```

3. **Simplify your game loop**:
```python:quoridor/src/gamestatemanager.py
def run_game(self):
    """Run the game loop."""
    self.renderer.render_board(self.state)
    
    while True:
        try:
            # Get move from current player (AI or human)
            move = self.get_move()
            
            # Handle commands uniformly
            if move.startswith("quit"):
                return
            elif move.startswith("undo"):
                self.undo()
            elif move.startswith("redo"):
                self.redo()
            else:
                # Regular move (wall or pawn)
                self.make_move(move)
            
            self.renderer.render_board(self.state)
            
            # Check for game over
            if self.state.current_player.is_winning():
                self.renderer.render_game_over()
                return
                
        except InvalidMoveError as e:
            self.renderer.render_error(str(e))
```

4. **Usage example**:
```python
# Example: 2 players, first is human, second is AI
player_types = [PlayerType.HUMAN, PlayerType.MINIMAX_AI]
game = GameStateManager(player_types, renderer=CLIRenderer())
game.run_game()

# Example: 4 players, mix of human and different AIs
player_types = [
    PlayerType.HUMAN,
    PlayerType.RANDOM_AI,
    PlayerType.MINIMAX_AI,
    PlayerType.HUMAN
]
game = GameStateManager(player_types, renderer=CLIRenderer())
game.run_game()
```

Key benefits of this approach:
1. Clean separation between player state and AI logic
2. Easy to add new AI types
3. Uniform move handling regardless of player type
4. Flexible configuration of player types
5. Clear game loop that works the same for all player combinations

Would you like me to elaborate on any part of this implementation?


# Quoridor API
## Small modifications
Rename fence to wall
## Big modifications
Correct the bug in place_wall which allows player to block path of opponent
#### Create a null renderer for use to check if the history is valid
Separate TerminalView into GameStateManager and CLIEngine(GameEngine)
```Almost done```
Implement all the commands in GameStateManager
```Basic architecture is ok, need to implement the commands```
Integrate verbose and debug mode into GameEngine
```
Stuff could be like inside CLIEngine:
if verbose_mode: 
    print information about internal stuff
else if debug_mode:
    print some other stuff
Other stuff in GUIEngine blabla
```
Make a pawn_deplacement class?
Make a wall_placement class?
Implement command pattern for wall/pawn/undo/redo etc? Maybe not

## Main.py entry point
1.Read the config file .quoridorrc and load the global constants
Or initialize the constants with values passed as arguments
Or use default values blabla

2.Load game from a file by calling Lucy's functions
Have to check if the history is valid by simulating the moves by initilizing a gamestatemanager blabla
This game state manager then doesn't have a renderer? Will the abc GameEngine be ok?

3.Initialize the AI controllers
There should be a dictionary mapping player_id to AI controller
Then in gamestatemanager, use sth like
if current_player_id in ai_controllers:
    ai_controller = ai_controllers[current_player_id]
    move = ai_controller.get_move(current_state)
else:
    move = get_move_from_user()

## Gamestate class
board: Graph
current_player: Player
players: list[Player]
blitz_mode: bool
history: list[list[str]]
move_count: int
create_board(size: int) -> Graph

### Player class
player_id: int
position: (int, int)
walls_remaining: int
time_remaining: int //(in seconds, -1 if not in blitz mode, default is 15 minutes or 900 seconds)
start_position: (int, int)
goal_line: list[(int, int)]
is_winning(self) -> bool

## Graph class
add_node(node:(int, int)) -> None
add_edge(node1:(int, int), node2:(int, int)) -> None
edge_exists(node1:(int, int), node2:(int, int)) -> bool
node_exists(node:(int, int)) -> bool
remove_node(node:(int, int)) -> None
remove_edge(node1:(int, int), node2:(int, int)) -> None
bfs(node1:(int, int), node2:(int, int)) -> list[(int, int)]
dfs(node1:(int, int), node2:(int, int)) -> list[(int, int)]
a_star(node1:(int, int), node2:(int, int)) -> list[(int, int)]

## GameStateManager
current_state: GameState
renderer: Renderer
initial_state: GameState
legal_pawn_deplacements: dict[player_id: list[str]]
legal_wall_placements: list[str]
run_game(self) -> None
translate_pawn_deplacement_to_edge(move: str) -> ((int, int), (int, int))
>Get these 2 function from TerminalView

next_player(self) -> Player
temp_board -> Graph
move_pawn(from: (int, int), to: (int, int)) -> None
place_wall(player: Player, wall: str) -> None
>Refactor the hell out of this function

get_previous_state(self.current_state) -> GameState
get_next_state(self.current_state) -> GameState

restart_game(self) -> None
quit_game(self) -> None
save_game(self) -> None
load_game(self) -> None
undo_move(self) -> None
redo_move(self) -> None


## CLI Engine
print_board(self) -> None
>Get this function from TerminalView


## CLI handled directly by main.py?
>Uses the IO module
number_of_players: int //(1 or 2 or 3 or 4)
wall_limit: int //(default is 10)

## IO module handled by io.py
Be able to read the config file .quoridorrc (INI format) and initialize the game
Be able to read from an ASCII file and return a gamestate object
Be able to write a gamestate object to an ASCII file

### History of moves
>1. 1 e1-e2 2 a10-a9 3 e2-e3 4 a9v 
>2. 1 a6v 2 a9-a8 3 e4-e5 4 a8-a7
>history is a list of the rounds
>for example:  [["e1-e2", "a10-a9", "e2-e3", "a9v"], ["a6v", "a9-a8", "e4-e5", "a8-a7"], ["e3-e4", "a7-a6", "e5-e6", "a6-a5"]]

history: list[list[str]]
play_move(move:str) -> None // Updates current_player, history, and the board

## AI player
Random AI
Minimax AI
Depth, heuristic, alpha-beta pruning
Have a function that return a move
Takes a gamestate by reference or else?

## GUI engine