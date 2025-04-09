import copy
import importlib
import logging
import time
import gi

from quoridor.command import (
    Command,
    PassCommand,
    PlaceWallCommand,
    MovePawnCommand,
    SaveAndQuitCommand,
    SaveCommand,
    UndoCommand,
    RedoCommand,
    RestartCommand,
    QuitCommand,
    AbandonCommand,
)
from quoridor.direction import Direction
from quoridor.exceptions import InvalidMoveError, QuitApp
from quoridor.gamemode import GameMode, AiMode, AiHeuristic
from quoridor.gamestate import GameState
from quoridor.observer import Observer

from quoridor.config import (
    BLITZ_TIME,
    DEFAULT_AI_COLOR_ID,
    GRID_SIZE,
    MIN_GRID_SIZE,
    MAX_GRID_SIZE,
    NUM_WALLS,
)
from quoridor.ai import GreedyAI

from quoridor.parser import parse_string_to_state
from quoridor.translations import T_


gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, Gio, GLib, GObject


class MainWindow(Gtk.ApplicationWindow, Observer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(600, 400)

        self.state = None
        self.initial_state = None
        self.game_is_over = False

        self._number_of_players = None
        self._board_size = None
        self._num_walls = None

        self._game_mode = None
        self._blitz_time = None
        self._ai_ids = set()
        self._ai_mode = None
        self._ai_depth = None
        self._ai_heuristic = None
        self._history = None

        self.hint_cases = []
        self.hint_activate = False
        self.hint_symbole = "⏺️"
        self.popup_activated = True

        GLib.set_application_name("quoridor")

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(300)

        self.home_page = self.create_home_page()
        self.stack.add_named(self.home_page, "home")

        self.new_game_page = self.create_new_game_page()
        self.stack.add_named(self.new_game_page, "new_game")

        self.running_game_page = self.create_running_game_page()
        self.stack.add_named(self.running_game_page, "running_game")

        self.about_page = self.create_about_page()
        self.stack.add_named(self.about_page, "about")

        self.end_page = self.create_end_page()
        self.stack.add_named(self.end_page, "end")

        self.set_child(self.stack)

        self.open_dialog = Gtk.FileChooserNative.new(
            title="Select a file", parent=self, action=Gtk.FileChooserAction.OPEN
        )
        self.open_dialog.set_modal(True)

        f = Gtk.FileFilter()
        f.set_name("Quoridor game file")
        f.add_mime_type("text/plain")

        self.open_dialog.set_filter(f)
        self.open_dialog.connect("response", self.open_response)

    def create_home_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)

        title = Gtk.Label()
        title.set_markup(
            '<span size="18000" weight="bold" foreground="#8B0000">QUORIDOR</span>'
        )
        title.set_justify(Gtk.Justification.CENTER)
        title.set_halign(Gtk.Align.CENTER)
        title.set_css_classes(["title"])
        box.append(title)

        self.create_button_for_menu(box, self.on_new_game_clicked, "New Game")
        self.create_button_for_menu(box, self.on_load_game_clicked, "Load Game")
        self.create_button_for_menu(box, self.on_about_clicked, "About")

        return box

    def create_new_game_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)

        self.create_return_button(box)
        self.create_nb_players(box)
        self.create_board_size_slider(box)
        self.create_wall_number_slider(box)
        self.create_game_mode(box)
        self.create_ai_switch(box)
        self.create_start_button(box)

        return box

    def create_running_game_page(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        main_box.set_halign(Gtk.Align.CENTER)
        main_box.set_valign(Gtk.Align.CENTER)

        # Left column (buttons)
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left_box.set_margin_top(20)
        left_box.set_margin_bottom(20)
        left_box.set_margin_start(20)
        left_box.set_margin_end(20)
        left_box.set_halign(Gtk.Align.CENTER)
        left_box.set_valign(Gtk.Align.CENTER)
        main_box.append(left_box)

        game_button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        game_button_box.set_halign(Gtk.Align.CENTER)
        game_button_box.set_valign(Gtk.Align.CENTER)
        restart_button = Gtk.Button(label="🔄 Restart")
        restart_button.connect("clicked", self.on_restart_clicked)

        download_button = Gtk.Button(label="📥 Save")
        download_button.set_size_request(20, 10)
        download_button.set_halign(Gtk.Align.START)
        download_button.connect("clicked", self.on_save_history)

        power_button = Gtk.Button(label="🚪 Quit")
        power_button.set_size_request(20, 10)
        power_button.set_halign(Gtk.Align.START)
        power_button.connect("clicked", self.on_quit_game_and_save)

        btn_abandon = Gtk.Button(label="🏳️ Abandon")
        btn_abandon.set_size_request(20, 10)
        btn_abandon.set_halign(Gtk.Align.START)
        btn_abandon.connect("clicked", self.on_abandon_game)

        game_button_box.append(restart_button)
        game_button_box.append(download_button)
        game_button_box.append(power_button)
        game_button_box.append(btn_abandon)
        left_box.append(game_button_box)

        self.game_players_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=10
        )
        self.game_players_box.set_halign(Gtk.Align.CENTER)
        self.game_players_box.set_valign(Gtk.Align.CENTER)
        left_box.append(self.game_players_box)

        # Game box
        game_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        game_box.set_margin_top(20)
        game_box.set_margin_bottom(20)
        game_box.set_margin_start(20)
        game_box.set_margin_end(20)
        game_box.set_halign(Gtk.Align.CENTER)
        game_box.set_valign(Gtk.Align.CENTER)
        # Game grid
        self.game_grid = Gtk.Grid()
        self.game_grid.set_row_homogeneous(True)
        self.game_grid.set_column_homogeneous(True)
        self.game_grid.set_size_request(300, 300)
        self.game_grid.set_vexpand(False)
        self.game_grid.set_hexpand(False)
        # Game walls
        walls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        walls_box.set_halign(Gtk.Align.CENTER)
        walls_box.set_valign(Gtk.Align.CENTER)
        self.horizontal_wall = Gtk.Button(label="─")
        self.vertical_wall = Gtk.Button(label="│")
        walls_box.append(Gtk.Label(label="Horizontal"))
        walls_box.append(self.horizontal_wall)
        walls_box.append(Gtk.Label(label="Vertical"))
        walls_box.append(self.vertical_wall)

        self.current_player_label = Gtk.Label(label="Current player")
        game_box.append(self.current_player_label)
        game_box.append(Gtk.Label(label="Drag n Drop to play"))
        game_box.append(self.game_grid)
        game_box.append(walls_box)

        # list history
        self.scrolled_window_history = Gtk.ScrolledWindow()
        self.scrolled_window_history.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        self.scrolled_window_history.set_vexpand(True)
        self.scrolled_window_history.set_size_request(600, 100)
        game_box.append(self.scrolled_window_history)
        main_box.append(game_box)

        # Right column (Chrono and arrows undo / redo)
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self.timer_label = Gtk.Label(label="00:00")
        right_box.append(self.timer_label)

        arrow_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        right_box.append(arrow_box)

        left_arrow = Gtk.Button(label="⬅ Undo")
        left_arrow.connect("clicked", self.on_undo_clicked)
        right_arrow = Gtk.Button(label="Redo ➡")
        right_arrow.connect("clicked", self.on_redo_clicked)
        arrow_box.append(left_arrow)
        arrow_box.append(right_arrow)

        hint_button = Gtk.Button(label="💡 Hint")
        hint_button.set_size_request(20, 10)
        hint_button.set_halign(Gtk.Align.CENTER)
        hint_button.connect("clicked", self.on_hint_clicked)
        right_box.append(hint_button)

        self.btn_pass_turn = Gtk.Button(label="⏭ Pass turn")
        self.btn_pass_turn.set_size_request(20, 10)
        self.btn_pass_turn.set_halign(Gtk.Align.CENTER)
        self.btn_pass_turn.connect("clicked", self.on_pass_turn)
        self.btn_pass_turn.set_visible(False)
        right_box.append(self.btn_pass_turn)
        main_box.append(right_box)

        return main_box

    def create_about_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(40)
        box.set_margin_end(40)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)

        self.create_return_button(box)

        title = Gtk.Label()
        title.set_markup(
            '<span size="18000" weight="bold" foreground="#8B0000">QUORIDOR</span>'
        )
        title.set_halign(Gtk.Align.CENTER)
        box.append(title)

        version = importlib.metadata.version("quoridor")
        box.append(
            self.create_label_for_about(
                f"""<span size="12000" weight="bold">Version:</span> <span size="12000">{version}</span>"""
            )
        )
        box.append(
            self.create_label_for_about(
                f"""<span size="12000" weight="bold">Developers:</span> <span size="12000">Mohamad Almousa, Lucy Curtis, Lucas Danglard, Bastien Rocher, Zhaoyuan Song</span>"""
            )
        )
        box.append(
            self.create_label_for_about(
                f"""<span size="12000" weight="bold">Expected release date:</span> <span size="12000">April 2025</span>"""
            )
        )
        box.append(
            self.create_label_for_about(
                f"""<span size="12000" weight="bold">Description:</span> """
            )
        )
        box.append(
            self.create_label_for_about(
                f"""<span size="10000">QUORIDOR is a two, three (although not recommended) or four-player intuitive strategy game.</span>"""
            )
        )
        box.append(
            self.create_label_for_about(
                f"""<span size="10000">The aim of the game is to reach the opposite side of the grid before the other players. While simultaniously navigating through walls placed by players.</span>"""
            )
        )

        return box

    def create_label_for_about(self, text):
        label = Gtk.Label()
        label.set_markup(text)
        label.set_justify(Gtk.Justification.CENTER)
        label.set_halign(Gtk.Align.CENTER)
        label.set_wrap(True)
        return label

    def create_end_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(40)
        box.set_margin_end(40)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)

        title = Gtk.Label()
        title.set_markup(
            '<span size="18000" weight="bold" foreground="#008000">GAME OVER</span>'
        )
        title.set_halign(Gtk.Align.CENTER)
        box.append(title)

        self.winner_label = Gtk.Label()
        self.winner_label.set_markup(
            f'<span size="14000" weight="bold">You won!</span>'
        )
        self.winner_label.set_halign(Gtk.Align.CENTER)
        box.append(self.winner_label)

        button_box = Gtk.Box(spacing=10)
        button_box.set_halign(Gtk.Align.CENTER)

        restart_button = Gtk.Button(label="Play Again")
        restart_button.connect("clicked", self.on_restart_clicked)
        button_box.append(restart_button)

        home_button = Gtk.Button(label=T_("Go Home"))
        home_button.connect("clicked", self.on_back_home)
        button_box.append(home_button)

        box.append(button_box)
        return box

    def create_button_for_menu(self, box, function, text):
        btn = Gtk.Button(label=text)
        btn.set_size_request(150, 50)
        btn.set_halign(Gtk.Align.CENTER)
        btn.connect("clicked", function)
        box.append(btn)

    def create_return_button(self, box):
        btn_back = Gtk.Button(label="Back")
        btn_back.set_size_request(20, 10)
        btn_back.set_halign(Gtk.Align.START)
        btn_back.connect("clicked", self.on_back_home)
        box.append(btn_back)

    def create_nb_players(self, box):
        self.create_option_label(box, "Number of players:")

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        self.btn_nb_players_2 = Gtk.CheckButton(label="2")
        self.btn_nb_players_3 = Gtk.CheckButton(label="3 (not recommended)")
        self.btn_nb_players_4 = Gtk.CheckButton(label="4")

        self.btn_nb_players_2.set_active(True)  # Two players by default

        self.btn_nb_players_3.set_group(self.btn_nb_players_2)
        self.btn_nb_players_4.set_group(self.btn_nb_players_3)

        self.btn_nb_players_2.connect("toggled", self.on_player_button_toggled, "2")
        self.btn_nb_players_3.connect("toggled", self.on_player_button_toggled, "3")
        self.btn_nb_players_4.connect("toggled", self.on_player_button_toggled, "4")

        hbox.append(self.btn_nb_players_2)
        hbox.append(self.btn_nb_players_3)
        hbox.append(self.btn_nb_players_4)

        box.append(hbox)

    def create_board_size_slider(self, box):
        self.create_option_label(box, "Board length :")
        self.board_slider = Gtk.Scale()
        self.board_slider.set_digits(0)
        self.board_slider.set_range(MIN_GRID_SIZE, MAX_GRID_SIZE)
        self.board_slider.set_increments(2, 2)
        self.board_slider.set_draw_value(True)
        self.board_slider.set_value(GRID_SIZE)
        self.board_slider.connect("value-changed", self.slider_changed_board)
        box.append(self.board_slider)

    def slider_changed_board(self, slider):
        value = round(slider.get_value())
        if value % 2 == 0:
            value += 1 if value < 15 else -1
        slider.set_value(value)
        self._board_size = int(slider.get_value())

    def create_wall_number_slider(self, box):
        self.create_option_label(box, "Number of walls per player :")
        self.wall_slider = Gtk.Scale()
        self.wall_slider.set_digits(0)
        self.wall_slider.set_range(0, MAX_GRID_SIZE * 2)
        self.wall_slider.set_draw_value(True)
        self.wall_slider.set_value(NUM_WALLS)
        self.wall_slider.connect("value-changed", self.slider_changed_wall)
        box.append(self.wall_slider)

    def slider_changed_wall(self, slider):
        self._num_walls = int(slider.get_value())

    def create_game_mode(self, box):
        self.create_option_label(box, "Game Mode:")
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        self.btn_normal = Gtk.CheckButton(label="Normal")
        self.btn_blitz = Gtk.CheckButton(label="Blitz")

        self.btn_normal.set_active(True)  # Normal mode by default
        self.btn_blitz.set_group(self.btn_normal)

        self.btn_normal.connect(
            "toggled", self.on_game_mode_button_toggled, GameMode.NORMAL
        )

        # blitz & timer box
        self.timer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.btn_blitz.connect(
            "toggled", self.on_game_mode_button_toggled, GameMode.BLITZ
        )
        self.timer_text_box = Gtk.SpinButton()
        adjustment = Gtk.Adjustment()
        adjustment.set_properties(
            value=0,
            lower=1,
            upper=60,
            step_increment=1,
            page_increment=5,
        )
        self.timer_text_box.set_adjustment(adjustment)
        self.timer_text_box.set_value(self._blitz_time or BLITZ_TIME)
        self.timer_text_box.set_size_request(20, -1)
        self.timer_text_box.set_hexpand(True)
        self.timer_box.append(self.btn_blitz)
        self.timer_box.append(self.timer_text_box)

        hbox.append(self.btn_normal)
        hbox.append(self.timer_box)

        box.append(hbox)

    def create_ai_switch(self, box):
        self.create_option_label(box, "AI Mode:")
        switch_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        self.switch_ai = Gtk.Switch()
        self.switch_ai.set_active(False)
        self.switch_ai.connect("state-set", self.on_ai_switch_switched)

        switch_box.append(self.switch_ai)
        box.append(switch_box)

        self.create_on_off_ai_players_buttons(box)
        self.create_ai_hidden_radio_buttons(box)

    def create_start_button(self, box):
        btn_start = Gtk.Button(label="Start")
        btn_start.set_size_request(20, 10)
        btn_start.set_halign(Gtk.Align.START)
        btn_start.connect("clicked", self.on_start_game_clicked)
        box.append(btn_start)

    def create_option_label(self, box, text):
        label = Gtk.Label(label=text)
        label.get_style_context().add_class("big-red")
        label.set_halign(Gtk.Align.START)
        box.append(label)

    def create_ai_hidden_radio_buttons(self, box):
        self.btn_ai_easy = Gtk.CheckButton(label="Easy (default)")
        self.btn_ai_easy.connect("toggled", self.on_button_ai_difficulty, "easy")
        self.btn_ai_medium = Gtk.CheckButton(label="Medium")
        self.btn_ai_medium.connect("toggled", self.on_button_ai_difficulty, "normal")
        self.btn_ai_hard = Gtk.CheckButton(label="Hard")
        self.btn_ai_hard.connect("toggled", self.on_button_ai_difficulty, "hard")

        self.btn_ai_easy.set_active(True)

        self.btn_ai_medium.set_group(self.btn_ai_easy)
        self.btn_ai_hard.set_group(self.btn_ai_medium)

        self.ai_option = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.depth_slider = Gtk.Scale()
        self.depth_slider.set_digits(0)
        self.depth_slider.set_range(1, 3)
        self.depth_slider.set_draw_value(True)
        self.depth_slider.set_value(1)
        self.depth_slider.connect("value-changed", self.slider_changed_depth)
        self.ai_option.append(self.depth_slider)

        self.radio_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.radio_box.append(self.btn_ai_easy)
        self.radio_box.append(self.btn_ai_medium)
        self.radio_box.append(self.btn_ai_hard)

        self.radio_box.append(self.ai_option)
        self.radio_box.set_visible(False)  # Hide by default
        box.append(self.radio_box)

    def slider_changed_depth(self, slider):
        self._ai_depth = int(slider.get_value())

    def on_button_ai_difficulty(self, button, mode):
        if mode == "easy":
            self._ai_mode = AiMode.MINIMAX
            self._ai_depth = 1
            self._ai_heuristic = AiHeuristic.RUNNER
        elif mode == "normal":
            self._ai_mode = AiMode.MINIMAX
            self._ai_depth = 1
            self._ai_heuristic = AiHeuristic.AGGRESSIVE
        elif mode == "hard":
            self._ai_mode = AiMode.MINIMAX
            self._ai_depth = 1
            self._ai_heuristic = AiHeuristic.DEFAULT

    def create_on_off_ai_players_buttons(self, box):
        self.player_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        label = Gtk.Label(label="AI player : ")
        label.get_style_context().add_class("big-red")
        self.player_box.append(label)

        self.ai_player_buttons = []

        for i in range(4):
            button = Gtk.ToggleButton(label=f"AI {i+1}")
            button.get_style_context().add_class("on-off-button")

            def on_toggle(btn, i=i + 1):
                btn.set_label(f"AI {i}" if btn.get_active() else f"AI {i}")
                if btn.get_active():
                    self._ai_ids.add(i - 1)
                else:
                    self._ai_ids.remove(i - 1)

            button.connect("toggled", on_toggle)
            self.ai_player_buttons.append(button)
            self.player_box.append(button)

        self.player_box.set_visible(False)  # Hide by default
        box.append(self.player_box)

    def on_new_game_clicked(self, button):
        self.stack.set_visible_child_name("new_game")

    def on_about_clicked(self, button):
        self.stack.set_visible_child_name("about")

    def clear_board_gui(self):
        if self.state is not None:
            for row in range(self.state.size):
                for col in range(self.state.size):
                    if (row, col) in self.cells:
                        self.game_grid.remove(self.cells[(row, col)])
        self.cells = {}
        self.clear_all_timer()

    def on_back_home(self, button):
        self.clear_board_gui()
        if self.state is not None:
            self.state.history.clear()
            self.state.redo_stack.clear()
            self.state.current_player.is_dead = True
        self.scrolled_window_history.set_child(None)
        self.game_is_over = True
        self.stack.set_visible_child_name("home")

    def on_quit_game_and_save(self, button):
        popup = SavePopup(self.state)
        popup.connect("close-request", self.on_popup_closed)
        popup.show()

    def on_save_history(self, button):
        SaveCommand(self.state, "outputHistory.txt").execute()
        pass

    def on_popup_closed(self, window):
        self.on_back_home(None)
        return False

    def on_restart_clicked(self, button):
        self.state = GameState()
        self.execute_command(RestartCommand(self.state, self.initial_state))
        self.clear_board_gui()
        if self.state.game_mode == GameMode.BLITZ:
            self.initialise_timer()
            self.state.current_player.timer.start_turn()
            self.state.current_player.timer.display_lock.set()
        self.create_board()
        self.render_board()
        self.handle_ai_player()
        self.game_is_over = False
        self.stack.set_visible_child_name("running_game")

    def on_player_button_toggled(self, button, players):
        if button.get_active():
            self._number_of_players = int(players)
            logging.debug(f"Number of players selected: {self._number_of_players}")

    def on_game_mode_button_toggled(self, button, mode: GameMode):
        if button.get_active():
            self._game_mode = mode
            logging.debug(f"Playing in {mode.display_name} Mode")
            if mode == GameMode.BLITZ:
                self.timer_text_box.set_visible(True)
            else:
                self.timer_text_box.set_visible(False)

    def on_ai_switch_switched(self, switch, state):
        logging.debug(f"The switch has been switched {'on' if state else 'off'}")
        if state:
            self.radio_box.set_visible(True)
            self.player_box.set_visible(True)
        else:
            self.btn_ai_easy.set_active(True)
            self.radio_box.set_visible(False)
            self.player_box.set_visible(False)

    ### Loading game
    def on_load_game_clicked(self, button):
        self.open_dialog.show()

    def open_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            filename = file.get_path()
            logging.debug(f"Loading gamestate from {filename}")
            file_state = None
            with open(filename, "r", encoding="utf-8") as file:
                file_state = parse_string_to_state(file)
            self.load_game_from_file(file_state)

    def load_game_from_file(self, state: GameState):
        if state is None:
            return False
        self.set_parameters(state)
        print(f"Loading Game from File . . .")
        self.state = state
        self.initial_state = self.state.copy_state()
        self.stack.set_visible_child_name("running_game")
        self.initialize_begining_game()
        
    ### --- Loading Game

    def manage_ai_parameters(self):
        """manage AI parameters, override -p option in case of conflict with -a"""
        current_ai_color = DEFAULT_AI_COLOR_ID
        ai_ids = set()
        if len(self._ai_ids) > 0:
            for ai in self._ai_ids:
                if ai is True:
                    ai_ids.add(current_ai_color - 1)
                    current_ai_color += 1
                elif ai == "A":
                    ai_ids = {0, 1, 2, 3}
                    break
                else:
                    color = int(ai)
                    if color != 1 and color not in ai_ids:
                        current_ai_color += 1
                    ai_ids.add(color)

        if (
            (self._number_of_players is not None)
            and (len(self._ai_ids) > 0)
            and len(ai_ids) > 0
        ):
            if self._number_of_players < max(len(ai_ids), max(ai_ids) + 1):
                logging.warning(
                    "Warning: -p option ignored due to presence of -a options"
                )
                self._number_of_players = max(
                    DEFAULT_AI_COLOR_ID, max(len(ai_ids), max(ai_ids) + 1)
                )
        elif len(self._ai_ids) > 0 and len(ai_ids) > 0:
            self._number_of_players = max(
                DEFAULT_AI_COLOR_ID, max(len(ai_ids), max(ai_ids) + 1)
            )

        self._ai_ids = ai_ids
        logging.debug(f"setup ai : {self._ai_ids}")

    def clear_box(self, box):
        child = box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            box.remove(child)
            child = next_child

    def create_box_players(self, box):
        self.clear_box(box)
        for player in self.state.players:
            emoji = "🔵"
            if player.id == 1:
                emoji = "🔴"
            elif player.id == 2:
                emoji = "🟢"
            elif player.id == 3:
                emoji = "🟡"
            is_ai = ""
            if player.id in self.state.ai_controllers:
                is_ai = "AI "
            walls = ""
            if not player.is_dead:
                walls = f" : walls remaining = {player.walls_remaining}"
            label = Gtk.Label(label=f"{is_ai}Player {player.id} {emoji} {walls}")
            label.get_style_context().add_class("player")
            if player.is_dead:
                label.get_style_context().add_class("player-is-dead")
            box.append(label)

    def on_start_game_clicked(self, button):
        self.stack.set_visible_child_name("running_game")
        self.game_is_over = False
        if self._game_mode == GameMode.BLITZ:
            self._blitz_time = self.timer_text_box.get_value_as_int()
            logging.debug("Temps sélectionné :", self._blitz_time)

        if not self.switch_ai.get_active():
            self._ai_ids = set()
        else:
            if len(self._ai_ids) <= 0:
                self._ai_ids.add(True)
            self.manage_ai_parameters()

        self.initialize_state(
            num_players=self._number_of_players,
            size=self._board_size,
            num_walls=self._num_walls,
            game_mode=self._game_mode,
            blitz_time=self._blitz_time,
            ai_ids=self._ai_ids,
            history=self._history,
            ai_mode=self._ai_mode,
            ai_depth=self._ai_depth,
            # todo heuristic
        )
        self.initialize_begining_game()

    def initialize_begining_game(self):
        if self.state.game_mode == GameMode.BLITZ:
            self.initialise_timer()
            self.state.current_player.timer.start_turn()
            self.state.current_player.timer.display_lock.set()
        self.create_box_players(self.game_players_box)
        self.create_board()
        self.render_board()
        self.handle_ai_player()

    def initialize_state(self, **kwargs):
        filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        self.state = GameState(**filtered_kwargs)
        self.initial_state = self.state.copy_state()

    def on_abandon_game(self, button):
        self.execute_command(AbandonCommand(self.state, self.state.current_player.id))
        if not self.state.game_over():
            self.update_players_box()
            self.update_current_player_label()

    def on_hint_clicked(self, button):
        self.hint_cases.clear()
        if self.hint_activate:
            self.hint_activate = False
        else:
            self.hint_activate = True

        ai_temp = GreedyAI(0, AiHeuristic.RUNNER)
        for case in ai_temp.possible_moves(self.state):
            self.hint_cases.append(case)
            self.draw_hint_on_case(case)

    def draw_hint_on_case(self, case):
        self.cells[case].set_label(self.hint_symbole)

    def display_pass_button(self):
        self.btn_pass_turn.set_visible(True)

    def remove_pass_button(self):
        self.btn_pass_turn.set_visible(False)

    def on_pass_turn(self, button):
        self.remove_pass_button()
        self.execute_command(PassCommand(self.state))

    def create_board(self):
        """Create a self.board_size by self.board_size game board with self.num_players pawns"""
        self.cells = {}

        for row in range(self.state.size):
            for col in range(self.state.size):
                cell = Gtk.Button(label="")
                cell.set_size_request(40, 40)
                self.game_grid.attach(cell, col, row, 1, 1)

                drop_target = Gtk.DropTarget.new(GObject.TYPE_NONE, Gdk.DragAction.MOVE)
                drop_target.set_gtypes([GObject.TYPE_STRING, GObject.TYPE_PYOBJECT])

                drop_target.connect("drop", self.on_drop)
                cell.add_controller(drop_target)

                self.cells[(row, col)] = cell

        for i in range(self.state.num_players):
            player = "winning_pos_player_blue"
            if i == 1:
                player = "winning_pos_player_red"
            elif i == 2:
                player = "winning_pos_player_green"
            elif i == 3:
                player = "winning_pos_player_yellow"
            for j in range(self.state.size):
                win = self.state.players[i].goal_line[j]
                cell = self.cells[(win[0], win[1])]
                cell.get_style_context().add_class(player)

                if player == "winning_pos_player_green" and j == 0:
                    cell.get_style_context().add_class("corner-bl")
                if player == "winning_pos_player_green" and j == self.state.size - 1:
                    cell.get_style_context().add_class("corner-br")

                if player == "winning_pos_player_yellow" and j == 0:
                    cell.get_style_context().add_class("corner-tl")
                if player == "winning_pos_player_yellow" and j == self.state.size - 1:
                    cell.get_style_context().add_class("corner-tr")

        # adding pawns
        self.blue_pos = self.state.players[0].position
        self.red_pos = self.state.players[1].position

        self.create_draggable_pawn(self.blue_pos, "🔵")
        self.create_draggable_pawn(self.red_pos, "🔴")
        if self._number_of_players is not None:
            if self._number_of_players > 2:
                self.green_pos = self.state.players[2].position
                self.create_draggable_pawn(self.green_pos, "🟢")
            if self._number_of_players > 3:
                self.yellow_pos = self.state.players[3].position
                self.create_draggable_pawn(self.yellow_pos, "🟡")

        # adding walls
        self.create_draggable_wall(self.horizontal_wall, Direction.H)
        self.create_draggable_wall(self.vertical_wall, Direction.V)

    def create_draggable_pawn(self, pos, emoji):
        """Adding a pawn with Drag n Drop action"""
        row, col = pos
        button = self.cells[(row, col)]
        button.set_label(emoji)

        drag_source = Gtk.DragSource.new()
        drag_source.set_actions(Gdk.DragAction.MOVE)
        drag_source.connect("prepare", self.on_drag_prepare, emoji, (row, col))
        button.add_controller(drag_source)

    def create_draggable_wall(self, button, wall_type):
        """Adding a wall with Drag n Drop action"""
        drag_source = Gtk.DragSource.new()
        drag_source.set_actions(Gdk.DragAction.MOVE)
        drag_source.connect("prepare", self.on_drag_prepare, wall_type)
        button.add_controller(drag_source)

    def on_drag_prepare(self, drag_source, x, y, emoji, pos=None):
        """Prepares the piece for dragging by storing its last position."""
        data = Gdk.ContentProvider.new_for_value(emoji)
        if emoji == "🔵":
            self.blue_last_pos = pos
        elif emoji == "🔴":
            self.red_last_pos = pos
        elif emoji == "🟢":
            self.green_last_pos = pos
        elif emoji == "🟡":
            self.yellow_last_pos = pos
        return data

    def on_drop(self, drop_target, value, x, y):
        """Handles dropping the piece and updates the board."""
        cell = drop_target.get_widget()

        row, col = None, None
        for (r, c), button in self.cells.items():
            if button == cell:
                row, col = r, c
                break

        if row is None or col is None:
            logging.debug("Error : no cell found in the grid")

        if value in ["🔵", "🔴", "🟢", "🟡"]:
            self.handle_pawn_move(row, col, value)

        elif value in [Direction.H, Direction.V]:
            self.handle_place_wall(row, col, value)

        return True

    def initialise_timer(self):
        for player in self.state.players:
            player.timer.set_gui_observer(self)

    def update_timer(self, time: int, player_id: int):
        self.timer_label.set_text(f"Timer : {time}")
        logging.debug(f"Timer : {time} {player_id}")

    def handle_timer_end_for_player(self, player_id: int):
        "handle 3 players"
        if self.state.num_players_remaining >= 3:
            self.execute_command(AbandonCommand(self.state, player_id))
            self.state.current_player.timer.start_turn()
            self.state.current_player.timer.display_lock.set()
            self.update_players_box()
            self.update_current_player_label()
        else:
            self.execute_command(AbandonCommand(self.state, player_id))
            self.state.switch_player()
            self.display_game_over_window()

    def handle_ai_player(self):
        if self.game_is_over:
            pass
        elif self.state.current_player.id in self.state.ai_controllers:
            if self.state.check_pass_player(self.state.current_player.id):
                command = PassCommand(self.state)
            else:
                command = self.state.ai_controllers[
                    self.state.current_player.id
                ].suggest_move(self.state)
            # Exécute la commande après 0,3 seconde
            GLib.timeout_add(300, lambda: self.execute_command(command))

            # Met à jour le plateau après 0,4 secondes
            GLib.timeout_add(400, lambda: self.render_board() or False)
        else:
            pass

    def handle_pass_player(self):
        if self.state.check_pass_player(self.state.current_player.id):
            self.display_pass_button()
        else:
            self.remove_pass_button()

    def handle_switch_player(self):
        logging.debug(f"Switching player : {self.state.current_player.id} ")
        if self.state.game_mode == GameMode.BLITZ:
            logging.debug(f"End timer for player : {self.state.current_player.id} ")
            logging.debug(f"with  : {self.state.current_player.timer.current_time} ")
            self.state.current_player.timer.end_turn()
            self.state.current_player.timer.display_lock.clear()

        self.state.switch_player()

        logging.debug(f"Switch player : {self.state.current_player.id} ")
        if self.state.game_mode == GameMode.BLITZ:
            logging.debug(f"Begin timer for player : {self.state.current_player.id} ")
            logging.debug(f"with  : {self.state.current_player.timer.current_time} ")
            self.state.current_player.timer.start_turn()
            self.state.current_player.timer.display_lock.set()

        self.remove_pass_button()
        if self.state.current_player.id in self.state.ai_controllers:
            self.handle_ai_player()
        else:
            self.handle_pass_player()

    def handle_pawn_move(self, row: int, col: int, player_id):
        """Manages pawn movement"""
        pawn_positions = {
            "🔵": "blue_last_pos",
            "🔴": "red_last_pos",
            "🟢": "green_last_pos",
            "🟡": "yellow_last_pos",
        }

        last_pos_attr = pawn_positions.get(player_id)
        if not last_pos_attr:
            logging.debug("Error: pawn not recognised")
            return

        last_pos = getattr(self, last_pos_attr, None)
        if not last_pos:
            logging.debug("Error: last position not found")
            return

        logging.debug(f"Moving pawn to : ({row}, {col})")

        last_row, last_col = last_pos
        try:
            move_pawn = MovePawnCommand(self.state, (last_row, last_col), (row, col))
            self.execute_command(move_pawn)
        except InvalidMoveError as e:
            logging.debug(f"Error : {InvalidMoveError.__name__} {e}")

    def handle_place_wall(self, row, col, wall_type: Direction):
        """Manages wall placement"""
        logging.debug(f"Placing a wall {wall_type} in ({row}, {col})")

        try:
            place_wall = PlaceWallCommand(self.state, (row, col), wall_type)
            self.execute_command(place_wall)
        except InvalidMoveError as e:
            logging.debug(f"Error : {InvalidMoveError.__name__} {e}")

    def display_game_over_window(self):
        self.clear_all_timer()
        id_player = self.state.current_player.id
        emoji = "🔵"
        if id_player == 1:
            emoji = "🔴"
        elif id_player == 2:
            emoji = "🟢"
        elif id_player == 3:
            emoji = "🟡"
        self.winner_label.set_markup(
            f'<span size="14000" weight="bold">{emoji} won!</span>'
        )
        self.stack.set_visible_child_name("end")

    def render_board(self):
        # clear label in self.cells
        for row in range(self.state.size):
            for col in range(self.state.size):
                button = self.cells[(row, col)]
                button.set_label("")
                button.get_style_context().remove_class("wall-h")
                button.get_style_context().remove_class("wall-v")

        for i in range(self.state.num_players):
            emoji = "🔵"
            if i == 1:
                emoji = "🔴"
            elif i == 2:
                emoji = "🟢"
            elif i == 3:
                emoji = "🟡"

            position_player = self.state.players[i].position
            self.cells[(position_player[0], position_player[1])].set_label(emoji)
            self.create_draggable_pawn((position_player[0], position_player[1]), emoji)

        for row in range(self.state.size - 1):
            for col in range(self.state.size - 1):
                if self.state.wall_exist(row, col, Direction.H):
                    self.cells[(row, col)].get_style_context().add_class("wall-h")
                    self.cells[(row, col + 1)].get_style_context().add_class("wall-h")
                elif self.state.wall_exist(row, col, Direction.V):
                    self.cells[(row, col)].get_style_context().add_class("wall-v")
                    self.cells[(row + 1, col)].get_style_context().add_class("wall-v")
        return

    def update_current_player_label(self):
        id_player = self.state.current_player.id
        emoji = "🔵"
        if id_player == 1:
            emoji = "🔴"
        elif id_player == 2:
            emoji = "🟢"
        elif id_player == 3:
            emoji = "🟡"
        self.current_player_label.set_label(f"Current player : {emoji}")
        logging.debug(f"Player {emoji} {id_player} must play")

    def update_players_box(self):
        self.create_box_players(self.game_players_box)
        self.update_scrolled_window_history()

    def update_scrolled_window_history(self):
        # Boîte pour le texte
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        text_box.set_size_request(300, -1)
        text_box.set_vexpand(True)
        text_list = []

        from quoridor.io import ReadWriteHistory

        history = ReadWriteHistory.parse_history_to_list_of_str(
            self.state.history, self.state
        )
        for turn_index, turn in enumerate(history, start=1):
            line = ""
            line += f"Turn {turn_index}: "
            for move in turn:
                line += move + " "
            text_list.append(line)

        # Ajouter chaque ligne de texte sous forme de label
        for line in text_list:
            label = Gtk.Label(label=line)
            label.set_xalign(0)  # Alignement à gauche
            text_box.append(label)

        self.scrolled_window_history.set_child(text_box)

    def set_parameters(self, state: GameState):
        self._number_of_players = state.num_players
        self._board_size = state.size
        self._num_walls = state.initial_num_walls
        self._game_mode = state.game_mode
        self._blitz_time = state.blitz_time
        self._ai_ids = state.ai_ids
        self._ai_depth = state.ai_depth
        self._ai_mode = state.ai_mode
        self._ai_heuristic = state.ai_heuristic

        self.btn_nb_players_2.set_active(False)
        self.btn_nb_players_3.set_active(False)
        self.btn_nb_players_4.set_active(False)
        if self._number_of_players == 2:
            self.btn_nb_players_2.set_active(True)
        elif self._number_of_players == 3:
            self.btn_nb_players_3.set_active(True)
        else:
            self.btn_nb_players_4.set_active(True)

        if self._board_size is not None:
            self.board_slider.set_value(self._board_size)

        if self._num_walls is not None:
            self.wall_slider.set_value(self._num_walls)

        self.btn_normal.set_active(False)
        self.btn_blitz.set_active(False)
        if self._game_mode is not None:
            if self._game_mode == GameMode.BLITZ:
                self.btn_blitz.set_active(True)
                self.timer_text_box.set_value(self._blitz_time or BLITZ_TIME)
            else:
                self.btn_normal.set_active(True)
        else:
            self.btn_normal.set_active(True)

        if len(self._ai_ids) > 0:
            self.switch_ai.set_active(True)
            self.manage_ai_parameters()
            for i, button in enumerate(self.ai_player_buttons):
                button.set_active(i in self._ai_ids)
        else:
            self.switch_ai.set_active(False)

    def load_game_from_history(self, state: GameState):
        self._history = state.history
        if self._history:
            logging.debug(f"Loading Game from History . . .")
            self.state = state
            self.initial_state = self.state.copy_state()
            self.stack.set_visible_child_name("running_game")
            self.initialize_begining_game()

    def execute_command(self, command: Command) -> bool:
        """
        Execute a command and add it to the command history.
        """
        try:
            logging.debug(f"command from {self.state.current_player.id}")
            result = command.execute()
            if result:
                self.state.history.append((self.state.current_player.id, command))
                self.state.redo_stack.clear()  # Clear redo stack when new command is executed

                if self.state.game_over():
                    logging.info("-------- GameOver --------")
                    if type(command) == AbandonCommand:
                        self.state.switch_player()
                    self.display_game_over_window()
                else:
                    self.handle_switch_player()
        except Exception as e:
            if self.state.current_player.id in self.state.ai_controllers:
                popup = AutoClosePopup(f"This AI try an \"Invalid Move\". To continue please play for him", self.popup_activated)
                popup.show()
                return False
            error_type = type(e).__name__
            logging.error(f"Error of type {error_type} while executing command: {e}")
            popup = AutoClosePopup(f"Error ({error_type}) : {e}", self.popup_activated)
            popup.show()

        self.handle_pass_player()
        self.update_players_box()
        self.update_current_player_label()
        self.render_board()

    def on_undo_clicked(self, button):
        self.execute_command(UndoCommand(self.state))

    def on_redo_clicked(self, button):
        self.execute_command(RedoCommand(self.state))

    def clear_all_timer(self):
        if self.state is not None:
            if self.state.game_mode == GameMode.BLITZ:
                for player in self.state.players:
                    if player.timer.turn_start_time is not None:
                        player.timer.end_turn()
                        player.timer.display_lock.clear()


class AutoClosePopup(Gtk.Window):
    def __init__(self, message, show):
        if show:
            super().__init__(title="Warning")
            self.set_default_size(200, 100)
            self.set_transient_for(None)
            self.set_modal(True)
            label = Gtk.Label(label=message)
            self.set_child(label)
            GLib.timeout_add(2500, self.destroy)

class SavePopup(Gtk.Window):
    def __init__(self, state: 'GameState'):
        super().__init__(title="Save and quit")
        self.set_default_size(200, 100)
        self.set_transient_for(None)
        self.set_modal(True)

        self.state = state

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin_top=10, margin_bottom=10, margin_start=10, margin_end=10)
        label = Gtk.Label(label="Do you want to save your game before quitting ?")
        vbox.append(label)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        yes_button = Gtk.Button(label="✅ Yes")
        no_button = Gtk.Button(label="❌ No")
        yes_button.connect("clicked", self.on_save_game_clicked)
        no_button.connect("clicked", lambda btn: self.close())

        button_box.append(yes_button)
        button_box.append(no_button)

        vbox.append(button_box)
        self.set_child(vbox)

        # Création de la boîte de dialogue de sélection de fichier
        self.open_dialog = Gtk.FileChooserNative.new(
            title="Select a file", parent=self, action=Gtk.FileChooserAction.SAVE
        )
        self.open_dialog.set_modal(True)

        file_filter = Gtk.FileFilter()
        file_filter.set_name("Quoridor game file")
        file_filter.add_mime_type("text/plain")
        self.open_dialog.set_filter(file_filter)

        self.open_dialog.connect("response", self.open_response)

    def on_save_game_clicked(self, button):
        self.open_dialog.show()

    def open_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            filename = file.get_path()
            logging.debug(f"Save gamestate in {filename}")
            try:
                SaveAndQuitCommand(self.state, filename).execute()
            except QuitApp:
                pass
        self.close()

class MyApplication(Gtk.Application):
    def __init__(self, state: GameState, **kwargs):
        super().__init__(**kwargs)
        self.load_from_file = False
        self.load_from_history = False
        self.connect("activate", self.on_activate)

        from pathlib import Path

        current_dir = Path(__file__).resolve().parent
        path_to_style_css = current_dir / "../quoridor/style.css"

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(path_to_style_css.as_posix())

        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )
        self.state = state

    def on_activate(self, app):
        self.window = MainWindow(application=app, title="Quoridor.py")
        self.window.connect("close-request", self.on_close_request)
        self.window.present()
        if self.state is not None:
            if self.load_from_file:
                self.window.load_game_from_file(self.state)
            else:
                self.window.set_parameters(self.state)
                if self.load_from_history:
                    self.window.load_game_from_history(self.state)
                else:
                    self.window.on_new_game_clicked(None)

    def load_game_from_file(self):
        self.load_from_file = True

    def load_game_from_history(self):
        self.load_from_history = True

    def on_close_request(self, window):
        logging.debug("Window closing")
        self.window.clear_all_timer()
        return False


class GUIEngine:
    def __init__(self, state: GameState):
        self.app = MyApplication(
            state=state,
            application_id="quoridor.py",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )

    def run(self):
        """"""
        self.app.run(None)

    def load_game_from_file(self):
        self.app.load_game_from_file()

    def load_game_from_history(self):
        self.app.load_game_from_history()

    def render_board(self):
        """update board"""
        self.app.window.render_board()
