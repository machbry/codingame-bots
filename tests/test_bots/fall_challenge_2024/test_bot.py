import pytest
from unittest.mock import PropertyMock, patch
from typing import List
from timeit import repeat
from functools import partial

from bots.fall_challenge_2024.game_loop import GameLoop


BOT_PACKAGE = "bots.fall_challenge_2024"
GameLoop.LOG = False
TEST_INPUTS = [
    (['18 8'], 3, [
         '102', '0 0 WALL -1 0 X 0 0', '1 0 WALL -1 0 X 0 0', '2 0 WALL -1 0 X 0 0', '3 0 WALL -1 0 X 0 0', '4 0 WALL -1 0 X 0 0', '5 0 WALL -1 0 X 0 0', '6 0 WALL -1 0 X 0 0', '7 0 WALL -1 0 X 0 0', '8 0 WALL -1 0 X 0 0', '9 0 WALL -1 0 X 0 0', '10 0 WALL -1 0 X 0 0', '11 0 WALL -1 0 X 0 0', '12 0 WALL -1 0 X 0 0', '13 0 WALL -1 0 X 0 0', '14 0 WALL -1 0 X 0 0', '15 0 WALL -1 0 X 0 0', '16 0 WALL -1 0 X 0 0', '17 0 WALL -1 0 X 0 0', '0 1 WALL -1 0 X 0 0', '1 1 WALL -1 0 X 0 0', '2 1 WALL -1 0 X 0 0', '3 1 WALL -1 0 X 0 0', '4 1 WALL -1 0 X 0 0', '5 1 WALL -1 0 X 0 0', '6 1 WALL -1 0 X 0 0', '7 1 WALL -1 0 X 0 0', '8 1 WALL -1 0 X 0 0', '9 1 WALL -1 0 X 0 0', '10 1 WALL -1 0 X 0 0', '11 1 WALL -1 0 X 0 0', '12 1 WALL -1 0 X 0 0', '13 1 WALL -1 0 X 0 0', '14 1 WALL -1 0 X 0 0', '15 1 WALL -1 0 X 0 0', '16 1 WALL -1 0 X 0 0', '17 1 WALL -1 0 X 0 0', '0 2 WALL -1 0 X 0 0', '1 2 ROOT 1 1 N 0 1', '2 2 BASIC 1 3 N 1 1', '3 2 BASIC 1 5 N 3 1', '4 2 BASIC 1 8 N 5 1', '5 2 BASIC 1 10 N 8 1', '6 2 BASIC 1 12 N 10 1', '7 2 BASIC 1 14 N 12 1', '8 2 BASIC 1 16 N 14 1', '9 2 BASIC 1 18 N 16 1', '10 2 BASIC 1 20 N 18 1', '11 2 BASIC 1 21 N 20 1', '13 2 BASIC 0 19 N 13 2', '17 2 WALL -1 0 X 0 0', '0 3 WALL -1 0 X 0 0', '13 3 BASIC 0 13 N 11 2', '14 3 BASIC 0 11 N 9 2', '15 3 BASIC 0 15 N 7 2', '17 3 WALL -1 0 X 0 0', '0 4 WALL -1 0 X 0 0', '14 4 BASIC 0 9 N 6 2', '15 4 BASIC 0 7 N 4 2', '17 4 WALL -1 0 X 0 0', '0 5 WALL -1 0 X 0 0', '12 5 BASIC 0 22 N 17 2', '13 5 BASIC 0 17 N 6 2', '14 5 BASIC 0 6 N 4 2', '15 5 BASIC 0 4 N 2 2', '16 5 ROOT 0 2 N 0 2', '17 5 WALL -1 0 X 0 0', '0 6 WALL -1 0 X 0 0', '1 6 WALL -1 0 X 0 0', '2 6 WALL -1 0 X 0 0', '3 6 WALL -1 0 X 0 0', '4 6 WALL -1 0 X 0 0', '5 6 WALL -1 0 X 0 0', '6 6 WALL -1 0 X 0 0', '7 6 WALL -1 0 X 0 0', '8 6 WALL -1 0 X 0 0', '9 6 WALL -1 0 X 0 0', '10 6 WALL -1 0 X 0 0', '11 6 WALL -1 0 X 0 0', '12 6 WALL -1 0 X 0 0', '13 6 WALL -1 0 X 0 0', '14 6 WALL -1 0 X 0 0', '15 6 WALL -1 0 X 0 0', '16 6 WALL -1 0 X 0 0', '17 6 WALL -1 0 X 0 0', '0 7 WALL -1 0 X 0 0', '1 7 WALL -1 0 X 0 0', '2 7 WALL -1 0 X 0 0', '3 7 WALL -1 0 X 0 0', '4 7 WALL -1 0 X 0 0', '5 7 WALL -1 0 X 0 0', '6 7 WALL -1 0 X 0 0', '7 7 WALL -1 0 X 0 0', '8 7 WALL -1 0 X 0 0', '9 7 WALL -1 0 X 0 0', '10 7 WALL -1 0 X 0 0', '11 7 WALL -1 0 X 0 0', '12 7 WALL -1 0 X 0 0', '13 7 WALL -1 0 X 0 0', '14 7 WALL -1 0 X 0 0', '15 7 WALL -1 0 X 0 0', '16 7 WALL -1 0 X 0 0', '17 7 WALL -1 0 X 0 0', '40 50 50 0', '40 50 50 0', '1',
         '104', '0 0 WALL -1 0 X 0 0', '1 0 WALL -1 0 X 0 0', '2 0 WALL -1 0 X 0 0', '3 0 WALL -1 0 X 0 0', '4 0 WALL -1 0 X 0 0', '5 0 WALL -1 0 X 0 0', '6 0 WALL -1 0 X 0 0', '7 0 WALL -1 0 X 0 0', '8 0 WALL -1 0 X 0 0', '9 0 WALL -1 0 X 0 0', '10 0 WALL -1 0 X 0 0', '11 0 WALL -1 0 X 0 0', '12 0 WALL -1 0 X 0 0', '13 0 WALL -1 0 X 0 0', '14 0 WALL -1 0 X 0 0', '15 0 WALL -1 0 X 0 0', '16 0 WALL -1 0 X 0 0', '17 0 WALL -1 0 X 0 0', '0 1 WALL -1 0 X 0 0', '1 1 WALL -1 0 X 0 0', '2 1 WALL -1 0 X 0 0', '3 1 WALL -1 0 X 0 0', '4 1 WALL -1 0 X 0 0', '5 1 WALL -1 0 X 0 0', '6 1 WALL -1 0 X 0 0', '7 1 WALL -1 0 X 0 0', '8 1 WALL -1 0 X 0 0', '9 1 WALL -1 0 X 0 0', '10 1 WALL -1 0 X 0 0', '11 1 WALL -1 0 X 0 0', '12 1 WALL -1 0 X 0 0', '13 1 WALL -1 0 X 0 0', '14 1 WALL -1 0 X 0 0', '15 1 WALL -1 0 X 0 0', '16 1 WALL -1 0 X 0 0', '17 1 WALL -1 0 X 0 0', '0 2 WALL -1 0 X 0 0', '1 2 ROOT 1 1 N 0 1', '2 2 BASIC 1 3 N 1 1', '3 2 BASIC 1 5 N 3 1', '4 2 BASIC 1 8 N 5 1', '5 2 BASIC 1 10 N 8 1', '6 2 BASIC 1 12 N 10 1', '7 2 BASIC 1 14 N 12 1', '8 2 BASIC 1 16 N 14 1', '9 2 BASIC 1 18 N 16 1', '10 2 BASIC 1 20 N 18 1', '11 2 BASIC 1 21 N 20 1', '12 2 BASIC 1 24 N 21 1', '13 2 BASIC 0 19 N 13 2', '14 2 BASIC 0 23 N 11 2', '17 2 WALL -1 0 X 0 0', '0 3 WALL -1 0 X 0 0', '13 3 BASIC 0 13 N 11 2', '14 3 BASIC 0 11 N 9 2', '15 3 BASIC 0 15 N 7 2', '17 3 WALL -1 0 X 0 0', '0 4 WALL -1 0 X 0 0', '14 4 BASIC 0 9 N 6 2', '15 4 BASIC 0 7 N 4 2', '17 4 WALL -1 0 X 0 0', '0 5 WALL -1 0 X 0 0', '12 5 BASIC 0 22 N 17 2', '13 5 BASIC 0 17 N 6 2', '14 5 BASIC 0 6 N 4 2', '15 5 BASIC 0 4 N 2 2', '16 5 ROOT 0 2 N 0 2', '17 5 WALL -1 0 X 0 0', '0 6 WALL -1 0 X 0 0', '1 6 WALL -1 0 X 0 0', '2 6 WALL -1 0 X 0 0', '3 6 WALL -1 0 X 0 0', '4 6 WALL -1 0 X 0 0', '5 6 WALL -1 0 X 0 0', '6 6 WALL -1 0 X 0 0', '7 6 WALL -1 0 X 0 0', '8 6 WALL -1 0 X 0 0', '9 6 WALL -1 0 X 0 0', '10 6 WALL -1 0 X 0 0', '11 6 WALL -1 0 X 0 0', '12 6 WALL -1 0 X 0 0', '13 6 WALL -1 0 X 0 0', '14 6 WALL -1 0 X 0 0', '15 6 WALL -1 0 X 0 0', '16 6 WALL -1 0 X 0 0', '17 6 WALL -1 0 X 0 0', '0 7 WALL -1 0 X 0 0', '1 7 WALL -1 0 X 0 0', '2 7 WALL -1 0 X 0 0', '3 7 WALL -1 0 X 0 0', '4 7 WALL -1 0 X 0 0', '5 7 WALL -1 0 X 0 0', '6 7 WALL -1 0 X 0 0', '7 7 WALL -1 0 X 0 0', '8 7 WALL -1 0 X 0 0', '9 7 WALL -1 0 X 0 0', '10 7 WALL -1 0 X 0 0', '11 7 WALL -1 0 X 0 0', '12 7 WALL -1 0 X 0 0', '13 7 WALL -1 0 X 0 0', '14 7 WALL -1 0 X 0 0', '15 7 WALL -1 0 X 0 0', '16 7 WALL -1 0 X 0 0', '17 7 WALL -1 0 X 0 0', '39 50 50 0', '39 50 50 0', '1',
         '105', '0 0 WALL -1 0 X 0 0', '1 0 WALL -1 0 X 0 0', '2 0 WALL -1 0 X 0 0', '3 0 WALL -1 0 X 0 0', '4 0 WALL -1 0 X 0 0', '5 0 WALL -1 0 X 0 0', '6 0 WALL -1 0 X 0 0', '7 0 WALL -1 0 X 0 0', '8 0 WALL -1 0 X 0 0', '9 0 WALL -1 0 X 0 0', '10 0 WALL -1 0 X 0 0', '11 0 WALL -1 0 X 0 0', '12 0 WALL -1 0 X 0 0', '13 0 WALL -1 0 X 0 0', '14 0 WALL -1 0 X 0 0', '15 0 WALL -1 0 X 0 0', '16 0 WALL -1 0 X 0 0', '17 0 WALL -1 0 X 0 0', '0 1 WALL -1 0 X 0 0', '1 1 WALL -1 0 X 0 0', '2 1 WALL -1 0 X 0 0', '3 1 WALL -1 0 X 0 0', '4 1 WALL -1 0 X 0 0', '5 1 WALL -1 0 X 0 0', '6 1 WALL -1 0 X 0 0', '7 1 WALL -1 0 X 0 0', '8 1 WALL -1 0 X 0 0', '9 1 WALL -1 0 X 0 0', '10 1 WALL -1 0 X 0 0', '11 1 WALL -1 0 X 0 0', '12 1 WALL -1 0 X 0 0', '13 1 WALL -1 0 X 0 0', '14 1 WALL -1 0 X 0 0', '15 1 WALL -1 0 X 0 0', '16 1 WALL -1 0 X 0 0', '17 1 WALL -1 0 X 0 0', '0 2 WALL -1 0 X 0 0', '1 2 ROOT 1 1 N 0 1', '2 2 BASIC 1 3 N 1 1', '3 2 BASIC 1 5 N 3 1', '4 2 BASIC 1 8 N 5 1', '5 2 BASIC 1 10 N 8 1', '6 2 BASIC 1 12 N 10 1', '7 2 BASIC 1 14 N 12 1', '8 2 BASIC 1 16 N 14 1', '9 2 BASIC 1 18 N 16 1', '10 2 BASIC 1 20 N 18 1', '11 2 BASIC 1 21 N 20 1', '12 2 BASIC 1 24 N 21 1', '13 2 BASIC 0 19 N 13 2', '14 2 BASIC 0 23 N 11 2', '17 2 WALL -1 0 X 0 0', '0 3 WALL -1 0 X 0 0', '13 3 BASIC 0 13 N 11 2', '14 3 BASIC 0 11 N 9 2', '15 3 BASIC 0 15 N 7 2', '17 3 WALL -1 0 X 0 0', '0 4 WALL -1 0 X 0 0', '13 4 BASIC 0 25 N 13 2', '14 4 BASIC 0 9 N 6 2', '15 4 BASIC 0 7 N 4 2', '17 4 WALL -1 0 X 0 0', '0 5 WALL -1 0 X 0 0', '12 5 BASIC 0 22 N 17 2', '13 5 BASIC 0 17 N 6 2', '14 5 BASIC 0 6 N 4 2', '15 5 BASIC 0 4 N 2 2', '16 5 ROOT 0 2 N 0 2', '17 5 WALL -1 0 X 0 0', '0 6 WALL -1 0 X 0 0', '1 6 WALL -1 0 X 0 0', '2 6 WALL -1 0 X 0 0', '3 6 WALL -1 0 X 0 0', '4 6 WALL -1 0 X 0 0', '5 6 WALL -1 0 X 0 0', '6 6 WALL -1 0 X 0 0', '7 6 WALL -1 0 X 0 0', '8 6 WALL -1 0 X 0 0', '9 6 WALL -1 0 X 0 0', '10 6 WALL -1 0 X 0 0', '11 6 WALL -1 0 X 0 0', '12 6 WALL -1 0 X 0 0', '13 6 WALL -1 0 X 0 0', '14 6 WALL -1 0 X 0 0', '15 6 WALL -1 0 X 0 0', '16 6 WALL -1 0 X 0 0', '17 6 WALL -1 0 X 0 0', '0 7 WALL -1 0 X 0 0', '1 7 WALL -1 0 X 0 0', '2 7 WALL -1 0 X 0 0', '3 7 WALL -1 0 X 0 0', '4 7 WALL -1 0 X 0 0', '5 7 WALL -1 0 X 0 0', '6 7 WALL -1 0 X 0 0', '7 7 WALL -1 0 X 0 0', '8 7 WALL -1 0 X 0 0', '9 7 WALL -1 0 X 0 0', '10 7 WALL -1 0 X 0 0', '11 7 WALL -1 0 X 0 0', '12 7 WALL -1 0 X 0 0', '13 7 WALL -1 0 X 0 0', '14 7 WALL -1 0 X 0 0', '15 7 WALL -1 0 X 0 0', '16 7 WALL -1 0 X 0 0', '17 7 WALL -1 0 X 0 0', '39 50 50 0', '38 50 50 0', '1',
    ]),
    (['18 8'], 1, [
           '113', '0 0 WALL -1 0 X 0 0', '1 0 WALL -1 0 X 0 0', '2 0 WALL -1 0 X 0 0', '3 0 WALL -1 0 X 0 0', '4 0 WALL -1 0 X 0 0', '5 0 WALL -1 0 X 0 0', '6 0 WALL -1 0 X 0 0', '7 0 WALL -1 0 X 0 0', '8 0 WALL -1 0 X 0 0', '9 0 WALL -1 0 X 0 0', '10 0 WALL -1 0 X 0 0', '11 0 WALL -1 0 X 0 0', '12 0 WALL -1 0 X 0 0', '13 0 WALL -1 0 X 0 0', '14 0 WALL -1 0 X 0 0', '15 0 WALL -1 0 X 0 0', '16 0 WALL -1 0 X 0 0', '17 0 WALL -1 0 X 0 0', '0 1 WALL -1 0 X 0 0', '1 1 WALL -1 0 X 0 0', '2 1 WALL -1 0 X 0 0', '3 1 WALL -1 0 X 0 0', '4 1 WALL -1 0 X 0 0', '5 1 WALL -1 0 X 0 0', '6 1 WALL -1 0 X 0 0', '7 1 WALL -1 0 X 0 0', '8 1 WALL -1 0 X 0 0', '9 1 WALL -1 0 X 0 0', '10 1 WALL -1 0 X 0 0', '11 1 WALL -1 0 X 0 0', '12 1 WALL -1 0 X 0 0', '13 1 WALL -1 0 X 0 0', '14 1 WALL -1 0 X 0 0', '15 1 WALL -1 0 X 0 0', '16 1 WALL -1 0 X 0 0', '17 1 WALL -1 0 X 0 0', '0 2 WALL -1 0 X 0 0', '1 2 ROOT 1 1 N 0 1', '2 2 BASIC 1 3 N 1 1', '3 2 BASIC 1 5 N 3 1', '4 2 BASIC 1 8 N 5 1', '5 2 BASIC 1 10 N 8 1', '6 2 BASIC 1 12 N 10 1', '7 2 BASIC 1 14 N 12 1', '8 2 BASIC 1 16 N 14 1', '9 2 BASIC 1 18 N 16 1', '10 2 BASIC 1 20 N 18 1', '11 2 BASIC 1 21 N 20 1', '12 2 BASIC 1 24 N 21 1', '13 2 BASIC 0 19 N 13 2', '14 2 BASIC 0 23 N 11 2', '15 2 BASIC 0 31 N 15 2', '17 2 WALL -1 0 X 0 0', '0 3 WALL -1 0 X 0 0', '11 3 BASIC 1 28 N 26 1', '12 3 BASIC 1 26 N 24 1', '13 3 BASIC 0 13 N 11 2', '14 3 BASIC 0 11 N 9 2', '15 3 BASIC 0 15 N 7 2', '16 3 BASIC 0 27 N 15 2', '17 3 WALL -1 0 X 0 0', '0 4 WALL -1 0 X 0 0', '11 4 BASIC 1 30 N 28 1', '12 4 WALL -1 0 X 0 0', '13 4 BASIC 0 25 N 13 2', '14 4 BASIC 0 9 N 6 2', '15 4 BASIC 0 7 N 4 2', '16 4 BASIC 0 29 N 2 2', '17 4 WALL -1 0 X 0 0', '0 5 WALL -1 0 X 0 0', '11 5 BASIC 1 32 N 30 1', '12 5 BASIC 0 22 N 17 2', '13 5 BASIC 0 17 N 6 2', '14 5 BASIC 0 6 N 4 2', '15 5 BASIC 0 4 N 2 2', '16 5 ROOT 0 2 N 0 2', '17 5 WALL -1 0 X 0 0', '0 6 WALL -1 0 X 0 0', '1 6 WALL -1 0 X 0 0', '2 6 WALL -1 0 X 0 0', '3 6 WALL -1 0 X 0 0', '4 6 WALL -1 0 X 0 0', '5 6 WALL -1 0 X 0 0', '6 6 WALL -1 0 X 0 0', '7 6 WALL -1 0 X 0 0', '8 6 WALL -1 0 X 0 0', '9 6 WALL -1 0 X 0 0', '10 6 WALL -1 0 X 0 0', '11 6 WALL -1 0 X 0 0', '12 6 WALL -1 0 X 0 0', '13 6 WALL -1 0 X 0 0', '14 6 WALL -1 0 X 0 0', '15 6 WALL -1 0 X 0 0', '16 6 WALL -1 0 X 0 0', '17 6 WALL -1 0 X 0 0', '0 7 WALL -1 0 X 0 0', '1 7 WALL -1 0 X 0 0', '2 7 WALL -1 0 X 0 0', '3 7 WALL -1 0 X 0 0', '4 7 WALL -1 0 X 0 0', '5 7 WALL -1 0 X 0 0', '6 7 WALL -1 0 X 0 0', '7 7 WALL -1 0 X 0 0', '8 7 WALL -1 0 X 0 0', '9 7 WALL -1 0 X 0 0', '10 7 WALL -1 0 X 0 0', '11 7 WALL -1 0 X 0 0', '12 7 WALL -1 0 X 0 0', '13 7 WALL -1 0 X 0 0', '14 7 WALL -1 0 X 0 0', '15 7 WALL -1 0 X 0 0', '16 7 WALL -1 0 X 0 0', '17 7 WALL -1 0 X 0 0', '34 50 50 0', '34 50 50 0', '1',
    ]),
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

    # last results : init, start, update: 1.07ms, 1.78ms, 1.39ms (R = 10, N = 10)
