from pyrpg.core.config import LOGGING

_INIT: bool = False

def get_init() -> bool:
    """Return True, if console config is already initiated.
    """
    return _INIT

#def init(game_path: str) -> None:
def init(logging_config: dict) -> None:

    # Iterate through handlers and whenever there is filename key, add the FILEPATHS["GAME_PATH"] to it
    #for handler, data in LOGGING.get("handlers", {}).copy().items():
    #    filename = data.get("filename", None)
    #    if filename: LOGGING["handlers"][handler]["filename"] = game_path + "/" + filename

    # Initiate the logging based on configuration
    #print(f'{logging_config=}')

    import logging.config
    logging.config.dictConfig(logging_config)

    global _INIT
    _INIT = True

