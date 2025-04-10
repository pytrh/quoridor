import gi
import pytest


gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from quoridor.direction import Direction
from quoridor.exceptions import InvalidMoveError
from quoridor.gamemode import AiHeuristic, GameMode
from quoridor.gamestate import GameState
from quoridor.guiengine import MainWindow, SavePopup
from unittest.mock import MagicMock, patch


class FakeGtkApplication(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@pytest.fixture
def main_window():
    fake_app = FakeGtkApplication(application_id="quoridor.test")
    window = MainWindow(application=fake_app)
    return window


def test_update_timer(main_window: MainWindow):
    mock_time = 10
    mock_player_id = 1
    main_window.update_timer(mock_time, mock_player_id)
    assert main_window.timer_label.get_text() == f"Timer: {mock_time}"


def test_handle_timer_end_for_player(main_window: MainWindow):
    mock_player_id = 1
    main_window.set_parameters(GameState())
    main_window.initialize_state(
        num_players=main_window._number_of_players,
        size=main_window._board_size,
        num_walls=main_window._num_walls,
        game_mode=main_window._game_mode,
        blitz_time=main_window._blitz_time,
        ai_ids=main_window._ai_ids,
        history=main_window._history,
        ai_mode=main_window._ai_mode,
        ai_depth=main_window._ai_depth,
    )
    main_window.create_board()
    main_window.handle_timer_end_for_player(mock_player_id)


def test_on_quit_game_and_save_connects_signal(main_window: MainWindow, monkeypatch):
    connected_signals = []

    def fake_connect(self, signal_name, callback):
        connected_signals.append(signal_name)

    monkeypatch.setattr(SavePopup, "connect", fake_connect)
    monkeypatch.setattr(SavePopup, "show", lambda self: None)

    button = Gtk.Button()
    main_window.on_quit_game_and_save(button)

    assert "close-request" in connected_signals

    for window in Gtk.Window.list_toplevels():
        window.destroy()


def test_on_quit_game_and_save_connects_signal(main_window: MainWindow, monkeypatch):
    connected_signals = []

    def fake_connect(self, signal_name, callback):
        connected_signals.append(signal_name)

    monkeypatch.setattr(SavePopup, "connect", fake_connect)
    monkeypatch.setattr(SavePopup, "show", lambda self: None)

    button = Gtk.Button()
    main_window.on_quit_game_and_save(button)

    assert "close-request" in connected_signals

    for window in Gtk.Window.list_toplevels():
        window.destroy()


def test_on_drop_pawn(main_window):
    mock_cell = MagicMock()
    row, col = 2, 3
    main_window.cells = {(row, col): mock_cell}
    
    drop_target = MagicMock()
    drop_target.get_widget.return_value = mock_cell

    main_window.handle_pawn_move = MagicMock()

    result = main_window.on_drop(drop_target, "🔵", x=0, y=0)

    main_window.handle_pawn_move.assert_called_once_with(row, col, "🔵")
    assert result is True


def test_on_drop_wall(main_window):
    mock_cell = MagicMock()
    row, col = 1, 1
    main_window.cells = {(row, col): mock_cell}
    
    drop_target = MagicMock()
    drop_target.get_widget.return_value = mock_cell

    main_window.handle_place_wall = MagicMock()

    result = main_window.on_drop(drop_target, Direction.H, x=0, y=0)

    main_window.handle_place_wall.assert_called_once_with(row, col, Direction.H)
    assert result is True


def test_on_drop_unknown_cell(main_window, caplog):
    drop_target = MagicMock()
    drop_target.get_widget.return_value = MagicMock() 

    main_window.cells = {(0, 0): MagicMock()}

    with caplog.at_level("DEBUG"):
        result = main_window.on_drop(drop_target, "🔴", x=0, y=0)

    assert "no cell found" in caplog.text
    assert result is True


def test_on_click_valid_cell(main_window):
    mock_cell = MagicMock()
    row, col = 4, 5
    main_window.cells = {(row, col): mock_cell}

    click_target = MagicMock()
    click_target.get_widget.return_value = mock_cell

    main_window.handle_pawn_move_click = MagicMock()

    result = main_window.on_click(click_target, "🔵", x=0, y=0)

    main_window.handle_pawn_move_click.assert_called_once_with(row, col, "🔵")
    assert result is True


def test_on_click_invalid_cell(main_window, caplog):
    click_target = MagicMock()
    click_target.get_widget.return_value = MagicMock()

    main_window.cells = {(0, 0): MagicMock()} 

    main_window.handle_pawn_move_click = MagicMock()

    with caplog.at_level("DEBUG"):
        result = main_window.on_click(click_target, "🔴", x=0, y=0)

    main_window.handle_pawn_move_click.assert_called_once_with(None, None, "🔴")
    assert "no cell found" in caplog.text
    assert result is True


def test_default_gui_use(main_window: MainWindow):
    main_window.set_parameters(GameState(num_players=4))
    main_window.initialize_state(
        num_players=4,
        size=main_window._board_size,
        num_walls=main_window._num_walls,
        game_mode=main_window._game_mode,
        blitz_time=main_window._blitz_time,
        ai_ids=main_window._ai_ids,
        history=main_window._history,
        ai_mode=main_window._ai_mode,
        ai_depth=main_window._ai_depth,
    )
    box_temp = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    btn_temp = Gtk.Button(label=("test button"))
    label_temp = Gtk.Label(label=("test label"))

    slider_temp = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 5, 20, 1)
    slider_temp.set_value(10)

    # slider_changed_board( slider)
    main_window.slider_changed_board(slider_temp)
    final_value = int(slider_temp.get_value())
    assert final_value % 2 == 1, f"Expected odd value, got {final_value}"
    assert main_window._board_size == final_value
    slider_temp.set_value(9)
    main_window.slider_changed_board(slider_temp)
    final_value = int(slider_temp.get_value())
    assert final_value % 2 == 1, f"Expected odd value, got {final_value}"
    assert main_window._board_size == final_value

    # slider_changed_wall( slider)
    main_window.slider_changed_wall(slider_temp)
    final_value = int(slider_temp.get_value())
    assert main_window._num_walls == final_value

    # slider_changed_depth( slider)
    main_window.slider_changed_depth(slider_temp)
    final_value = int(slider_temp.get_value())
    assert main_window._ai_depth == final_value

    # on_button_ai_difficulty( button, mode)
    main_window.on_button_ai_difficulty(btn_temp, "easy")
    assert main_window._ai_heuristic == AiHeuristic.RUNNER
    main_window.on_button_ai_difficulty(btn_temp, "normal")
    assert main_window._ai_heuristic == AiHeuristic.AGGRESSIVE
    main_window.on_button_ai_difficulty(btn_temp, "hard")
    assert main_window._ai_heuristic == AiHeuristic.DEFAULT
    main_window.on_button_ai_difficulty(btn_temp, "wrong")
    assert main_window._ai_heuristic == AiHeuristic.RUNNER

    # on_new_game_clicked
    main_window.on_new_game_clicked(btn_temp)
    visible_child = main_window.stack.get_visible_child_name()
    assert visible_child == "new_game", f"Expected 'new_game', got '{visible_child}'"

    # on_about_clicked
    main_window.on_about_clicked(btn_temp)
    visible_child = main_window.stack.get_visible_child_name()
    assert visible_child == "about", f"Expected 'about', got '{visible_child}'"

    # on_start_game_clicked
    main_window.on_start_game_clicked(btn_temp)
    visible_child = main_window.stack.get_visible_child_name()
    assert (
        visible_child == "running_game"
    ), f"Expected 'running_game', got '{visible_child}'"

    # on_restart_clicked
    main_window.on_restart_clicked(btn_temp)
    visible_child = main_window.stack.get_visible_child_name()
    assert (
        visible_child == "running_game"
    ), f"Expected 'running_game', got '{visible_child}'"

    # on_back_home
    main_window.on_back_home(btn_temp)
    visible_child = main_window.stack.get_visible_child_name()
    assert visible_child == "home", f"Expected 'about', got '{visible_child}'"

    # on_save_history
    main_window.on_save_history(btn_temp)
    main_window.load_game_from_history(GameState())

    # on_popup_closed -> go to Home
    main_window.on_popup_closed(None)
    visible_child = main_window.stack.get_visible_child_name()
    assert visible_child == "home", f"Expected 'about', got '{visible_child}'"

    # on_ai_switch_switched
    state = GameState(num_players=4)
    main_window.on_ai_switch_switched(btn_temp, state)
    main_window.on_ai_switch_switched(btn_temp, None)

    # load_game_from_file
    main_window.load_game_from_file(state)
    main_window.load_game_from_file(None)

    # manage_ai_parameters
    main_window.manage_ai_parameters()
    assert main_window._ai_ids == set()
    main_window._ai_ids = {2}
    main_window.manage_ai_parameters()
    assert main_window._ai_ids == { 2 }

    # on_abandon_game
    main_window.on_abandon_game(btn_temp)

    # on_hint_clicked
    main_window.on_hint_clicked(btn_temp)
    main_window.hint_activate == True
    main_window.on_hint_clicked(btn_temp)

    # draw_hint_on_case
    main_window.draw_hint_on_case((0,0))

    # display_pass_button
    main_window.display_pass_button()

    # on_pass_turn
    main_window.on_pass_turn(btn_temp)

    # on_drag_prepare
    main_window.create_board()
    main_window.on_drag_prepare(None, 4, 0, '🔵')
    assert main_window.blue_pos == (4,0)
    main_window.on_drag_prepare(None, 4, 8, '🔴')
    assert main_window.red_pos == (4, 8)
    main_window.on_drag_prepare(None, 0, 4, '🟢')
    assert main_window.green_pos == (0, 4)
    main_window.on_drag_prepare(None, 8, 4, '🟡')
    assert main_window.yellow_pos == (8, 4)


    # clear window
    for window in Gtk.Window.list_toplevels():
        window.destroy()


def test_clear_all_timer_blitz(main_window):
    mock_timer = MagicMock()
    mock_timer.turn_start_time = 123456 
    mock_timer.display_lock = MagicMock()

    player1 = MagicMock()
    player1.timer = mock_timer

    player2 = MagicMock()
    player2.timer = mock_timer

    main_window.state = MagicMock()
    main_window.state.game_mode = GameMode.BLITZ
    main_window.state.players = [player1, player2]

    main_window.clear_all_timer()

    assert mock_timer.end_turn.call_count == 2
    assert mock_timer.display_lock.clear.call_count == 2


def test_handle_switch_player(main_window):
    timer1 = MagicMock()
    timer1.current_time = 120
    timer1.display_lock = MagicMock()

    timer2 = MagicMock()
    timer2.current_time = 150
    timer2.display_lock = MagicMock()

    player1 = MagicMock()
    player1.id = 1
    player1.timer = timer1

    player2 = MagicMock()
    player2.id = 2
    player2.timer = timer2

    state = MagicMock()
    state.game_mode = GameMode.BLITZ
    state.current_player = player1

    def fake_switch_player():
        state.current_player = player2

    state.switch_player.side_effect = fake_switch_player
    main_window.state = state

    main_window.handle_switch_player()

    timer1.end_turn.assert_called_once()
    timer1.display_lock.clear.assert_called_once()

    timer2.start_turn.assert_called_once()
    timer2.display_lock.set.assert_called_once()

def test_handle_pawn_move_click_valid(main_window):
    main_window.set_parameters(GameState(num_players=4))
    main_window.initialize_state(
        num_players=4,
        size=main_window._board_size,
        num_walls=main_window._num_walls,
        game_mode=main_window._game_mode,
        blitz_time=main_window._blitz_time,
        ai_ids=main_window._ai_ids,
        history=main_window._history,
        ai_mode=main_window._ai_mode,
        ai_depth=main_window._ai_depth,
    )
    main_window.create_board()
    main_window.state.current_player.position = (4, 0)
    main_window.handle_pawn_move_click(4, 1, player_id=0)
    assert main_window.state.players[0].position == (4,1)

def test_handle_pawn_move_click_invalid(main_window):
    main_window.set_parameters(GameState(num_players=4))
    main_window.initialize_state(
        num_players=4,
        size=main_window._board_size,
        num_walls=main_window._num_walls,
        game_mode=main_window._game_mode,
        blitz_time=main_window._blitz_time,
        ai_ids=main_window._ai_ids,
        history=main_window._history,
        ai_mode=main_window._ai_mode,
        ai_depth=main_window._ai_depth,
    )
    main_window.create_board()
    main_window.state.players[1].position = (4, 8)
    main_window.handle_pawn_move_click(0, 8, player_id=1)
    assert main_window.state.players[1].position == (4,8)

def test_handle_pawn_move_click_no_last_position(main_window, caplog):
    main_window.set_parameters(GameState(num_players=4))
    main_window.initialize_state(
        num_players=4,
        size=main_window._board_size,
        num_walls=main_window._num_walls,
        game_mode=main_window._game_mode,
        blitz_time=main_window._blitz_time,
        ai_ids=main_window._ai_ids,
        history=main_window._history,
        ai_mode=main_window._ai_mode,
        ai_depth=main_window._ai_depth,
    )
    main_window.state.current_player.position = None

    with caplog.at_level("DEBUG"):
        main_window.handle_pawn_move_click(4, 4, player_id=1)

    assert "Error: last position not found" in caplog.text

def test_handle_place_wall_valid(main_window):
    main_window.set_parameters(GameState(num_players=4))
    main_window.initialize_state(
        num_players=4,
        size=main_window._board_size,
        num_walls=main_window._num_walls,
        game_mode=main_window._game_mode,
        blitz_time=main_window._blitz_time,
        ai_ids=main_window._ai_ids,
        history=main_window._history,
        ai_mode=main_window._ai_mode,
        ai_depth=main_window._ai_depth,
    )
    main_window.create_board()
    main_window.handle_place_wall(3, 4, Direction.V)
    assert main_window.state.wall_exist(3, 4, Direction.V)
    main_window.handle_place_wall(2, 5, Direction.H)
    assert main_window.state.wall_exist(2, 5, Direction.H)

    main_window.handle_place_wall(3, 4, Direction.H)
    assert not main_window.state.wall_exist(3, 4, Direction.H)