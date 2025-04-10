import gi
import pytest


gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from quoridor.gamestate import GameState
from quoridor.guiengine import MainWindow
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
    main_window.create_about_page()
    box_temp = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    main_window.create_ai_hidden_radio_buttons(box_temp)
    main_window.create_ai_switch(box_temp)
