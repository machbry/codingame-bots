import pytest
from unittest.mock import PropertyMock, patch
from typing import List
from timeit import repeat
from functools import partial

from bots.fall_challenge_2023.game_loop import GameLoop


BOT_PACKAGE = "bots.fall_challenge_2023"
GameLoop.LOG = False

TEST_INPUTS = [
    (['12', '2 0 0', '3 1 0', '4 0 1', '5 1 1', '6 0 2', '7 1 2', '8 2 0', '9 3 0', '10 2 1', '11 3 1', '12 2 2', '13 3 2'],
     1, ['0', '0', '0', '0', '1', '0 3333 500 0 30', '1', '1 6666 500 0 30', '0', '12', '2 1625 3881 -200 0', '3 8374 3881 200 0', '4 1409 6412 141 141', '5 8590 6412 -141 141', '6 1313 8792 200 0', '7 8686 8792 -200 0', '8 6778 3650 -141 -141', '9 3221 3650 141 -141', '10 2489 6061 -141 141', '11 7510 6061 141 141', '12 2713 8743 0 -200', '13 7286 8743 0 -200', '12', '0 2 BL', '0 3 BR', '0 4 BL', '0 5 BR', '0 6 BL', '0 7 BR', '0 8 BR', '0 9 BL', '0 10 BL', '0 11 BR', '0 12 BL', '0 13 BR']),
    (['12', '2 0 0', '3 1 0', '4 0 1', '5 1 1', '6 0 2', '7 1 2', '8 2 0', '9 3 0', '10 2 1', '11 3 1', '12 2 2', '13 3 2'],
     1, ['3', '7', '2', '8', '2', '3', '2', '5', '8', '1', '0 3333 5000 0 3', '1', '1 3489 5630 0 27', '0', '12', '2 2013 3104 -64 -190', '3 7986 3104 64 -190', '4 8153 6218 141 141', '5 1846 6218 -141 141', '6 3929 8413 141 141', '7 6070 8413 -141 141', '8 3586 3373 64 190', '9 6413 3373 -64 190', '10 9586 6585 141 -141', '11 413 6585 -141 -141', '12 7421 8600 200 0', '13 2578 8600 -200 0', '12', '0 2 TL', '0 3 TR', '0 4 BR', '0 5 BL', '0 6 BR', '0 7 BR', '0 8 TR', '0 9 TR', '0 10 BR', '0 11 BL', '0 12 BR', '0 13 BL']),
    (['12', '2 0 0', '3 1 0', '4 0 1', '5 1 1', '6 0 2', '7 1 2', '8 2 0', '9 3 0', '10 2 1', '11 3 1', '12 2 2', '13 3 2'],
     1, ['0', '0', '0', '0', '1', '0 3333 500 0 30', '1', '1 6666 500 0 30', '0', '0', '12', '0 2 BR', '0 3 BL', '0 4 BL', '0 5 BR', '0 6 BR', '0 7 BL', '0 8 BR', '0 9 BL', '0 10 BL', '0 11 BR', '0 12 BL', '0 13 BR']),
    (['12', '2 0 0', '3 1 0', '4 0 1', '5 1 1', '6 0 2', '7 1 2', '8 2 0', '9 3 0', '10 2 1', '11 3 1', '12 2 2', '13 3 2'],
     1, ['0', '2', '0', '1', '3', '1', '0 1807 4500 0 7', '1', '1 4122 3436 0 7', '3', '0 2', '0 8', '1 8', '1', '2 1608 4478 -199 -22', '12', '0 2 TL', '0 3 TR', '0 4 BR', '0 5 BR', '0 6 BR', '0 7 BL', '0 8 BR', '0 9 BR', '0 10 BL', '0 11 BR', '0 12 BR', '0 13 BR']),
    (['12', '2 0 0', '3 1 0', '4 0 1', '5 1 1', '6 0 2', '7 1 2', '8 2 0', '9 3 0', '10 2 1', '11 3 1', '12 2 2', '13 3 2'],
     1, ['0', '0', '0', '0', '1', '0 4769 3442 0 0', '1', '1 4970 996 0 24', '6', '0 8', '0 9', '0 3', '0 2', '1 8', '1 9', '4', '2 6707 3679 -200 0', '3 3292 3679 200 0', '8 4576 2905 141 -141', '9 5423 2905 -141 -141', '12', '0 2 BR', '0 3 BL', '0 4 BR', '0 5 BL', '0 6 BL', '0 7 BR', '0 8 TL', '0 9 TR', '0 10 BR', '0 11 BL', '0 12 BL', '0 13 BR']),
    (['12', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2'],
     1, ['0', '0', '0', '0', '2', '0 2000 500 0 30', '2 6000 500 0 30', '2', '1 7999 500 0 30', '3 3999 500 0 30', '0', '0', '24', '0 4 BL', '0 5 BR', '0 6 BR', '0 7 BR', '0 8 BL', '0 9 BR', '0 10 BR', '0 11 BR', '0 12 BR', '0 13 BR', '0 14 BR', '0 15 BR', '2 4 BL', '2 5 BR', '2 6 BR', '2 7 BL', '2 8 BL', '2 9 BR', '2 10 BL', '2 11 BR', '2 12 BR', '2 13 BL', '2 14 BR', '2 15 BL']),
    (['12', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2'],
     1, ['0', '0', '0', '0', '2', '0 2386 959 0 25', '2 5680 1007 0 25', '2', '1 7999 1100 0 30', '3 3999 1100 0 30', '0', '0', '24', '0 4 BL', '0 5 BR', '0 6 BR', '0 7 BR', '0 8 BL', '0 9 BR', '0 10 BR', '0 11 BR', '0 12 BR', '0 13 BR', '0 14 BR', '0 15 BR', '2 4 BL', '2 5 BR', '2 6 BR', '2 7 BL', '2 8 BL', '2 9 BR', '2 10 BL', '2 11 BR', '2 12 BR', '2 13 BL', '2 14 BR', '2 15 BL']),
    (['12', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2'],
     1, ['14', '0', '4', '6', '7', '4', '12', '0', '2', '0 6297 2017 0 1', '2 5827 2039 0 1', '2', '1 1183 9999 0 10', '3 478 9999 0 14', '16', '1 11', '1 5', '1 12', '1 6', '1 9', '1 4', '1 7', '1 13', '1 14', '3 4', '3 10', '3 6', '3 7', '3 8', '3 13', '3 15', '0', '22', '0 4 BL', '0 5 BR', '0 6 BR', '0 7 BL', '0 8 BL', '0 9 BR', '0 10 BL', '0 11 BR', '0 12 BR', '0 13 BL', '0 14 BR', '2 4 BL', '2 5 BR', '2 6 BR', '2 7 BL', '2 8 BL', '2 9 BR', '2 10 BL', '2 11 BR', '2 12 BR', '2 13 BL', '2 14 BR']),
    (['12', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2'],
     1, ['14', '0', '4', '6', '7', '4', '12', '0', '2', '0 6549 2561 0 2', '2 6106 2570 0 2', '2', '1 583 9999 0 11', '3 78 9999 0 15', '16', '1 11', '1 5', '1 12', '1 6', '1 9', '1 4', '1 7', '1 13', '1 14', '3 4', '3 10', '3 6', '3 7', '3 8', '3 13', '3 15', '0', '20', '0 4 BL', '0 5 BR', '0 6 BR', '0 7 BL', '0 9 BL', '0 10 BL', '0 11 BR', '0 12 BR', '0 13 BL', '0 14 BR', '2 4 BL', '2 5 BR', '2 6 BR', '2 7 BL', '2 9 BR', '2 10 BL', '2 11 BR', '2 12 BR', '2 13 BL', '2 14 BR']),
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


def start_game_loop(game_loop: GameLoop, turns_inputs: List[str], running_side_effect: List[bool]):
    GameLoop.RUNNING = PropertyMock(side_effect=running_side_effect)
    with patch(f"{BOT_PACKAGE}.game_loop.input", side_effect=turns_inputs):
        game_loop.start()


def test_perfs():
    N = 1000
    print()
    for i, test_inputs in enumerate(TEST_INPUTS[8:9]):
        init_inputs, nb_turns, turns_inputs = test_inputs
        with patch(f"{BOT_PACKAGE}.game_loop.print"):
            init_perf = min(repeat(partial(init_game_loop, init_inputs), number=N))
            game_loop = init_game_loop(init_inputs)
            running_side_effect = [*[True] * nb_turns, False]
            loop_perf = min(repeat(partial(start_game_loop, game_loop, turns_inputs, running_side_effect), number=N))
        print(f"init, start: {round(1000*init_perf)}ms, {round(1000*loop_perf)}ms")
