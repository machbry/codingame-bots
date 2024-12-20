import pytest
from unittest.mock import PropertyMock, patch
from typing import List
from timeit import repeat
from functools import partial

from bots.fall_challenge_2024.game_loop import GameLoop


BOT_PACKAGE = "bots.fall_challenge_2024"
GameLoop.LOG = False
TEST_INPUTS = [
    (['18 9'], 1, ['81', '0 0 WALL -1 0 X 0 0', '1 0 WALL -1 0 X 0 0', '2 0 WALL -1 0 X 0 0', '3 0 WALL -1 0 X 0 0', '4 0 WALL -1 0 X 0 0', '5 0 WALL -1 0 X 0 0', '6 0 WALL -1 0 X 0 0', '7 0 WALL -1 0 X 0 0', '8 0 WALL -1 0 X 0 0', '9 0 WALL -1 0 X 0 0', '10 0 WALL -1 0 X 0 0', '11 0 WALL -1 0 X 0 0', '12 0 WALL -1 0 X 0 0', '13 0 WALL -1 0 X 0 0', '14 0 WALL -1 0 X 0 0', '15 0 WALL -1 0 X 0 0', '16 0 WALL -1 0 X 0 0', '17 0 WALL -1 0 X 0 0', '0 1 WALL -1 0 X 0 0', '3 1 A -1 0 X 0 0', '6 1 A -1 0 X 0 0', '9 1 A -1 0 X 0 0', '14 1 A -1 0 X 0 0', '17 1 WALL -1 0 X 0 0', '0 2 WALL -1 0 X 0 0', '1 2 ROOT 1 1 N 0 1', '12 2 A -1 0 X 0 0', '16 2 A -1 0 X 0 0', '17 2 WALL -1 0 X 0 0', '0 3 WALL -1 0 X 0 0', '10 3 A -1 0 X 0 0', '17 3 WALL -1 0 X 0 0', '0 4 WALL -1 0 X 0 0', '1 4 WALL -1 0 X 0 0', '2 4 WALL -1 0 X 0 0', '3 4 WALL -1 0 X 0 0', '4 4 WALL -1 0 X 0 0', '5 4 WALL -1 0 X 0 0', '6 4 WALL -1 0 X 0 0', '7 4 WALL -1 0 X 0 0', '8 4 WALL -1 0 X 0 0', '9 4 WALL -1 0 X 0 0', '10 4 WALL -1 0 X 0 0', '11 4 WALL -1 0 X 0 0', '12 4 WALL -1 0 X 0 0', '13 4 WALL -1 0 X 0 0', '14 4 WALL -1 0 X 0 0', '15 4 WALL -1 0 X 0 0', '17 4 WALL -1 0 X 0 0', '0 5 WALL -1 0 X 0 0', '3 5 A -1 0 X 0 0', '6 5 A -1 0 X 0 0', '9 5 A -1 0 X 0 0', '14 5 A -1 0 X 0 0', '17 5 WALL -1 0 X 0 0', '0 6 WALL -1 0 X 0 0', '1 6 ROOT 0 2 N 0 2', '12 6 A -1 0 X 0 0', '16 6 A -1 0 X 0 0', '17 6 WALL -1 0 X 0 0', '0 7 WALL -1 0 X 0 0', '10 7 A -1 0 X 0 0', '17 7 WALL -1 0 X 0 0', '0 8 WALL -1 0 X 0 0', '1 8 WALL -1 0 X 0 0', '2 8 WALL -1 0 X 0 0', '3 8 WALL -1 0 X 0 0', '4 8 WALL -1 0 X 0 0', '5 8 WALL -1 0 X 0 0', '6 8 WALL -1 0 X 0 0', '7 8 WALL -1 0 X 0 0', '8 8 WALL -1 0 X 0 0', '9 8 WALL -1 0 X 0 0', '10 8 WALL -1 0 X 0 0', '11 8 WALL -1 0 X 0 0', '12 8 WALL -1 0 X 0 0', '13 8 WALL -1 0 X 0 0', '14 8 WALL -1 0 X 0 0', '15 8 WALL -1 0 X 0 0', '16 8 WALL -1 0 X 0 0', '17 8 WALL -1 0 X 0 0', '10 0 0 0', '10 0 0 0', '1']),
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

    # last results : init, start, update: 0.08ms, 0.64ms, 0.57ms (R = 10, N = 10)
