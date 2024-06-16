import pytest
import numpy as np

from bots.summer_challenge_2024.challengelibs.actions import Action
from bots.summer_challenge_2024.challengelibs.mini_games import Archery


@pytest.mark.parametrize("turn_input, my_idx, action, gpu_expected, reg_expected", [
    ("332213 20 -11 6 -13 6 -13 0", 0, Action.UP, "32213", np.array([20, -14, 6, -13, 6, -13, 0])),
    ("332213 20 -11 6 -13 6 -13 0", 0, Action.RIGHT, "32213", np.array([20, -11, 6, -13, 6, -13, 0])),
    ("332213 20 -11 6 -13 6 -13 0", 1, Action.DOWN, "32213", np.array([20, -11, 6, -10, 6, -13, 0])),
    ("332213 20 -11 6 -13 6 -13 0", 2, Action.LEFT, "32213", np.array([20, -11, 6, -13, 3, -13, 0])),
])
def test_next_gpu_reg_with_player_action(turn_input, my_idx, action, gpu_expected, reg_expected):
    mini_game = Archery(inputs=turn_input.split(), my_idx=my_idx)
    gpu = mini_game.gpu

    next_gpu, next_reg = mini_game.next_gpu_reg_with_player_action(player_idx=my_idx, action=action, current_gpu=gpu,
                                                                   current_reg=mini_game.reg)

    assert (next_reg == reg_expected).all()


@pytest.mark.parametrize("reg, players_mini_game_results_expected", [
    (np.array([1, -1, 6, -13, 7, -4, 3]), [np.array([[1/3 + (4/10) * (2/3), 1/3 - (4/10) * (1/3), 1/3 - (4/10) * (1/3)]]),
                                           np.array([[1/3 - (4/10) * (1/3), 1/3 - (4/10) * (1/3), 1/3 + (4/10) * (2/3)]]),
                                           np.array([[1/3 - (4/10) * (1/3), 1/3 + (4/10) * (2/3), 1/3 - (4/10) * (1/3)]])])
])
def test_predict_players_mini_game_results_with_gpu_reg(reg, players_mini_game_results_expected):
    mini_game = Archery(inputs="332213 20 -11 6 -13 6 -13 0".split(), my_idx=0)
    gpu = mini_game.gpu

    players_mini_game_results = mini_game.predict_players_mini_game_results_with_gpu_reg(gpu, reg)

    for i, player_mini_game_results in enumerate(players_mini_game_results):
        assert (player_mini_game_results == players_mini_game_results_expected[i]).all()


