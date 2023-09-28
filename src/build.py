from pathlib import Path
from argparse import ArgumentParser

from builderlibs.challenge import ChallengeFolder


ROOT = Path(__file__).parent.parent.resolve()
BOTS_DIRECTORY = ROOT / "bots"
BOTLIBS_DIRECTORY = ROOT / "botlibs"


parser = ArgumentParser()
parser.add_argument("-c", "--challenge_name", type=str)
parser.add_argument("-m", "--make", type=bool, default=True)
parser.add_argument("-d", "--destroy", type=bool, default=False)
arguments = parser.parse_args().__dict__

challenge_name = arguments["challenge_name"]
make_challenge = arguments["make"]
destroy_challenge = arguments["destroy"]

challenge_folder = ChallengeFolder(name=challenge_name, parent=BOTS_DIRECTORY)
if make_challenge:
    challenge_folder.make()
if destroy_challenge:
    if challenge_folder.exists():
        challenge_folder.destroy(force_destroy=False)
else:
    challenge_source = challenge_folder.aggregate_to_source(local_packages_paths=[BOTLIBS_DIRECTORY])
    with open(BOTS_DIRECTORY / (challenge_name + ".py"), "w") as f:
        f.write(challenge_source)
