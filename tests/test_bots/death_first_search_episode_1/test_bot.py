import pytest
from unittest.mock import PropertyMock, patch
from typing import List

from bots.death_first_search_episode_1.challengelibs.game_loop import GameLoop


CHALLENGELIBS_PACKAGE = "bots.death_first_search_episode_1.challengelibs"


@pytest.mark.parametrize("init_inputs, turns_inputs", [
    (['4 4 1', '1 3', '2 3', '0 1', '0 2', '3'], ['0', '1'])
])
def test_replay_turns(init_inputs: List[str], turns_inputs: List[str]):
    input_side_effect = [*init_inputs, *turns_inputs]
    with patch(f"{CHALLENGELIBS_PACKAGE}.game_loop.input", side_effect=input_side_effect):
        running_side_effect = [*[True]*len(turns_inputs), False]
        GameLoop.RUNNING = PropertyMock(side_effect=running_side_effect)
        GameLoop().start()

