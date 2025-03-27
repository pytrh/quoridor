import copy
import logging
import gi

from quoridor.command import (
    Command,
    PlaceWallCommand,
    MovePawnCommand,
    UndoCommand,
    RedoCommand,
    RestartCommand,
    QuitCommand,
    AbandonCommand,
)
from quoridor.direction import Direction
from quoridor.exceptions import InvalidMoveError
from quoridor.gamemode import GameMode
from quoridor.gamestate import GameState
from quoridor.observer import Observer

from quoridor.config import (
    DEFAULT_BLITZ_TIME,
    MIN_GRID_SIZE,
    MAX_GRID_SIZE,
    DEFAULT_NUM_WALLS,
)


gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, Gio, GLib, GObject


class MainWindow(Gtk.ApplicationWindow, Observer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(600, 400)

        self.state = None
        self.initial_state = None
        self._number_of_players = None
        self._board_size = None
        self._num_walls = None

        self._blitz_mode = None
        self._blitz_time = None
        self._ai_mode = None
        self._ai_colors = None

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

        # Crée une boîte de dialogue pour ouvrir un fichier
        self.open_dialog = Gtk.FileChooserNative.new(
            title="Select a file", parent=self, action=Gtk.FileChooserAction.OPEN
        )
        self.open_dialog.set_modal(True)

        f = Gtk.FileFilter()
        f.set_name("Quoridor game file")
        f.add_mime_type("image/jpeg")
        f.add_mime_type("image/png")

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
        box.set_halign(Gtk.Align.START)
        box.set_valign(Gtk.Align.START)

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
        main_box.append(left_box)

        restart_button = Gtk.Button(label="🔄 Restart")
        restart_button.connect("clicked", self.on_restart_clicked)

        download_button = Gtk.Button(label="📥 Save")

        power_button = Gtk.Button(label="🚪 Quit")
        power_button.set_size_request(20, 10)
        power_button.set_halign(Gtk.Align.START)
        power_button.connect("clicked", self.on_back_home)

        left_box.append(restart_button)
        left_box.append(download_button)
        left_box.append(power_button)

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
        main_box.append(game_box)

        # Right column (Chrono and arrows undo / redo)
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.append(right_box)

        self.timer_label = Gtk.Label(label="00:00")
        right_box.append(self.timer_label)

        arrow_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        right_box.append(arrow_box)

        left_arrow = Gtk.Button(label="⬅ Undo")
        right_arrow = Gtk.Button(label="Redo ➡")
        arrow_box.append(left_arrow)
        arrow_box.append(right_arrow)

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
        info = """<span size="12000" weight="bold">Version:</span> <span size="12000">0.2.0</span>
                <span size="12000" weight="bold">Developers:</span> <span size="12000">Mohamad Almousa, Lucy Curtis, Lucas Danglard, Bastien Rocher, Zhaoyuan Song</span>
                <span size="12000" weight="bold">Expected release date:</span> <span size="12000">April 2025</span>
                <span size="12000" weight="bold">Description:</span> 
                <span size="10000">QUORIDOR is a two, three (although not recommended) or four-player intuitive strategy game. 
                    The aim of the game is to reach the opposite side of the grid before the other players. While simultaniously navigating through walls placed by players.</span>
                """

        label = Gtk.Label()
        label.set_markup(info)
        label.set_justify(Gtk.Justification.CENTER)
        label.set_halign(Gtk.Align.CENTER)
        label.set_wrap(True)
        box.append(label)

        return box

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

        home_button = Gtk.Button(label="Go Home")
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
        self.board_slider.set_value(9)
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
        self.wall_slider.set_value(DEFAULT_NUM_WALLS)
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
        self.timer_text_box.set_value(self._blitz_time or DEFAULT_BLITZ_TIME)
        self.timer_text_box.set_size_request(20, -1)
        self.timer_text_box.set_hexpand(True)
        self.timer_box.append(self.btn_blitz)
        self.timer_box.append(self.timer_text_box)

        hbox.append(self.btn_normal)
        hbox.append(self.timer_box)

        box.append(hbox)

    def create_ai_switch(self, box):
        self.create_option_label(box, "AI Mode:")
        switch_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.switch_ai = Gtk.Switch()
        self.switch_ai.set_active(False)
        self.switch_ai.connect("state-set", self.on_ai_switch_switched)

        switch_box.append(self.switch_ai)
        box.append(switch_box)

        self.create_ai_hidden_radio_buttons(box)

    def create_start_button(self, box):
        btn_start = Gtk.Button(label="Start")
        btn_start.set_size_request(20, 10)
        btn_start.set_halign(Gtk.Align.START)
        btn_start.connect("clicked", self.on_start_game_clicked)
        box.append(btn_start)

    def create_option_label(self, box, text):
        label = Gtk.Label()
        # TODO: variable "dark red"
        label.set_markup(
            f'<span foreground="#8B0000" font_desc="14pt bold">{text}</span>'
        )
        label.set_halign(Gtk.Align.START)
        box.append(label)

    def create_ai_hidden_radio_buttons(self, box):
        self.btn_ai_easy = Gtk.CheckButton(label="Easy")
        self.btn_ai_medium = Gtk.CheckButton(label="Medium")
        self.btn_ai_hard = Gtk.CheckButton(label="Hard")

        self.btn_ai_easy.set_active(True)

        self.btn_ai_medium.set_group(self.btn_ai_easy)
        self.btn_ai_hard.set_group(self.btn_ai_medium)

        self.radio_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.radio_box.append(self.btn_ai_easy)
        self.radio_box.append(self.btn_ai_medium)
        self.radio_box.append(self.btn_ai_hard)

        self.radio_box.set_visible(False)  # Hide by default
        box.append(self.radio_box)

    def on_new_game_clicked(self, button):
        self.stack.set_visible_child_name("new_game")

    def on_about_clicked(self, button):
        self.stack.set_visible_child_name("about")

    def on_back_home(self, button):
        if self.state is not None:
            for row in range(self.state.size):
                for col in range(self.state.size):
                    if (row, col) in self.cells:
                        self.game_grid.remove(self.cells[(row, col)])
        self.cells = {}
        self.clear_all_timer()
        self.state = None
        self.stack.set_visible_child_name("home")
        logging.debug("Button was clicked")

    def on_restart_clicked(self, button):  # TODO dupplicate code
        for row in range(self.state.size):
            for col in range(self.state.size):
                if (row, col) in self.cells:
                    self.game_grid.remove(self.cells[(row, col)])
        self.cells = {}
        self.clear_all_timer()
        self.state = None

        self.on_start_game_clicked("clicked")

    def on_load_game_clicked(self, button):
        self.open_dialog.show()

    def on_player_button_toggled(self, button, players):
        if button.get_active():
            self._number_of_players = int(players)
            logging.debug(f"Number of players selected: {self._number_of_players}")

    def on_game_mode_button_toggled(self, button, mode: GameMode):
        if button.get_active():
            self._blitz_mode = mode
            logging.debug(f"Playing in {mode.display_name} Mode")
            if mode == GameMode.BLITZ:
                self.timer_text_box.set_visible(True)
            else:
                self.timer_text_box.set_visible(False)

    def on_ai_switch_switched(self, switch, state):
        logging.debug(f"The switch has been switched {'on' if state else 'off'}")
        if state:
            self.radio_box.set_visible(True)
        else:
            self.btn_ai_easy.set_active(True)
            self.radio_box.set_visible(False)

    def open_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            filename = file.get_path()
            logging.debug(filename)

    def on_start_game_clicked(self, button):
        self.stack.set_visible_child_name("running_game")
        if self._blitz_mode == GameMode.BLITZ:
            self._blitz_time = self.timer_text_box.get_value_as_int()
            logging.debug("Temps sélectionné :", self._blitz_time)

        self.initialize_state(
            num_players=self._number_of_players,
            size=self._board_size,
            num_walls=self._num_walls,
            blitz_mode=self._blitz_mode,
            blitz_time=self._blitz_time,
            # self._ai_mode
            # self._ai_colors
        )
        if self.state.blitz_mode == GameMode.BLITZ:
            self.initialise_timer()
            self.state.current_player.timer.start_turn()
            self.state.current_player.timer.display_lock.set()
        self.create_board()
        self.render_board()

    def initialize_state(self, **kwargs):
        filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        self.state = GameState(**filtered_kwargs)
        self.initial_state = self.state.copy_state()

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
        logging.debug(value)
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
            self.update_current_player_label()
        else:
            self.execute_command(AbandonCommand(self.state, player_id))
            self.display_game_over_window()

    def handle_switch_player(self):
        logging.debug(f"Switching player : {self.state.current_player.id} ")
        if self.state.blitz_mode == GameMode.BLITZ:
            logging.debug(f"End timer for player : {self.state.current_player.id} ")
            logging.debug(f"with  : {self.state.current_player.timer.current_time} ")
            self.state.current_player.timer.end_turn()
            self.state.current_player.timer.display_lock.clear()

        self.state.switch_player()

        logging.debug(f"Switch player : {self.state.current_player.id} ")
        if self.state.blitz_mode == GameMode.BLITZ:
            logging.debug(f"Begin timer for player : {self.state.current_player.id} ")
            logging.debug(f"with  : {self.state.current_player.timer.current_time} ")
            self.state.current_player.timer.start_turn()
            self.state.current_player.timer.display_lock.set()

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
            if self.state.game_over():
                logging.info("-------- GameOver --------")
                self.display_game_over_window()
            else:
                self.handle_switch_player()
            self.render_board()
        except InvalidMoveError as e:
            logging.debug(f"Error : {InvalidMoveError.__name__} {e}")

    def handle_place_wall(self, row, col, wall_type: Direction):
        """Manages wall placement"""
        logging.debug(f"Placing a wall {wall_type} in ({row}, {col})")

        try:
            place_wall = PlaceWallCommand(self.state, (row, col), wall_type)
            self.execute_command(place_wall)
            self.handle_switch_player()
            self.render_board()
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
        for row in range(self.state.size):
            for col in range(self.state.size):
                button = self.cells[(row, col)]
                button.set_label("")

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

        self.update_current_player_label()

        return

    def update_current_player_label(self):
        id_player = self.state.current_player.id
        logging.debug(f"id : {id_player}")
        emoji = "🔵"
        if id_player == 1:
            emoji = "🔴"
        elif id_player == 2:
            emoji = "🟢"
        elif id_player == 3:
            emoji = "🟡"
        self.current_player_label.set_label(f"Current player : {emoji}")

    def set_parameters(self, state: GameState):
        self._number_of_players = state.num_players
        self._board_size = state.size
        self._num_walls = state.initial_num_walls
        self._blitz_mode = state.blitz_mode
        self._blitz_time = state.blitz_time
        self._ai_mode = state.ai_mode
        # self._ai_colors

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
        if self._blitz_mode is not None:
            if self._blitz_mode == GameMode.BLITZ:
                self.btn_blitz.set_active(True)
            else:
                self.btn_normal.set_active(True)
        else:
            self.btn_normal.set_active(True)

        self.switch_ai.set_active(False)

    def execute_command(self, command: Command) -> bool:
        """
        Execute a command and add it to the command history.
        """
        result = command.execute()
        if result:
            self.state.history.append(command)
            self.state.redo_stack.clear()  # Clear redo stack when new command is executed
        return result

    def clear_all_timer(self):
        if self.state is not None:
            if self.state.blitz_mode == GameMode.BLITZ:
                for player in self.state.players:
                    if player.timer.turn_start_time is not None:
                        player.timer.end_turn()
                        player.timer.display_lock.clear()


class MyApplication(Gtk.Application):
    def __init__(self, state: GameState, **kwargs):
        super().__init__(**kwargs)
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
            self.window.set_parameters(self.state)
            self.window.on_new_game_clicked(None)

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

    def render_board(self):
        """update board"""
        self.app.window.render_board()
