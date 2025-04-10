import gi
import pytest


gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from quoridor.gamemode import AiHeuristic, GameMode
from quoridor.gamestate import GameState
from quoridor.guiengine import MainWindow, SavePopup
from unittest.mock import MagicMock


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

    # Nettoyage si le popup a été créé
    for window in Gtk.Window.list_toplevels():
        window.destroy()


def test_default_gui_use(main_window: MainWindow):
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

    # on_popup_closed -> go to Home
    main_window.on_popup_closed(None)
    visible_child = main_window.stack.get_visible_child_name()
    assert visible_child == "home", f"Expected 'about', got '{visible_child}'"

    # clear window
    for window in Gtk.Window.list_toplevels():
        window.destroy()
