
# Init logging config
import logging
logger = logging.getLogger(__name__)

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

# Reference to the main game module
MAIN_GAME_MODULE = None

# Global dictionaries holding all configurations
PYRPG: dict = {}
LOGGING: dict = {}
CONSOLE: dict = {}
DISPLAY: dict = {}
GUI: dict = {}
SOUND: dict = {}
KEYS: dict = {}
FILEPATHS: dict = {}
GAME: dict = {}
MESSAGES: dict = {}
MODULEPATHS: dict = {}
FONTS: dict = {}
FRAMES: dict = {}
STATES: dict = {}

# Console reference
cons = None


def show(config: any, text: str="") -> None:
    """Print nicely any config variable."""
    import pprint
    print(f'{text}')
    pprint.pprint(config)


def load(config_file: str=None, hide_res: bool=True) -> None:
    """ Loads configuration into global dictionary CONFIG as
    a merge of defaults.jsonc and given configuration file.

    Can be used repeatedly for reloading of config after change
    in config jsons during the game.
    """

    # If config file is specified, always reload config from this file
    if config_file is not None:
        global CONFIG_FILEPATH
        CONFIG_FILEPATH = Path(config_file)
        hide_res or show(text="CONFIG_FILEPATH config", config=CONFIG_FILEPATH)
    
    # config file not specified, use the config file configured during the latest load
    assert CONFIG_FILEPATH is not None, f"No config file loaded yet"

    # Read specific GAME config and basic PYRPG config for further merging
    from pyrpg.functions import get_dict_from_file
    game_config_data = get_dict_from_file(filepath=CONFIG_FILEPATH) 
    pyrpg_config_data = get_dict_from_file(filepath=PYRPG_DEFAULT_CONFIG_FILEPATH)

    # Process PYRPG - general config of the framework
    global PYRPG
    PYRPG = _prep_conf_pyrpg(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="PYRPG"))
    hide_res or show(text="PYRPG config:", config=PYRPG)

    # Process FILEPATHS - take every path and add the game directory to it
    # Must go first as paths are used in other configurations
    global FILEPATHS
    FILEPATHS = _prep_conf_filepaths(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="FILEPATHS"))
    hide_res or show(text="FILEPATHS config:", config=FILEPATHS)

    # Process DISPLAY - initiate pygame screen
    global DISPLAY
    DISPLAY =_prep_conf_display(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="DISPLAY"))
    hide_res or show(text="DISPLAY config", config=DISPLAY)

    # Process KEYS
    global KEYS
    KEYS =_prep_conf_keys(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="KEYS"))
    hide_res or show(text="KEYS config", config=KEYS)

    # Process GUI
    global GUI
    GUI =_prep_conf_gui(
        gui_config=_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="GUI"),
        display_config=DISPLAY.copy()
    )
    hide_res or show(text="GUI config", config=GUI)

    # Process SOUND
    global SOUND
    SOUND =_prep_conf_sound(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="SOUND"))
    hide_res or show(text="SOUND config", config=SOUND)

    # Process GAME
    global GAME
    GAME =_prep_conf_game(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="GAME"))
    hide_res or show(text="GAME config", config=GAME)

    # Process MESSAGES
    global MESSAGES
    MESSAGES =_prep_conf_msgs(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="MESSAGES"))
    hide_res or show(text="MESSAGES config", config=MESSAGES)

    # Process MODULEPATHS
    global MODULEPATHS
    MODULEPATHS =_prep_conf_modulepaths(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="MODULEPATHS"))
    hide_res or show(text="MODULEPATHS config", config=MODULEPATHS)

    # Process FONTS - needs to have display already initiated
    global FONTS
    FONTS =_prep_conf_fonts(
        fonts_config=_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="FONTS"),
        filepaths_config=FILEPATHS.copy()
        )
    hide_res or show(text="FONTS config", config=FONTS)

    # Process FRAMES - needs to have display already initiated
    global FRAMES
    FRAMES =_prep_conf_frames(
        frames_config=_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="FRAMES"),
        filepath_config=FILEPATHS.copy()
        )
    hide_res or show(text="FRAMES config", config=FRAMES)

    # Process CONSOLE - must be the last because internally it is importing pyrpg module that is using some KEYS configurations that 
    # must be already ready
    global CONSOLE
    CONSOLE =_prep_conf_console(
        console_config=_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="CONSOLE"),
        filepaths_config=FILEPATHS.copy()
        )
    hide_res or show(text="CONSOLE config", config=CONSOLE)

    # Process LOGGING - must go after console as logging to console can be part of the configuration
    global LOGGING
    LOGGING = _prep_conf_logging(
        logging_config=_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="LOGGING"),
        filepaths_config=FILEPATHS.copy()
        )
    hide_res or show(text="LOGGING config:", config=LOGGING)

    # Process LOGGING - must go after console as logging to console can be part of the configuration
    global STATES
    STATES = _prep_conf_states(_merge_conf(default_config=pyrpg_config_data, game_config=game_config_data, conf_key="STATES"))
    hide_res or show(text="STATES config:", config=STATES)

def init(main_module=None, states: bool=True) -> None:
    """Initiate all necessary configuration - logging, console, display,...
    Create configuration objects.
    """

    # If config file is specified, always reload config from this file
    if main_module is not None:
        global MAIN_GAME_MODULE
        MAIN_GAME_MODULE = main_module
    
    # config file not specified, use the config file configured during the latest load
    assert MAIN_GAME_MODULE is not None, f"No main game module specified"

    _init_display()
    _init_console()
    _init_logging()

    _init_fonts()
    _init_frames()

    _init_gui()
    _init_sound()
    if states: _init_states()


def _merge_conf(default_config: dict, game_config: dict, conf_key: str) -> dict:
    """Merge configs from 2 dictionaries for a given conf key.
    Default config is overwritten by particular game config.
    """
    from pyrpg.functions import merge_dicts
    return merge_dicts(default_config.get(conf_key, dict()), game_config.get(conf_key, dict()))

### PREPS

def _prep_conf_pyrpg(pyrpg_config: dict) -> dict:
    """ Prepare all necessary pyrpg configurations.
    """
    return pyrpg_config

def _prep_conf_filepaths(filepaths_config: dict) -> dict:
    """ Prepare all necessary filepaths configurations.
    """
    # Convert filepaths to Paths
    for path_name, path_rel in filepaths_config.copy().items():
        filepaths_config[path_name] = Path(filepaths_config["GAME_PATH"], path_rel) if path_name not in ("GAME_PATH", "PYRPG_PATH") else Path(path_rel)

    return filepaths_config

def _prep_conf_logging(logging_config: dict, filepaths_config: dict) -> dict:
    """ Prepare all necessary logging configurations.
    """

    # Iterate through handlers and whenever there is filename key, add the FILEPATHS["GAME_PATH"] to it
    for handler, data in logging_config.get("handlers", {}).copy().items():
        filename = data.get("filename", None)
        if filename: logging_config["handlers"][handler]["filename"] = str(filepaths_config["GAME_PATH"]) + "/" + filename

    return logging_config

def _prep_conf_display(display_config: dict) -> dict:
    """ Prepare global DISPLAY dictionary with configurations.
    """

    from functools import namedtuple
    Resolution = namedtuple("Resolution", ["width", "height"])

    # Set automatically to native resolution if required
    if display_config["RESOLUTION"] == "DEFAULT":
        display_config["RESOLUTION"] = Resolution(pygame.display.Info().current_w, pygame.display.Info().current_h)
    else:
        display_config["RESOLUTION"] = Resolution(display_config["RESOLUTION"][0], display_config["RESOLUTION"][1])

    # Set the best bitdepth (default)
    if display_config["BITDEPTH"] == "DEFAULT": display_config["BITDEPTH"] = 0

    return display_config

def _prep_conf_console(console_config: dict, filepaths_config: dict) -> dict:
    """ Prepare all necessary console configurations.
    """

    # Fix the relative paths so that they are directing into correct folders
    if console_config.get('global', {}).get('bck_image', None): console_config.get('global').update({'bck_image' : filepaths_config["IMAGE_PATH"] / console_config.get('global').get('bck_image')})
    if console_config.get('header', {}).get('bck_image', None): console_config.get('header').update({'bck_image' : filepaths_config["IMAGE_PATH"] / console_config.get('header').get('bck_image')})
    if console_config.get('footer', {}).get('bck_image', None): console_config.get('footer').update({'bck_image' : filepaths_config["IMAGE_PATH"] / console_config.get('footer').get('bck_image')})
    if console_config.get('header', {}).get('font_file', None): console_config.get('header').update({'font_file' : filepaths_config["FONT_PATH"] / console_config.get('header').get('font_file')})
    if console_config.get('output', {}).get('font_file', None): console_config.get('output').update({'font_file' : filepaths_config["FONT_PATH"] / console_config.get('output').get('font_file')})
    if console_config.get('input', {}).get('font_file', None): console_config.get('input').update({'font_file' : filepaths_config["FONT_PATH"] / console_config.get('input').get('font_file')})
    if console_config.get('footer', {}).get('font_file', None): console_config.get('footer').update({'font_file' : filepaths_config["FONT_PATH"] / console_config.get('footer').get('font_file')})

    # Add console_script_path to the console config
    console_config.get('global').update({'script_path': filepaths_config["CONSOLE_SCRIPT_PATH"]})

    # For now just text, reference is created in console manager, during creation of the Console entity
    console_config["CLI_MODULE"] = console_config.get("global").get("cli_module", "pyrpg")

    return console_config

def _prep_conf_keys(keys_config: dict) -> dict:
    """ Prepare all necessary keys configurations.
    """

    def _trans_key_from_str(key_string):
        """ Returns pygame code of the key.
        """
        import pygame
        return eval('pygame.' + key_string) if key_string is not None else pygame.K_CLEAR # Clear key should not be currently supported so ideal to use

    # Iterate through key schemas defined in config file and assign the keyboard keys
    k_profile = dict()
    for key_profile in keys_config.copy().get('KEY_PROFILES', []):
        k_profile.update({key_profile: {k: _trans_key_from_str(v) for k, v in keys_config[key_profile].items()}})
    keys_config["K_PROFILE"] = k_profile

    # Clear the original pre-conversion config
    for profile in keys_config["KEY_PROFILES"]: del(keys_config[profile])
    del(keys_config["KEY_PROFILES"])

    # Convert the rest of the keys
    for k,v in keys_config.items(): keys_config[k] = _trans_key_from_str(v) if k not in ("K_PROFILE") else keys_config[k]

    return keys_config

def _prep_conf_gui(gui_config: dict, display_config: dict) -> dict:
    """ Prepare all necessary gui configurations.
    """
    gui_config["DLG_DIM_PX"] = [
        display_config["RESOLUTION"][0] * gui_config["GUI_WINDOW_RATIO"], 
        display_config["RESOLUTION"][1] * gui_config["GUI_WINDOW_RATIO"]
    ]
    gui_config["DLG_START_PX"] = [
        (display_config["RESOLUTION"][0] - gui_config["DLG_DIM_PX"][0]) / 2, 
        (display_config["RESOLUTION"][1]- gui_config["DLG_DIM_PX"][1]) / 2
    ]

    # Any necessary translation would go here. Now not needed.
    return gui_config

def _prep_conf_sound(sound_config: dict) -> dict:
    """ Prepare all necessary gui configurations.
    """
    # Any necessary translation would go here. Now not needed.
    return sound_config

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

def _prep_conf_fonts(fonts_config: dict, filepaths_config: dict) -> dict:
    """ Prepare all necessary fonts configurations.
    """
    # Any necessary translation would go here. Now not needed.
    # Cannot create the BitmaFont object here as pygame.display is not initiated in init config
    # which is happening before the GUI manager is initiated.

    # Font for in-game dialog bubbles
    fonts_config["GAME_DEBUG_FONT"] = filepaths_config["FONT_PATH"] / fonts_config["GAME_DEBUG_FONT"]
    fonts_config["PLAYER_TALK_FONT"] = filepaths_config["FONT_PATH"] / fonts_config["PLAYER_TALK_FONT"]

    # Font for in-game messages such as 'item picked'
    fonts_config["GAME_MSG_FONT"] = filepaths_config["FONT_PATH"] / fonts_config["GAME_MSG_FONT"]

    # Font or GUI manager
    fonts_config["GUI_MANAGER_FONT"] = filepaths_config["FONT_PATH"] / fonts_config["GUI_MANAGER_FONT"]

    return fonts_config

def _prep_conf_frames(frames_config: dict, filepath_config: dict) -> dict:
    """ Prepare all necessary frames configurations.
    """
    # Any necessary translation would go here. Now not needed.
    # Cannot create the BitmapFrame object here as pygame.display is not initiated in init config
    # which is happening before the GUI manager is initiated.

    frames_config["PLAYER_TALK_FRAME"] = filepath_config["FRAME_PATH"] / frames_config["PLAYER_TALK_FRAME"]
    frames_config["GAME_DEBUG_FRAME"] = filepath_config["FRAME_PATH"] / frames_config["GAME_DEBUG_FRAME"]

    return frames_config

def _prep_conf_states(states_config: dict) -> dict:
    """ Prepare all necessary states configurations.
    """
    return states_config

### INIT

def _init_logging() -> None:
    import logging.config
    logging.config.dictConfig(LOGGING)


def _init_display() -> None:
    global display

    if DISPLAY.get("WINDOW") is None:
        DISPLAY["WINDOW"] = pygame.display.set_mode(
            size=DISPLAY["RESOLUTION"],
            flags=pygame.FULLSCREEN if DISPLAY["FULLSCREEN"] else 0,
            depth=DISPLAY["BITDEPTH"]
        )

        # Set window title
        pygame.display.set_caption(DISPLAY["WIN_TITLE"])

    else:
        #Resize the resolution and/or switch to fullscreen 

        # copy the surface
        temp_surf = pygame.display.get_surface().convert()
        cursor = pygame.mouse.get_cursor()

        # change the mode
        DISPLAY["WINDOW"] = pygame.display.set_mode(
            size=DISPLAY["RESOLUTION"],
            flags=pygame.FULLSCREEN if DISPLAY["FULLSCREEN"] else 0,
            depth=DISPLAY["BITDEPTH"]
        )
        # Set window title
        pygame.display.set_caption(DISPLAY["WIN_TITLE"])
        pygame.mouse.set_cursor(*cursor)
        pygame.key.set_mods(0) # ???

        # paste to the copy to the new window
        DISPLAY["WINDOW"].blit(temp_surf, (0, 0))

        print("Display reloaded")

def _init_console(app_module: str=None) -> None:
    from pyrpg.utils import Console
    global cons
    
    if cons is None:
        import pyrpg.core.config.console # because this module is used for functions displaying info on console
        # Load the console from utils
        cons = Console(
            #app=import_module(CONSOLE["CLI_MODULE"]), #Carefull this triggers import of the module!!!
            app=None, # set the main module as entry point to the console
            lua_runtime=None,
            width=DISPLAY["RESOLUTION"].width,
            config=CONSOLE
        )

        # try to load CLI module if possible
        cons.set_cli_app(app_module if app_module is not None else CONSOLE["CLI_MODULE"])

    else:

        cons.init(
            app=None, 
            lua_runtime=None,
            width=DISPLAY["RESOLUTION"][0],
            config=CONSOLE
        )

        # reload the game CLI entry point module
        cons.set_cli_app(app_module if app_module is not None else CONSOLE["CLI_MODULE"])

def _init_fonts() -> None:
    import pyrpg.utils as utils# for BitmapFont class
    from pygame import Color# for pygame.Color

    # Font for in-game dialog bubbles
    FONTS["GAME_DEBUG_FONT_OBJ"] = utils.BitmapFont(FONTS["GAME_DEBUG_FONT"], color=FONTS.get("GAME_DEBUG_FONT_COLOUR"))
    FONTS["PLAYER_TALK_FONT_OBJ"] = utils.BitmapFont(FONTS["PLAYER_TALK_FONT"], color=FONTS.get("PLAYER_TALK_FONT_COLOUR"))

    # Font for in-game messages such as 'item picked'
    FONTS["GAME_MSG_FONT_OBJ"]= utils.BitmapFont(FONTS["GAME_MSG_FONT"], color=FONTS.get("GAME_MSG_FONT_COLOUR"))

    # Font or GUI manager
    FONTS["GUI_MANAGER_FONT_OBJ"]= utils.BitmapFont(FONTS["GUI_MANAGER_FONT"], color=FONTS.get("GUI_MANAGER_FONT_COLOUR"))

def _init_frames() -> None:
    import pyrpg.utils as utils # for BitmapFrame class
    import pygame # for pygame.Color

    FRAMES["PLAYER_TALK_FRAME_OBJ"] = utils.BitmapFrame(FRAMES["PLAYER_TALK_FRAME"], color=FRAMES.get("PLAYER_TALK_FRAME_COLOUR"))
    FRAMES["GAME_DEBUG_FRAME_OBJ"] = utils.BitmapFrame(FRAMES["GAME_DEBUG_FRAME"], color=FRAMES.get("GAME_DEBUG_FRAME_COLOUR"))

def _init_sound() -> None:
    import pyrpg.core.config.sound as s
    s.init()

def _init_states() -> None:
    import pyrpg.core.config.states as st
    st.init(states=STATES)

def _init_gui() -> None:
    """GUI needs sound and states"""
    # recalculate dialog parameters so that correct dialogs are shown after the
    # resolution is changed during the game (and config.init() is called again)
    global GUI
    GUI = _prep_conf_gui(gui_config=GUI, display_config=DISPLAY)

    import pyrpg.core.config.gui as g
    g.init_background_animation(display=DISPLAY, filepaths=FILEPATHS, gui_conf=GUI)
    g.init_gui(display=DISPLAY, fonts=FONTS)



if __name__ == "__main__":
    load(config_file="example_game/config.jsonc")
    load(config_file="example_game/config.jsonc")
    load(hide_res=False)
    #init()
    #init()