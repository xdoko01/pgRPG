from pyrpg.core.config import LOGGING


def init(game_path: str) -> None:
    # Iterate through handlers and whenever there is filename key, add the FILEPATHS["GAME_PATH"] to it
    for handler, data in LOGGING.get("handlers", {}).copy().items():
        filename = data.get("filename", None)
        if filename: LOGGING["handlers"][handler]["filename"] = game_path + "/" + filename

    # Initiate the logging based on configuration
    import logging.config
    logging.config.dictConfig(LOGGING)
