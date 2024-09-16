from pyrpg.core.config.filepaths import FILEPATHS
from pyrpg.core.config import LOGGING, show

# Iterate through handlers and whenever there is filename key, add the FILEPATHS["GAME_PATH"] to it
for handler, data in LOGGING.get("handlers", {}).copy().items():
    filename = data.get("filename", None)
    if filename: LOGGING["handlers"][handler]["filename"] = str(FILEPATHS["GAME_PATH"]) + "/" + filename

# Initiate the logging based on configuration
import logging.config
from pyrpg.core.config import LOGGING
logging.config.dictConfig(LOGGING)
show(LOGGING)
