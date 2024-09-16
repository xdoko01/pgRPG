from pyrpg.core.config import FILEPATHS, show
from pathlib import Path

# Convert filepaths to Paths
for path_name, path_rel in FILEPATHS.copy().items():
    FILEPATHS[path_name] = Path(FILEPATHS["GAME_PATH"], path_rel) if path_name not in ("GAME_PATH", "PYRPG_PATH") else Path(path_rel)

show(FILEPATHS)

# Add access to FILEPATHS dictionary keys as variables of this module
# Now it is able to get the configuration as follows:
# from pyrpg.core.config.filepaths import GAME_PATH
#
# Without this, you would always need to use the following way
# from pyrpg.core.config. filepaths import FILEPATHS
# GAME_PATH = FILEPATHS["GAME_PATH"]
globals().update((k,v) for k, v in FILEPATHS.items())