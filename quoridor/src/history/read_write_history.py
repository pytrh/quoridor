class ReadWriteHistory:
    @staticmethod
    def read_history(input_file_path : str) -> None:
        # Open file
        try :
            with open(input_file_path, "r") as input_file:
                history_array = [line for line in input_file
                                                    if not line.startswith("#") and line.strip()]
            if not history_array:
                print("Input file path is empty.")
                return None
            # Get game info
            game_info : tuple = ReadWriteHistory.get_game_info_from_file(history_array)
            # Print game info
            ReadWriteHistory.print_game_info(len(game_info[1]), game_info[0],
                                                   game_info[2], game_info[3],
                                                   game_info[1].items())
                                                    # NOTE: passing tuple better?

        except FileNotFoundError:
            print(f"Error: The file '{input_file_path}' was not found.")
        except ValueError as ve:
            print(ve)
        except Exception as e:
            print(f"An unexpected error occurred while reading the file: {e}")


    @staticmethod
    def get_game_info_from_file(history_array : list[str]) -> tuple[str, dict[int, list[str]],
                                                                     int, int]:
        moves_per_player: dict[int, list[str]] = {}
        nb_vert_wall : int = 0
        nb_horz_wall : int = 0

        try:
            for turn in history_array:
                line_sections = turn.split()
                # Check there are lines and all start with turn number
                if not line_sections or not line_sections[0].endswith("."):
                    print(f"Invalid line for turn: {turn}")
                    continue # Skip invalid line

                turn_nb = line_sections[0][:-1]
                print(f"Turn {turn_nb}:")
                for i in range(1, len(line_sections), 2):
                    try:
                        player_id = int(line_sections[i])
                        move = line_sections[i + 1]
                        moves_per_player.setdefault(player_id, []).append(move)
                        if move == "skip":
                            print(f"  Player {player_id} SKIPPED their turn.")
                        elif move.endswith("v"): # Vertical wall
                            print(f"  Player {player_id} placed a vertical wall: {move}")
                            nb_vert_wall += 1
                        elif move.endswith("h"): # Horizontal wall
                            print(f"  Player {player_id} placed a horizontal wall: {move}")
                            nb_horz_wall += 1
                        else:
                            print(f"  Player {player_id} moved: {move}")

                    except (IndexError, ValueError):
                        print(f"Warning: Skipping invalid move {move} at turn {turn}")
                        continue

            return [turn_nb, moves_per_player, nb_vert_wall, nb_horz_wall]

        except Exception as e:
            print(f"An error occurred while processing game data: {e}")
            return [0, {}, 0, 0]  # Return empty values


    @staticmethod
    def print_game_info(nb_players : int, turn_nb : int, nb_vert_wall : int, nb_horz_wall : int,
                        players_moves : dict) -> None:
        try:
            print(f"\nNumber of players: {nb_players}")
            print(f"Number of turns: {turn_nb}")
            print(f"Number of vertical walls placed: {nb_vert_wall}")
            print(f"Number of horizontal walls placed: {nb_horz_wall}")
            print("\nMove Summary:")
            for player, moves in players_moves:
                print(f"Player {player} made these moves: {', '.join(moves)}")
            print("\n")

        except Exception as e:
            print(f"An error occurred while printing game info: {e}")


    @staticmethod
    def write_history(turns):
        try:
            output_file_path : str = "outputHistory.txt"
            with open(output_file_path, "w+") as history_file:
                history_file.write("# Quoridor Game History")
                for turn_nb, turn in enumerate(turns):
                    turn_str = " ".join(f"{player + 1} {move}" for player, move in enumerate(turn))
                    history_file.write(f"\n{turn_nb + 1}. {turn_str} ")
            print(f"History successfully written to {output_file_path}")

        except IOError:
            print(f"Error: Could not write to file '{output_file_path}'.")
        except Exception as e:
            print(f"An unexpected error occurred while writing the history: {e}")


# Testing read_history
print("##########TEST 1##########")
ReadWriteHistory.read_history("test_history1.txt")

print("##########TEST 2##########")
ReadWriteHistory.read_history("test_history2.txt")

print("######TEST TWO PLAYER######")
ReadWriteHistory.read_history("test_history_two_player.txt")

print("######TEST SKIP######")
ReadWriteHistory.read_history("test_history_skip.txt")

# Testing writeHistory
turnsTest1 = [["e1-e2", "a10-a9", "e2-e3", "a9v"],
              ["a6v", "a9-a8", "e4-e5", "a8-a7"],
              ["e3-e4", "a7-a6", "e5-e6", "a6-a5"]]
# Read_write_history
#.writeHistory(turnsTest1)

turnsTestSkip = [["e1-e2", "a10-a9", "e2-e3", "a9v"],
                 ["a6v", "a9-a8", "skip", "a8-a7"],
                 ["e3-e4", "a7-a6", "e5-e6", "a6-a5"]]
ReadWriteHistory.write_history(turnsTestSkip)
