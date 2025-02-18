# Quoridor API
>How to handle the case with temporary fences?

## CLI handled directly by main.py
>Uses the IO module
number_of_players: int //(1 or 2 or 3 or 4)
fence_limit: int //(default is 10)

## IO module handled by io.py
Be able to read the config file .quoridorrc (INI format) and initialize the game
Be able to read from an ASCII file and return a gamestate object
Be able to write a gamestate object to an ASCII file

## Graph class
>Node are int tuples from (1, 1) to (9, 9)
>Edges are tuples of nodes

add_node(node:(int, int)) -> None
add_edge(node1:(int, int), node2:(int, int)) -> None
edge_exists(node1:(int, int), node2:(int, int)) -> bool
node_exists(node:(int, int)) -> bool
remove_node(node:(int, int)) -> None
remove_edge(node1:(int, int), node2:(int, int)) -> None
bfs(node1:(int, int), node2:(int, int)) -> list[(int, int)]
dfs(node1:(int, int), node2:(int, int)) -> list[(int, int)]
a_star(node1:(int, int), node2:(int, int)) -> list[(int, int)]

## Gamelogic
>Encapsulate the rules of the game
>Takes a gamestate and returns the legal moves

## Gamestate class
### Current player
>Either 1 or 2 or 3 or 4

current_player: int //(1 or 2 or 3 or 4)

### Time left if in blitz mode
time_left: int //(in seconds, -1 if not in blitz mode, default is 15 minutes or 900 seconds)
### State of the board
>Players positions: (int, int)
>Fences positions are reflected by the edges of the graph
>Available fences for each player: int, main.fence_limit

**Make Player class?**
player_1_position: (int, int)
player_2_position: (int, int)
player_3_position: (int, int)
player_4_position: (int, int)
player_1_fences: int
player_2_fences: int
player_3_fences: int
player_4_fences: int
board: Graph

### History of moves
>1. 1 e1-e2 2 a10-a9 3 e2-e3 4 a9v 
>2. 1 a6v 2 a9-a8 3 e4-e5 4 a8-a7
>history is a list of the rounds
>for example:  [["e1-e2", "a10-a9", "e2-e3", "a9v"], ["a6v", "a9-a8", "e4-e5", "a8-a7"], ["e3-e4", "a7-a6", "e5-e6", "a6-a5"]]

history: list[list[str]]
play_move(move:str) -> None // Updates current_player, history, and the board

## GUI engine