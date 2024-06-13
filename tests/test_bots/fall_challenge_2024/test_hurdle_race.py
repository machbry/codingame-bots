import pytest

from bots.summer_challenge_2024.challengelibs.actions import Action
from bots.summer_challenge_2024.challengelibs.mini_games import HurdleRace
from bots.summer_challenge_2024.challengelibs.score_info import ScoreInfo


@pytest.mark.parametrize("turn_input, player_idx, action, result_expected", [
    ("....#...#....#................ 2 0 0 0 0 0 0", 0, Action.UP, 2 - HurdleRace.ESTIMATE_PENALTY_MOVE_WHEN_STUNNED),
    ("....#...#....#................ 2 0 0 0 0 0 0", 0, Action.LEFT, 1),
    ("....#...#....#................ 2 0 0 0 0 0 0", 0, Action.DOWN, 2 - HurdleRace.ESTIMATE_PENALTY_MOVE_WHEN_STUNNED),
    ("....#...#....#................ 2 0 0 0 0 0 0", 0, Action.RIGHT, 2 - HurdleRace.ESTIMATE_PENALTY_MOVE_WHEN_STUNNED),
    ("....#...#....#................ 3 0 0 0 0 0 0", 0, Action.UP, 2),
    ("....#...#....#................ 3 0 0 0 0 0 0", 0, Action.LEFT, 1 - HurdleRace.ESTIMATE_PENALTY_MOVE_WHEN_STUNNED),
    ("....#...#....#................ 3 0 0 0 0 0 0", 0, Action.DOWN, 1 - HurdleRace.ESTIMATE_PENALTY_MOVE_WHEN_STUNNED),
    ("....#...#....#................ 3 0 0 0 0 0 0", 0, Action.RIGHT, 1 - HurdleRace.ESTIMATE_PENALTY_MOVE_WHEN_STUNNED),
    ("....#...#....#................ 4 0 0 0 0 0 0", 0, Action.UP, 2),
    ("....#...#....#................ 4 0 0 0 0 0 0", 0, Action.LEFT, 1),
    ("....#...#....#................ 4 0 0 0 0 0 0", 0, Action.DOWN, 2),
    ("....#...#....#................ 4 0 0 0 0 0 0", 0, Action.RIGHT, 3),
])
def test_evaluate_action(turn_input, player_idx, action, result_expected):
    score_info = ScoreInfo(inputs="126 0 2 1 0 3 0 2 1 0 1 0 2".split(), nb_mini_games=4)

    mini_game = HurdleRace(inputs=turn_input.split(), player_idx=player_idx, players_scores=[score_info]*3)

    result = mini_game.average_score_evolution_expected(action)

    assert result == result_expected
