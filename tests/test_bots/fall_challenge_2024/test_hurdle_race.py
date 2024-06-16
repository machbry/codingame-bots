import pytest
import numpy as np

from bots.summer_challenge_2024.challengelibs.actions import Action
from bots.summer_challenge_2024.challengelibs.mini_games import HurdleRace


TEST_RACETRACK = "....#...#....#................"


@pytest.mark.parametrize("turn_input, my_idx, action, reg_expected", [
    (f"{TEST_RACETRACK} 2 0 0 0 0 0 0", 0, Action.UP, np.array([4, 0, 0, 3, 0, 0, 0])),
    (f"{TEST_RACETRACK} 2 0 0 0 0 0 0", 0, Action.LEFT, np.array([3, 0, 0, 0, 0, 0, 0])),
    (f"{TEST_RACETRACK} 2 0 0 0 0 0 0", 0, Action.DOWN, np.array([4, 0, 0, 3, 0, 0, 0])),
    (f"{TEST_RACETRACK} 2 0 0 0 0 0 0", 0, Action.RIGHT, np.array([4, 0, 0, 3, 0, 0, 0])),
    (f"{TEST_RACETRACK} 3 0 0 0 0 0 0", 0, Action.UP, np.array([5, 0, 0, 0, 0, 0, 0])),
    (f"{TEST_RACETRACK} 3 0 0 0 0 0 0", 0, Action.LEFT, np.array([4, 0, 0, 3, 0, 0, 0])),
    (f"{TEST_RACETRACK} 3 0 0 0 0 0 0", 0, Action.DOWN, np.array([4, 0, 0, 3, 0, 0, 0])),
    (f"{TEST_RACETRACK} 3 0 0 0 0 0 0", 0, Action.RIGHT, np.array([4, 0, 0, 3, 0, 0, 0])),
    (f"{TEST_RACETRACK} 4 0 0 0 0 0 0", 0, Action.UP, np.array([6, 0, 0, 0, 0, 0, 0])),
    (f"{TEST_RACETRACK} 4 0 0 0 0 0 0", 0, Action.LEFT, np.array([5, 0, 0, 0, 0, 0, 0])),
    (f"{TEST_RACETRACK} 4 0 0 0 0 0 0", 0, Action.DOWN, np.array([6, 0, 0, 0, 0, 0, 0])),
    (f"{TEST_RACETRACK} 4 0 0 0 0 0 0", 0, Action.RIGHT, np.array([7, 0, 0, 0, 0, 0, 0])),
    (f"{TEST_RACETRACK} 8 0 0 2 0 0 0", 0, Action.UP, np.array([8, 0, 0, 1, 0, 0, 0])),
    (f"{TEST_RACETRACK} 28 0 0 0 0 0 0", 0, Action.DOWN, np.array([29, 0, 0, 0, 0, 0, 0])),
])
def test_next_gpu_reg_with_player_action(turn_input, my_idx, action, reg_expected):
    mini_game = HurdleRace(inputs=turn_input.split(), my_idx=my_idx)
    gpu = mini_game.gpu

    next_gpu, next_reg = mini_game.next_gpu_reg_with_player_action(player_idx=my_idx, action=action, current_gpu=gpu,
                                                                   current_reg=mini_game.reg)

    assert (next_reg == reg_expected).all()


@pytest.mark.parametrize("reg, players_mini_game_results_expected", [
    (np.array([7, 2, 4, 0, 0, 0, 0]), [np.array([[1/3 + (7/29) * (2/3), 1/3 - (7/29) * (1/3), 1/3 - (7/29) * (1/3)]]),
                                       np.array([[1/3 - (7/29) * (1/3), 1/3 - (7/29) * (1/3), 1/3 + (7/29) * (2/3)]]),
                                       np.array([[1/3 - (7/29) * (1/3), 1/3 + (7/29) * (2/3), 1/3 - (7/29) * (1/3)]])])
])
def test_predict_players_mini_game_results_with_gpu_reg(reg, players_mini_game_results_expected):
    mini_game = HurdleRace(inputs=f"{TEST_RACETRACK} 2 0 0 0 0 0 0".split(), my_idx=0)
    gpu = mini_game.gpu

    players_mini_game_results = mini_game.predict_players_mini_game_results_with_gpu_reg(gpu, reg)

    for i, player_mini_game_results in enumerate(players_mini_game_results):
        assert (player_mini_game_results == players_mini_game_results_expected[i]).all()

