# TODO: exceptions

class Foo:
    def readHistory(inputFilePath):
        file = open(inputFilePath, "r")
        history = []
        for line in file:
            if line.startswith("#") or not line:
                continue  # Skip commented lines and empty lines
            history.append(line)
        if not history:
            print("File path is empty.")
            return
        
        movesPerPlayer = {}
        nbVertWall = 0
        nbHorzWall = 0

        for turn in history:
            lineSections = turn.split()
            # Check there are lines and all start with turn number
            if not lineSections or not lineSections[0].endswith("."):
                print(f"Invalid line: {turn}")
                continue # Skip invalid line

            turnNb = lineSections[0][:-1]
            print(f"Turn {turnNb}:")
            for i in range(1, len(lineSections), 2):
                playerId = int(lineSections[i])
                move = lineSections[i + 1]
                if playerId not in movesPerPlayer:
                    movesPerPlayer[playerId] = []
                movesPerPlayer[playerId].append(move)

                if (move == "skip"):
                    print(f"  Player {playerId} SKIPPED their turn.")
                elif move.endswith("v"): # Vertical wall
                    print(f"  Player {playerId} placed a vertical wall: {move}")
                    nbVertWall = nbVertWall + 1
                elif move.endswith("h"): # Horizontal wall
                    print(f"  Player {playerId} placed a horizontal wall: {move}")
                    nbHorzWall = nbHorzWall + 1
                else: 
                    print(f"  Player {playerId} moved: {move}")

        nbPlayers = len(movesPerPlayer)
        print(f"\nNumber of players: {nbPlayers}")
        print(f"\nNumber of vertical walls placed: {nbVertWall}")
        print(f"\nNumber of horizontal walls placed: {nbHorzWall}")

        print("\nMove Summary:")
        for player, moves in movesPerPlayer.items():
            print(f"Player {player} made these moves: {', '.join(moves)}")


    def writeHistory(turns):
        historyFile = open("outputHistory.txt", "w+")
        historyFile.write("# Quoridor Game History")
        for turnNb, turn in enumerate(turns):
            historyFile.write(f"\n{turnNb + 1}. ")
            for player, move in enumerate(turn):
                historyFile.write(f"{player + 1} {move} ")




# Testing readHistory
print("##########TEST 1##########")
Foo.readHistory("testHistory1.txt")

print("##########TEST 2##########")
Foo.readHistory("testHistory2.txt")

print("######TEST TWO PLAYER######")
Foo.readHistory("testHistoryTwoPlayer.txt")

print("######TEST SKIP######")
Foo.readHistory("testHistorySkip.txt")

# Testing writeHistory
turnsTest1 = [["e1-e2", "a10-a9", "e2-e3", "a9v"], ["a6v", "a9-a8", "e4-e5", "a8-a7"], ["e3-e4", "a7-a6", "e5-e6", "a6-a5"]]
# Foo.writeHistory(turnsTest1)

turnsTestSkip = [["e1-e2", "a10-a9", "e2-e3", "a9v"], ["a6v", "a9-a8", "skip", "a8-a7"], ["e3-e4", "a7-a6", "e5-e6", "a6-a5"]]
Foo.writeHistory(turnsTestSkip)