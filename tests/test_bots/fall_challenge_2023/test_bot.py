import pytest
from unittest.mock import PropertyMock, patch
from typing import List

from bots.fall_challenge_2023.challengelibs.game_loop import GameLoop


CHALLENGELIBS_PACKAGE = "bots.fall_challenge_2023.challengelibs"


@pytest.mark.parametrize("init_inputs, nb_turns, turns_inputs", [
    (['0'], 1, ['1'])
])
def test_replay_turns(init_inputs: List[str], nb_turns: int, turns_inputs: List[str]):
    input_side_effect = [*init_inputs, *turns_inputs]
    with patch(f"{CHALLENGELIBS_PACKAGE}.game_loop.input", side_effect=input_side_effect):
        running_side_effect = [*[True]*nb_turns, False]
        GameLoop.RUNNING = PropertyMock(side_effect=running_side_effect)
        GameLoop().start()
