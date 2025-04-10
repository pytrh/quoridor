import logging
import threading
import time
import os

from quoridor.gamemode import GameMode
from quoridor.observer import Observer


class Timer:

    def __init__(self, blitz_time: int, game_mode: GameMode, player_id: int):
        """
        Initialize a Timer object to manage countdown timing in blitz game modes.

        Args:
            blitz_time (int): The amount of time (in seconds) assigned to a player per turn.
            game_mode (GameMode): The current game mode (e.g., BLITZ, BLITZ_LONG).
        """
        self.game_mode = game_mode
        self.initial_time = blitz_time
        self.current_time = blitz_time
        self.turn_start_time = None
        self._stop_event = threading.Event()
        self.display_lock = threading.Event()
        self._watchdog_thread = None
        self.player_id = player_id
        self.gui = None

    def start_turn(self, reset_timer: bool = False):
        """
        Start a player's turn and launch the countdown watchdog.

        Args:
            current_player (int): The ID of the player whose turn it is.
            blitz_mode_active (bool): Whether the blitz timer should reset at each turn.
        """
        if reset_timer:
            self.current_time = self.initial_time
        self.turn_start_time = time.time()

        if self.game_mode == GameMode.BLITZ:
            self._stop_event.clear()
            self._watchdog_thread = threading.Thread(target=self._timeout_watchdog)
            self._watchdog_thread.start()

    def end_turn(self):
        """
        End the current turn, update the remaining time, and stop the watchdog thread.
        """
        if self.game_mode == GameMode.BLITZ and self.turn_start_time is not None:
            turn_end_time = time.time() - self.turn_start_time
            self.current_time -= int(turn_end_time)
            self.turn_start_time = None
            self._stop_event.set()
            if (
                self._watchdog_thread.is_alive()
                and self._watchdog_thread is not threading.current_thread()
            ):
                self._watchdog_thread.join()
            self._watchdog_thread = None

    def get_time_remaining(self) -> int: # NOTE: never used
        """
        Return the current remaining time for the player.

        Returns:
            int: Time left in seconds.
        """
        return self.current_time

    def set_gui_observer(self, gui: Observer):
        self.gui = gui

    def _timeout_watchdog(self):
        """
        Internal method run in a separate thread that monitors the countdown.
        If time runs out, it terminates the game.

        Args:
            current_player (int): The player being monitored for timeout.
        """
        while not self._stop_event.is_set():
            now = time.time()
            elapsed = int(now - self.turn_start_time)
            self.remaining = max(0, self.current_time - elapsed)

            if self.gui is not None:
                self.gui.update_timer(self.remaining, self.player_id)

            if not self.display_lock.is_set():
                print(f"\r[⏳ Remaining: {self.remaining}s] ", end="", flush=True)

            if self.remaining <= 0:
                print(f"\n⏰ Time out! Player {self.player_id + 1} has lost the game!")
                if self.gui is not None:
                    self.gui.handle_timer_end_for_player(self.player_id)
                    break
                else:
                    self.end_turn()
                    break

            time.sleep(0.5)
