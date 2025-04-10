import pytest
import time
import time as real_time
from unittest.mock import MagicMock, patch

from quoridor.timer import Timer
from quoridor.gamemode import GameMode


@pytest.fixture
def timer():
    timer = Timer(blitz_time=5, game_mode=GameMode.BLITZ, player_id=0)
    timer.display_lock.clear()
    return timer


def test_initial_time(timer):
    assert timer.get_time_remaining() == 5


def test_set_time_remaining(timer):
    timer.set_time_remaining(3)
    assert timer.get_time_remaining() == 3


def test_start_turn_resets_timer(timer):
    timer.set_time_remaining(2)
    timer.start_turn(reset_timer=True)
    assert timer.get_time_remaining() == 5
    assert timer.turn_start_time is not None
    timer.end_turn()


def test_start_turn_without_reset(timer):
    timer.set_time_remaining(3)
    timer.start_turn(reset_timer=False)
    assert timer.get_time_remaining() == 3
    assert timer.turn_start_time is not None
    timer.end_turn()


def test_end_turn_updates_time(timer):
    timer.start_turn(reset_timer=True)
    time.sleep(1)
    timer.end_turn()
    assert 3 <= timer.get_time_remaining() <= 4


def test_end_turn_no_crash_when_not_started(timer):
    timer.end_turn()
    assert timer.get_time_remaining() == 5
