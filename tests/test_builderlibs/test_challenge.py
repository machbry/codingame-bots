import pytest

from builderlibs.challenge import ChallengeFolder


@pytest.fixture(scope="session")
def create_challenge_folder(unbuilt_bots_parent):

    folders_made = []

    def _create_challenge_folder(name: str, make: bool = False):
        challenge_folder = ChallengeFolder(name=name, parent=unbuilt_bots_parent)
        if make:
            challenge_folder.make()
            folders_made.append(challenge_folder)
        return challenge_folder

    yield _create_challenge_folder

    [folder.destroy() for folder in folders_made]


def test_challenge(create_challenge_folder):
    create_challenge_folder(name="test_challenge", make=True)
