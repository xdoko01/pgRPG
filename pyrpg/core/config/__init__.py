
# Initiate pygame
# This is very early statement because this package is imported before the game is started. 
# It ensures that pygame timer is available and also screen can be initialized using DISPLAY configuration.
import pygame
pygame.init()

# Where config defaults are stored
from pathlib import Path
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

def show(text: str, config: any) -> None:
    """Print nicely any config variable."""
    import pprint
    print(f'{text}')
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
    show("CONFIG_FILEPATH config", CONFIG_FILEPATH)

    # Read specific GAME config and basic PYRPG config for further merging
    from pyrpg.functions import get_dict_from_file
    game_config_data = get_dict_from_file(filepath=CONFIG_FILEPATH) 
    pyrpg_config_data = get_dict_from_file(filepath=PYRPG_DEFAULT_CONFIG_FILEPATH)

    # Process LOGGING - goes first in order to have logging for all config modules
    global LOGGING
    LOGGING = _prep_conf_logging(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="LOGGING"))
    import pyrpg.core.config.logging as l
    l.init(game_path=game_config_data["FILEPATHS"]["GAME_PATH"])
    show("LOGGING config:", LOGGING)

    # Process FILEPATHS - take every path and add the game directory to it
    # Must go first as paths are used in other configurations
    global FILEPATHS
    FILEPATHS = _prep_conf_filepaths(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="FILEPATHS"))
    import pyrpg.core.config.filepaths as fp
    fp.init()
    fp.convert_dict_conf_to_vars()
    #show("FILEPATHS config:", FILEPATHS)

    # Process DISPLAY - initiate pygame screen
    global DISPLAY
    DISPLAY =_prep_conf_display(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="DISPLAY"))
    import pyrpg.core.config.display as d
    d.init()
    d.convert_dict_conf_to_vars()
    #show("DISPLAY config", DISPLAY)

    # Process KEYS
    global KEYS
    KEYS =_prep_conf_keys(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="KEYS"))
    import pyrpg.core.config.keys as k
    k.init()
    k.convert_dict_conf_to_vars()
    #show("KEYS config", KEYS)

    # Process GUI
    global GUI
    GUI =_prep_conf_gui(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="GUI"))
    #show("GUI config", GUI)

    # Process GAME
    global GAME
    GAME =_prep_conf_game(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="GAME"))
    #show("GAME config", GAME)

    # Process MESSAGES
    global MESSAGES
    MESSAGES =_prep_conf_msgs(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="MESSAGES"))
    #show("MESSAGES config", MESSAGES)

    # Process MODULEPATHS
    global MODULEPATHS
    MODULEPATHS =_prep_conf_modulepaths(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="MODULEPATHS"))
    #show("MODULEPATHS config", MODULEPATHS)

    # Process FONTS - needs to have display already initiated
    global FONTS
    FONTS =_prep_conf_fonts(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="FONTS"))
    import pyrpg.core.config.fonts as fonts
    fonts.init()
    fonts.convert_dict_conf_to_vars()
    #show("FONTS config", FONTS)

    # Process FRAMES - needs to have display already initiated
    global FRAMES
    FRAMES =_prep_conf_frames(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="FRAMES"))
    import pyrpg.core.config.frames as frames
    frames.init()
    frames.convert_dict_conf_to_vars()
    #show("FRAMES config", FRAMES)

    # Process CONSOLE - must be the last because internally it is importing pyrpg.main module that is using some KEYS configurations that 
    # must be already ready
    global CONSOLE
    CONSOLE =_prep_conf_console(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="CONSOLE"))
    import pyrpg.core.config.console as c
    c.init()
    #show("CONSOLE config", CONSOLE)


def _merge_conf(default_config: dict, game_config: dict, conf_key: str) -> dict:
    """Merge configs from 2 dictionaries for a given conf key.
    Default config is overwritten by particular game config.
    """
    from pyrpg.functions import merge_dicts
    return merge_dicts(default_config.get(conf_key, dict()), game_config.get(conf_key, dict()))
    #return {**default_config.get(conf_key, dict()), **game_config.get(conf_key, dict())}

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
