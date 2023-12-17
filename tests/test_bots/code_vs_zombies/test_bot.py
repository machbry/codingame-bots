import pytest
from unittest.mock import PropertyMock, patch
from typing import List

from bots.code_vs_zombies.challengelibs.game_loop import GameLoop


CHALLENGELIBS_PACKAGE = "bots.code_vs_zombies.challengelibs"


@pytest.mark.parametrize("init_inputs, nb_turns, turns_inputs", [
    ([], 12, ['0 0', '1', '0 8250 4500', '1', '0 8250 8999 8250 8599', '0 0', '1', '0 8250 4500', '1', '0 8250 8599 8250 8199', '0 0', '1', '0 8250 4500', '1', '0 8250 8199 8250 7799', '0 0', '1', '0 8250 4500', '1', '0 8250 7799 8250 7399', '0 0', '1', '0 8250 4500', '1', '0 8250 7399 8250 6999', '0 0', '1', '0 8250 4500', '1', '0 8250 6999 8250 6599', '0 0', '1', '0 8250 4500', '1', '0 8250 6599 8250 6199', '0 0', '1', '0 8250 4500', '1', '0 8250 6199 8250 5799', '0 0', '1', '0 8250 4500', '1', '0 8250 5799 8250 5399', '0 0', '1', '0 8250 4500', '1', '0 8250 5399 8250 4999', '0 0', '1', '0 8250 4500', '1', '0 8250 4999 8250 4599', '0 0', '1', '0 8250 4500', '1', '0 8250 4599 8250 4500'])
])
def test_replay_turns(init_inputs: List[str], nb_turns: int, turns_inputs: List[str]):
    GameLoop.LOG = False
    input_side_effect = [*init_inputs, *turns_inputs]
    with patch(f"{CHALLENGELIBS_PACKAGE}.game_loop.input", side_effect=input_side_effect):
        running_side_effect = [*[True]*nb_turns, False]
        GameLoop.RUNNING = PropertyMock(side_effect=running_side_effect)
        GameLoop().start()
