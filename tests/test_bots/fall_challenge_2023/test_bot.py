import pytest
from unittest.mock import PropertyMock, patch
from typing import List
from timeit import repeat
from functools import partial

from bots.fall_challenge_2023.game_loop import GameLoop


BOT_PACKAGE = "bots.fall_challenge_2023"
GameLoop.LOG = False

TEST_INPUTS = [
    (['14', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1'],
     1, ['0', '0', '0', '0', '2', '0 2000 500 0 30', '2 6000 500 0 30', '2', '1 7999 500 0 30', '3 3999 500 0 30', '0', '0', '28', '0 4 BR', '0 5 BR', '0 6 BR', '0 7 BR', '0 8 BR', '0 9 BR', '0 10 BL', '0 11 BR', '0 12 BR', '0 13 BR', '0 14 BR', '0 15 BR', '0 16 BL', '0 17 BR', '2 4 BR', '2 5 BL', '2 6 BR', '2 7 BL', '2 8 BL', '2 9 BR', '2 10 BL', '2 11 BR', '2 12 BR', '2 13 BL', '2 14 BL', '2 15 BR', '2 16 BL', '2 17 BR']),
    (['18', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1', '18 -1 -1', '19 -1 -1', '20 -1 -1', '21 -1 -1'],
     1, ['0', '0', '0', '0', '2', '0 5866 7546 0 5', '2 5859 7457 0 5', '2', '1 6755 6018 0 11', '3 826 7013 0 17', '14', '0 4', '0 6', '0 7', '2 4', '2 6', '2 7', '1 11', '1 12', '1 5', '1 6', '3 4', '3 10', '3 7', '3 13', '2', '17 6516 7310 -527 118', '19 6298 8451 0 0', '34', '0 4 TL', '0 5 TL', '0 6 TR', '0 7 TL', '0 8 BR', '0 9 BL', '0 10 TL', '0 11 TR', '0 12 TR', '0 14 BL', '0 15 BR', '0 16 TL', '0 17 TR', '0 18 BL', '0 19 BR', '0 20 BL', '0 21 BR', '2 4 TL', '2 5 TL', '2 6 TR', '2 7 TL', '2 8 BR', '2 9 BL', '2 10 TL', '2 11 TR', '2 12 TR', '2 14 BL', '2 15 BR', '2 16 TL', '2 17 TR', '2 18 BL', '2 19 BR', '2 20 BL', '2 21 BR']),
    (['18', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1', '18 -1 -1', '19 -1 -1', '20 -1 -1', '21 -1 -1'],
     1, ['0', '0', '0', '0', '2', '0 3776 3201 0 0', '2 4476 4459 0 0', '2', '1 9999 8802 0 30', '3 2557 5496 0 28', '11', '0 4', '2 4', '1 11', '1 4', '1 5', '1 6', '1 12', '3 5', '3 13', '3 7', '3 14', '2', '4 2257 4119 -171 104', '17 5022 3358 -240 484', '30', '0 4 BL', '0 5 BR', '0 6 BR', '0 7 BR', '0 11 BR', '0 12 BR', '0 13 BL', '0 14 BL', '0 15 BR', '0 16 BR', '0 17 BR', '0 18 TL', '0 19 BR', '0 20 BL', '0 21 BR', '2 4 TL', '2 5 TR', '2 6 BR', '2 7 BR', '2 11 TR', '2 12 BR', '2 13 BL', '2 14 BL', '2 15 BR', '2 16 BR', '2 17 TR', '2 18 TL', '2 19 BR', '2 20 BL', '2 21 BR'])
]


@pytest.mark.parametrize("init_inputs, nb_turns, turns_inputs", TEST_INPUTS)
def test_replay_turns(init_inputs: List[str], nb_turns: int, turns_inputs: List[str]):
    input_side_effect = [*init_inputs, *turns_inputs]
    with patch(f"{BOT_PACKAGE}.game_loop.input", side_effect=input_side_effect):
        running_side_effect = [*[True]*nb_turns, False]
        GameLoop.RUNNING = PropertyMock(side_effect=running_side_effect)
        GameLoop().start()


def init_game_loop(init_inputs: List[str]) -> GameLoop:
    with patch(f"{BOT_PACKAGE}.game_loop.input", side_effect=init_inputs):
        return GameLoop()


def start_game_loop(init_inputs: List[str], turns_inputs: List[str], running_side_effect: List[bool]):
    game_loop = init_game_loop(init_inputs)
    GameLoop.RUNNING = PropertyMock(side_effect=running_side_effect)
    with patch(f"{BOT_PACKAGE}.game_loop.input", side_effect=turns_inputs):
        game_loop.start()


# @pytest.mark.skip
def test_perfs():
    N = 1000
    print()
    for i, test_inputs in enumerate(TEST_INPUTS):
        init_inputs, nb_turns, turns_inputs = test_inputs
        with patch(f"{BOT_PACKAGE}.game_loop.print"):
            init_perf = min(repeat(partial(init_game_loop, init_inputs), number=N))
            running_side_effect = [*[True] * nb_turns, False]
            loop_perf = min(repeat(partial(start_game_loop, init_inputs, turns_inputs, running_side_effect), number=N))
        print(f"init, start: {round(1000*init_perf)}ms, {round(1000*(loop_perf-init_perf))}ms")

        # last results : 359ms, 973ms // 408ms, 1231ms // 407ms, 1182ms
