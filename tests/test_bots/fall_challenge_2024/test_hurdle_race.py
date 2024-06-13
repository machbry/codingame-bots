import pytest

from bots.summer_challenge_2024.challengelibs.actions import Action
from bots.summer_challenge_2024.challengelibs.mini_games import HurdleRace


@pytest.mark.parametrize("turn_input, player_idx, action, result_expected", [
    ("....#...#....#................ 2 0 0 0 0 0 0", 0, Action.UP, -4),
    ("....#...#....#................ 2 0 0 0 0 0 0", 0, Action.LEFT, 1),
    ("....#...#....#................ 2 0 0 0 0 0 0", 0, Action.DOWN, -4),
    ("....#...#....#................ 2 0 0 0 0 0 0", 0, Action.RIGHT, -4),
    ("....#...#....#................ 3 0 0 0 0 0 0", 0, Action.UP, 2),
    ("....#...#....#................ 3 0 0 0 0 0 0", 0, Action.LEFT, -5),
    ("....#...#....#................ 3 0 0 0 0 0 0", 0, Action.DOWN, -5),
    ("....#...#....#................ 3 0 0 0 0 0 0", 0, Action.RIGHT, -5),
    ("....#...#....#................ 4 0 0 0 0 0 0", 0, Action.UP, 2),
    ("....#...#....#................ 4 0 0 0 0 0 0", 0, Action.LEFT, 1),
    ("....#...#....#................ 4 0 0 0 0 0 0", 0, Action.DOWN, 2),
    ("....#...#....#................ 4 0 0 0 0 0 0", 0, Action.RIGHT, 3),
])
def test_evaluate_action(turn_input, player_idx, action, result_expected):
    mini_game = HurdleRace(inputs=turn_input.split(), player_idx=player_idx)

    result = mini_game.evaluate_action(action)

    assert result == result_expected
