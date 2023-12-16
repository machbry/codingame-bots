from unittest.mock import PropertyMock, patch

from bots.death_first_search_episode_1.challengelibs.game_loop import GameLoop


def test_replay_turn():
    with patch("bots.death_first_search_episode_1.challengelibs.game_loop.input", side_effect=['4 4 1', '1 3', '2 3', '0 1', '0 2', '3', '0']):
        GameLoop.RUNNING = PropertyMock(side_effect=[True, False])
        GameLoop().start()

