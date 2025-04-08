"""
IO module.
==========================

Provides functionality for reading and writing game history files for a Quoridor game.
Handles parsing game moves from a text file and writing formatted game history back to a file.

Usage:
------
# Reading game history from a file
game_history = ReadWriteHistory.read_history("history.txt")

# Writing game history to a file
turns = [["e2", "e3"], ["d4", "d5"]]
ReadWriteHistory.write_history("output_history.txt", turns)
"""

from typing import TYPE_CHECKING
from quoridor.graph import Graph
from quoridor.exceptions import InvalidMoveError

if TYPE_CHECKING:
    from quoridor.command import Command
    from quoridor.gamestate import GameState


def write_to_file(file: str, content: str):
    """
    Write out the content of a string to a file
    """
    with open(file, "w") as file_to_write:
        file_to_write.write(content)


# TODO: Change legacy code to adopt a modular approach
class ReadWriteHistory:
    """
    Reading and writing Quoridor game history.

    Provides methods to:
    - Read a history file and extract player moves per turn.
    - Write formatted game history to a text file.

    Methods:
    --------
    read_history(input_file_path: str) -> list[list[str]]
        Reads a history file and returns a nested list of game moves.

    _get_game_info_from_file(history_array: list[str]) -> list[list[str]]
        Parses raw history data into a structured format.

    _process_moves(turn_nb: int, line_sections: list[str], game_info: list[list[str]]) -> None
        Processes and extracts player moves for a given turn.

    write_history(output_file_path: str, turns: list[list[str]]) -> None
        Writes a formatted game history file.

    Usage:
    ------
    history = ReadWriteHistory.read_history("game_history.txt")
    ReadWriteHistory.write_history("output.txt", history)
    """

    @staticmethod
    def read_history(input_file_path: str) -> list[list[tuple[int, str]]]:
        """
        Reads the history from a text input file and returns an array containing
        the game information, a list of game moves per player per turn.
        """
        try:
            # open file
            with open(input_file_path, "r", encoding="utf-8") as input_file:
                history_array = [
                    line
                    for line in input_file
                    if not line.startswith("#") and line.strip()
                ]
            if history_array == []:
                print("Input file path is empty.")
                return []
            return ReadWriteHistory._get_game_info_from_file(history_array)

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
    def _get_game_info_from_file(history_array: list[str]) -> list[list[str]]:
        """
        Extracts the moves done by each player for each turn from raw history data and puts them
        into an array.
        game_info = [nb_of_turns][nb_of_players].
        """
        game_info: list[tuple[int, str]] = []
        max_players = 0
        try:
            for turn_nb, turn in enumerate(history_array):
                line_sections = turn.split()
                # Check there are lines and all start with turn number
                if not line_sections or not line_sections[0].endswith("."):
                    print(f"Invalid line for turn: {turn_nb + 1}")
                    continue  # Skip invalid line
                turn_nb = int(line_sections[0][:-1])
                max_players = max(max_players, (len(line_sections) - 1) // 2)
                while len(game_info) < turn_nb:
                    game_info.append(
                        [(-1, "")] * max_players
                    )  # Initialize turn with empty moves

                ReadWriteHistory._process_moves(turn_nb, line_sections, game_info)

            return game_info

        except (ValueError, IndexError) as error:
            print(f"Error processing game data: {error}")
            return []

    @staticmethod
    def _process_moves(
        turn_nb: int, line_sections: list[str], game_info: list[tuple[int, str]]
    ) -> None:
        """Extract and process player moves for a given turn."""
        for i in range(1, len(line_sections), 2):
            move = None
            try:
                player_id = int(line_sections[i])
                move = line_sections[i + 1]
                # print(player_id,move)
                game_info[turn_nb - 1][player_id - 1] = (player_id, move)

            except (IndexError, ValueError) as error:
                print(
                    f"Warning: Skipping invalid move {move} at turn {turn_nb}: {error}"
                )
                continue

    @staticmethod
    def write_history(output_file_path: str, turns: list[list[str]]):
        """Writes a history text file with the game information in the 'turns' parameter."""
        try:
            with open(output_file_path, "w", encoding="utf-8") as history_file:
                history_file.write(
                    "# Quoridor Game History"
                )  # EOF should be positioned new line
                for turn_nb, turn in enumerate(turns):
                    turn_str = " ".join(f"{move}" for player, move in enumerate(turn))
                    history_file.write(f"\n{turn_nb + 1}. {turn_str} ")

                history_file.write("\n")  # Add a new line for futur writing
            print(f"History successfully written to {output_file_path}")

        except IOError:
            print(f"Error: Could not write to file '{output_file_path}'.")

    @staticmethod
    def parse_history_to_list_of_str(
        history: list[tuple[int, "Command"]], state: "GameState"
    ) -> list[list[str]]:
        from quoridor.command import AbandonCommand

        game_info: list[list[str]] = []
        current_turn: list[str] = []

        players_alive = {p.id for p in state.players if not p.is_dead}
        players_this_turn = set()

        for player_id, cmd in history:
            if isinstance(cmd, AbandonCommand):
                cmd_str = f"{player_id + 1} SURRENDER"
                players_alive.discard(player_id)
            else:
                cmd_str = f"{player_id + 1} {str(cmd)}"
            current_turn.append(cmd_str)
            players_this_turn.add(player_id)

            if players_alive.issubset(players_this_turn):
                game_info.append(current_turn)
                current_turn = []
                players_this_turn = set()

        if current_turn:
            game_info.append(current_turn)

        return game_info

    @staticmethod
    def parse_list_of_str_to_history(
        state: "GameState", turns: list[list[tuple[int, str]]]
    ) -> list[tuple[int, "Command"]]:
        from quoridor.cliengine import CLIEngine
        from quoridor.command import AbandonCommand, MovePawnCommand, PlaceWallCommand

        c = CLIEngine(state)
        cmds: list[tuple[int, Command]] = []
        for turn in turns:
            for player_id, cmd_str in turn:
                try:
                    if player_id >= 0:
                        pid = player_id - 1
                        if cmd_str == "SURRENDER":
                            cmd = AbandonCommand(state, pid)
                            c.execute_command(cmd)
                        elif len(cmd_str) == 2 or (
                            len(cmd_str) >= 3 and not cmd_str[-1] in "hv"
                        ):
                            _, to_case = cmd_str.strip().lower().split("-")
                            to_pos = c.translate_move(to_case)
                            from_pos = state.players[pid].position
                            cmd = MovePawnCommand(state, from_pos, to_pos)
                            c.execute_command(cmd)
                        elif len(cmd_str) >= 3 and cmd_str[-1] in "hv":
                            x, y, direction = c.translate_wall(cmd_str)
                            cmd = PlaceWallCommand(state, (x, y), direction)
                            c.execute_command(cmd)
                        else:
                            raise InvalidMoveError(f"Command not found : {cmd_str}")
                        cmds.append((pid, cmd))

                except (InvalidMoveError, ValueError, IndexError) as e:
                    print(
                        f"Commande ignorée pour le joueur {player_id} : '{cmd_str}' → {e}"
                    )
        c = None
        return cmds

    @staticmethod
    def num_players_from_file(turns: list[list[tuple[int, str]]]) -> int:
        num_players = 0
        for turn in turns:
            for i in turn:
                id, _ = i
                num_players = max(id, num_players)
        return num_players
