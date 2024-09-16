from pyrpg.core.config import FILEPATHS, show
from pathlib import Path

# Convert filepaths to Paths
for path_name, path_rel in FILEPATHS.copy().items():
    FILEPATHS[path_name] = Path(FILEPATHS["GAME_PATH"], path_rel) if path_name not in ("GAME_PATH", "PYRPG_PATH") else Path(path_rel)

show(FILEPATHS)