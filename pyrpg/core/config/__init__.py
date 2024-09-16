from pathlib import Path

# Where config defaults are stored
PYRPG_DEFAULT_CONFIG_FILEPATH = Path("pyrpg/core/config/defaults.jsonc")

# Where game configs are stored
CONFIG_FILEPATH = None

# Global dictionaries holding all configurations
LOGGING = dict()
CONSOLE = dict()
DISPLAY = dict()
GUI = dict()
KEYS = dict()
FILEPATHS = dict()
GAME = dict()
MESSAGES = dict()
MODULEPATHS = dict()
FONTS = dict()
FRAMES = dict()

def show(config):
    import pprint
    print(f'PRINTING ...')
    pprint.pprint(config)

def reload() -> None:
    """ Reloads the configuration based on up-to-date data
    present in default and given configuration file.
    """
    
    if CONFIG_FILEPATH: 
        load(config_file=CONFIG_FILEPATH)

def load(config_file: str) -> None:
    """ Loads configuration into global dictionary CONFIG as
    a merge of defaults.jsonc and given configuration file.
    """

    # We want to remember the location of config file
    global CONFIG_FILEPATH
    CONFIG_FILEPATH = Path(config_file)
    show(CONFIG_FILEPATH)

    # Read specific GAME config and basic PYRPG config for further merging
    from pyrpg.functions import get_dict_from_file
    game_config_data = get_dict_from_file(filepath=CONFIG_FILEPATH) 
    pyrpg_config_data = get_dict_from_file(filepath=PYRPG_DEFAULT_CONFIG_FILEPATH)

    # Process LOGGING
    global LOGGING
    LOGGING = _prep_conf_logging(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="LOGGING"))

    # Process FILEPATHS - take every path and add the game directory to it
    global FILEPATHS
    FILEPATHS = _prep_conf_filepaths(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="FILEPATHS"))

    # Process DISPLAY
    global DISPLAY
    DISPLAY =_prep_conf_display(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="DISPLAY"))

    # Process CONSOLE
    global CONSOLE
    CONSOLE =_prep_conf_console(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="CONSOLE"))

    # Process KEYS
    global KEYS
    KEYS =_prep_conf_keys(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="KEYS"))

    # Process GUI
    global GUI
    GUI =_prep_conf_gui(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="GUI"))

    # Process GAME
    global GAME
    GAME =_prep_conf_game(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="GAME"))

    # Process MESSAGES
    global MESSAGES
    MESSAGES =_prep_conf_msgs(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="MESSAGES"))

    # Process MODULEPATHS
    global MODULEPATHS
    MODULEPATHS =_prep_conf_modulepaths(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="MODULEPATHS"))

    # Process FONTS
    global FONTS
    FONTS =_prep_conf_fonts(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="FONTS"))

    # Process FRAMES
    global FRAMES
    FRAMES =_prep_conf_frames(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="FRAMES"))


def _merge_conf(default_config: dict, game_config: dict, conf_key: str) -> dict:
    """Merge configs from 2 dictionaries for a given conf key.
    Default config is overwritten by particular game config.
    """
    return {**default_config.get(conf_key, dict()), **game_config.get(conf_key, dict())}

def _prep_conf_filepaths(filepaths_config: dict) -> dict:
    """ Prepare all necessary logging configurations.
    """
    # Any necessary translation would go here. Now not needed.
    return filepaths_config

def _prep_conf_logging(logging_config: dict) -> dict:
    """ Prepare all necessary logging configurations.
    """
    # Any necessary translation would go here. Now not needed.
    return logging_config

def _prep_conf_display(display_config: dict) -> dict:
    """ Prepare global DISPLAY dictionary with configurations.
    """
    display_config["WIDTH"] = display_config["RESOLUTION"][0]
    display_config["HEIGHT"] = display_config["RESOLUTION"][1]

    return display_config

def _prep_conf_console(console_config: dict) -> dict:
    """ Prepare all necessary console configurations.
    """
    # Any necessary translation would go here. Now not needed.
    return console_config

def _prep_conf_keys(keys_config: dict) -> dict:
    """ Prepare all necessary keys configurations.
    """
    # Any necessary translation would go here. Now not needed.
    return keys_config

def _prep_conf_gui(gui_config: dict) -> dict:
    """ Prepare all necessary gui configurations.
    """
    # Any necessary translation would go here. Now not needed.
    return gui_config

def _prep_conf_game(game_config: dict) -> dict:
    """ Prepare all necessary game configurations.
    """
    # Any necessary translation would go here. Now not needed.
    return game_config

def _prep_conf_msgs(msgs_config: dict) -> dict:
    """ Prepare all necessary messages configurations.
    """
    # Any necessary translation would go here. Now not needed.
    return msgs_config

def _prep_conf_modulepaths(modulepaths_config: dict) -> dict:
    """ Prepare all necessary modulepaths configurations.
    """
    # Any necessary translation would go here. Now not needed.
    return modulepaths_config

def _prep_conf_fonts(fonts_config: dict) -> dict:
    """ Prepare all necessary fonts configurations.
    """
    # Any necessary translation would go here. Now not needed.
    # Cannot create the BitmaFont object here as pygame.display is not initiated in init config
    # which is happening before the GUI manager is initiated.
    return fonts_config

def _prep_conf_frames(frames_config: dict) -> dict:
    """ Prepare all necessary frames configurations.
    """
    # Any necessary translation would go here. Now not needed.
    # Cannot create the BitmapFrame object here as pygame.display is not initiated in init config
    # which is happening before the GUI manager is initiated.
    return frames_config
