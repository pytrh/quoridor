class ReadWriteHistory:
    @staticmethod
    def read_history(input_file_path : str) -> None:
        try :
            with open(input_file_path, "r", encoding="utf-8") as input_file:
                history_array = [line for line in input_file
                                                    if not line.startswith("#") and line.strip()]
            if not history_array:
                print("Input file path is empty.")
                return []

            game_info : list[list] = ReadWriteHistory.get_game_info_from_file(history_array)
            return game_info

        except FileNotFoundError:
            print(f"Error: The file '{input_file_path}' was not found.")
            return []
        except ValueError as value_error:
            print(value_error)
            return []
        except IOError as io_error:
            print(f"An unexpected error occurred while reading the file: {io_error}")
            return []


    @staticmethod
    def get_game_info_from_file(history_array : list[str]) -> list[list[str]]:
        game_info : list[list[str]] = []
        max_players = 0
        try:
            for turn in history_array:
                line_sections = turn.split()
                # Check there are lines and all start with turn number
                if not line_sections or not line_sections[0].endswith("."):
                    print(f"Invalid line for turn: {turn}")
                    continue # Skip invalid line

                turn_nb = int(line_sections[0][:-1])
                max_players = max(max_players, (len(line_sections) - 1) // 2)
                while len(game_info) < turn_nb:
                    game_info.append([""] * max_players)  # Initialize turn with empty moves

                for i in range(1, len(line_sections), 2):
                    try:
                        player_id = int(line_sections[i])
                        move = line_sections[i + 1]
                        game_info[turn_nb - 1][player_id - 1] = move

                    except (IndexError, ValueError) as err:
                        print(f"Warning: Skipping invalid move {move} at turn {turn}: {err}")
                        continue

            return game_info

        except (ValueError, IndexError, TypeError) as error:
            print(f"Error processing game data: {error}")
            return []


    @staticmethod
    def write_history(output_file_path : str, turns : list[list[str]]):
        try:
            with open(output_file_path, "a", encoding="utf-8") as history_file:
                history_file.write("# Quoridor Game History") # EOF should be positioned new line
                for turn_nb, turn in enumerate(turns):
                    turn_str = " ".join(f"{player + 1} {move}" for player, move in enumerate(turn))
                    history_file.write(f"\n{turn_nb + 1}. {turn_str} ")

                history_file.write("\n") # Add a new line for futur writing
            print(f"History successfully written to {output_file_path}")

        except IOError:
            print(f"Error: Could not write to file '{output_file_path}'.")
