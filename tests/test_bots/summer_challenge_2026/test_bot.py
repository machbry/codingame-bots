import pytest
from unittest.mock import PropertyMock, patch
from typing import List
from timeit import repeat
from functools import partial

from bots.summer_challenge_2026.game_loop import GameLoop


BOT_PACKAGE = "bots.summer_challenge_2026"
GameLoop.LOG = False

TEST_INPUTS = [
    (
        ['16 8', '................', '................', '................', '......0.........', '.........1......', '................', '................', '................'], 
        1, 
        ['0 0 0 0 0 0', '0 0 0 0 0 0', '18', 'PLUM 13 0 3 10 0 3', 'PLUM 2 7 3 10 0 3', 'LEMON 14 4 2 8 0 1', 'LEMON 1 3 2 8 0 1', 'LEMON 6 6 4 12 3 5', 'LEMON 9 1 4 12 3 5', 'LEMON 14 6 3 10 0 1', 'LEMON 1 1 3 10 0 1', 'APPLE 7 4 3 17 0 8', 'APPLE 8 3 3 17 0 8', 'APPLE 2 3 4 20 1 2', 'APPLE 13 4 4 20 1 2', 'APPLE 9 6 3 17 0 4', 'APPLE 6 1 3 17 0 4', 'BANANA 1 6 4 6 2 1', 'BANANA 14 1 4 6 2 1', 'BANANA 5 4 4 6 1 5', 'BANANA 10 3 4 6 1 5', '2', '0 0 6 3 1 1 1 0 0 0 0 0 0 0', '1 1 9 4 1 1 1 0 0 0 0 0 0 0']
    ),
]


@pytest.mark.parametrize("init_inputs, nb_turns, turns_inputs", TEST_INPUTS)
def test_replay_turns(init_inputs: List[str], nb_turns: int, turns_inputs: List[str]):
    input_side_effect = [*init_inputs, *turns_inputs]
    with (patch(f"{BOT_PACKAGE}.game_loop.input", side_effect=input_side_effect)):
        running_side_effect = [*[True] * nb_turns, False]
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


def update_game_loop(init_inputs: List[str], turns_inputs: List[str]):
    game_loop = init_game_loop(init_inputs)
    with patch(f"{BOT_PACKAGE}.game_loop.input", side_effect=turns_inputs):
        game_loop.update_assets()


def test_perfs():
    R = 10
    N = 10
    print()
    init_perfs = []
    start_perfs = []
    update_perfs = []
    L = len(TEST_INPUTS)
    for i, test_inputs in enumerate(TEST_INPUTS):
        init_inputs, nb_turns, turns_inputs = test_inputs
        if nb_turns > 1:
            L -= 1
            continue
        with patch(f"{BOT_PACKAGE}.game_loop.print"):
            init_perf = sum(repeat(partial(init_game_loop, init_inputs), repeat=R, number=N)) / (N * R)
            init_perfs.append(init_perf)

            running_side_effect = [*[True] * nb_turns, False]
            start_perf = sum(repeat(partial(start_game_loop, init_inputs, turns_inputs, running_side_effect), repeat=R,
                                    number=N)) / (N * R)
            start_perfs.append(start_perf - init_perf)

            update_perf = sum(repeat(partial(update_game_loop, init_inputs, turns_inputs), repeat=R, number=N)) / (
                    N * R)
            update_perfs.append(update_perf - init_perf)

    print(
        f"init, start, update: {round(1000 * sum(init_perfs) / L, 2)}ms, {round(1000 * sum(start_perfs) / L, 2)}ms, {round(1000 * sum(update_perfs) / L, 2)}ms (R = {R}, N = {N})")

    # last results : init, start, update: ms, ms, ms (R = 10, N = 10)




