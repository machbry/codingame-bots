import pytest
from unittest.mock import PropertyMock, patch
from typing import List

from bots.fall_challenge_2023.game_loop import GameLoop


BOT_PACKAGE = "bots.fall_challenge_2023"
GameLoop.LOG = False


@pytest.mark.parametrize("init_inputs, nb_turns, turns_inputs", [
    (['12', '2 0 0', '3 1 0', '4 0 1', '5 1 1', '6 0 2', '7 1 2', '8 2 0', '9 3 0', '10 2 1', '11 3 1', '12 2 2', '13 3 2'],
     1, ['0', '0', '0', '0', '1', '0 3333 500 0 30', '1', '1 6666 500 0 30', '0', '12', '2 1625 3881 -200 0', '3 8374 3881 200 0', '4 1409 6412 141 141', '5 8590 6412 -141 141', '6 1313 8792 200 0', '7 8686 8792 -200 0', '8 6778 3650 -141 -141', '9 3221 3650 141 -141', '10 2489 6061 -141 141', '11 7510 6061 141 141', '12 2713 8743 0 -200', '13 7286 8743 0 -200', '12', '0 2 BL', '0 3 BR', '0 4 BL', '0 5 BR', '0 6 BL', '0 7 BR', '0 8 BR', '0 9 BL', '0 10 BL', '0 11 BR', '0 12 BL', '0 13 BR']),
    (['12', '2 0 0', '3 1 0', '4 0 1', '5 1 1', '6 0 2', '7 1 2', '8 2 0', '9 3 0', '10 2 1', '11 3 1', '12 2 2', '13 3 2'],
     1, ['3', '7', '2', '8', '2', '3', '2', '5', '8', '1', '0 3333 5000 0 3', '1', '1 3489 5630 0 27', '0', '12', '2 2013 3104 -64 -190', '3 7986 3104 64 -190', '4 8153 6218 141 141', '5 1846 6218 -141 141', '6 3929 8413 141 141', '7 6070 8413 -141 141', '8 3586 3373 64 190', '9 6413 3373 -64 190', '10 9586 6585 141 -141', '11 413 6585 -141 -141', '12 7421 8600 200 0', '13 2578 8600 -200 0', '12', '0 2 TL', '0 3 TR', '0 4 BR', '0 5 BL', '0 6 BR', '0 7 BR', '0 8 TR', '0 9 TR', '0 10 BR', '0 11 BL', '0 12 BR', '0 13 BL']),
])
def test_replay_turns(init_inputs: List[str], nb_turns: int, turns_inputs: List[str]):
    input_side_effect = [*init_inputs, *turns_inputs]
    with patch(f"{BOT_PACKAGE}.game_loop.input", side_effect=input_side_effect):
        running_side_effect = [*[True]*nb_turns, False]
        GameLoop.RUNNING = PropertyMock(side_effect=running_side_effect)
        GameLoop().start()
