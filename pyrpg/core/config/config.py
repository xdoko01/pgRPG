''' Config module loading all related game configs
'''
########################################################
### Default configuration
########################################################

CONFIG_FILE = "config.json"

MOVE_SPEED = 120 # in px per second
TILE_RES = 64
DEAD_TIME_TO_DISAPPEAR = 10000 # in ms
MENU_BACKGROUND_ANIMATION_DELAY = 130 # in ms

''' MESSAGES contain format of message that should be generated
upon game event generation. Such message is then displayed on 
the game window. If event is not represented as a key in 'on_events'
dictionary it means that such event is not generating any message (for
example collision - that would generat too much unncesessary messages)
'''
MESSAGES = {
        'on_events' : {
            'TELEPORTATION' : ['Entity {} was teleported using teleport {}.', ['generator_obj', 'other_obj']],
            'ITEM_PICKUP' : ['Entity {} was picked up by entity {}.', ['generator_obj', 'other_obj']],
            'WEARABLE_WEARED' : ['Entity {} weared {}.', ['generator_obj', 'other_obj']],
            'WEAPON_ARMED' : ['Entity {} picked up weapon {}.', ['other_obj', 'generator_obj']],
            'AMMO_PACK_ARMED' : ['Entity {} picked up ammo pack {}.', ['other_obj', 'generator_obj']],
            'AMMO_PACK_DISARMED' : ['Ammo pack {} was disarmed from {}.', ['generator_obj', 'other_obj']],
            'DAMAGE' : ['Entity {} was hit by entity {}.', ['generator_obj', 'other_obj']],
            'SCORE' : ['Entity {} has scored.', ['generator_obj']],
            'KILL' : ['Entity {} was killed by entity {}.', ['other_obj', 'generator_obj']],
            'QUEST_START' : ['Quest {} has started.', ['generator_obj']],
            'PHASE_START' : ['Phase {} has started.', ['generator_obj']]
        },
        'default_ttl' : 2000
}

''' KEYS contain mapping of functionalities to keyboard keys.
It also defines key_schemas - set of keys for manipulating the
characters.
'''
KEYS = {

    # List of key profiles for manipulating of characters
    "key_profiles" : ["default", "key_controls_1", "key_controls_2", "key_controls_3", "key_controls_4"],

    # Default must be always present, it is used in controllable component
    "default" : {
        "up" : "K_UP",
        "down" : "K_DOWN",
        "left" : "K_LEFT",
        "right" : "K_RIGHT",
        "attack" : "K_z"
    },

    "key_controls_1" : {
        "up" : None,
        "down" : None,
        "left" : None,
        "right" : None,
        "attack" : None
    },

    "key_controls_2" : {
        "up" : None,
        "down" : None,
        "left" : None,
        "right" : None,
        "attack" : None
    },

    "key_controls_3" : {
        "up" : None,
        "down" : None,
        "left" : None,
        "right" : None,
        "attack" : None
    },

    "key_controls_4" : {
        "up" : None,
        "down" : None,
        "left" : None,
        "right" : None,
        "attack" : None
    },

    # Keys for game management
    "console_toggle" : None,
    "save_game" : None,
    "load_game" : None,
    "pause_game" : None,

    # Keys for navigating through menus
    "nav_up" : "K_UP",
    "nav_down" : "K_DOWN",
    "nav_left" : "K_LEFT",
    "nav_right" : "K_RIGHT",
    "submit" : "K_RETURN"

}

DISPLAY = {
    "resolution" : [640, 480],
    "bitdepth" : 32,
    "fullscreen" : False,
    "max_fps" : 120,
    "show_fps" : True
}

PATHS = {
    "font_path" : "pyrpg/resources/fonts/",
    "frame_path" : "pyrpg/resources/frames/",
    "dialog_path" : "pyrpg/resources/dialogs/",
    "model_path" : "pyrpg/resources/models/",
    "image_path" : "pyrpg/resources/images/",
    "quest_path" : "pyrpg/resources/quests/",
    "entity_path" : "pyrpg/resources/entities/",
    "map_path" : "pyrpg/resources/maps/",
    "sound_path" : "pyrpg/resources/sounds/",
    "log_path" : "pyrpg/logs/",
    "save_path" : "pyrpg/save/",
    "console_script_path" : "pyrpg/utils/scripts/",
    "menu_background_path" : "pyrpg/resources/images/menu_background/waterfall/",
    "script_module_path" : "pyrpg.core.scripts."
}

CONSOLE = {
    'global' : {
        'cli_module' : 'pyrpg.main',
        'bck_alpha' : 150,
        },
    'input' : {
        'font_file' : 'JackInput.ttf',
        'bck_alpha' : 0
        },
    'output' : {
        'font_file' : 'JackInput.ttf',
        'bck_alpha' : 0,
        'display_lines' : 20,
        'display_columns' : 100
        }
    }

DEBUG = {
    'show_health' : False,
    'show_state' : False,
    'show_weapons' : False,
    'show_wearables' : False,
    'show_inventory' : False,
    'show_labels' : False,
    'show_position' : False,
    'show_brain' : False,
    'show_collision' : False,
    'show_direction' : False,
    'show_map_screen_area' : False
}

LOGGING = {
    "version" : 1.0,
    "disable_existing_loggers": False,

    "formatters": {
        "console_short": {
            "format": "%(name)s - %(message)s"
        },
        "short": {
            "format": "%(filename)-45s - %(message)s"
        },
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "extra": {
            "format":"%(asctime)-2s %(levelname)-6s %(name)-30s %(filename)-15s %(funcName)-18s %(lineno)-6s %(message)s",
            "datefmt":"%m-%d %H:%M:%S"
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },
        "in_game_console": {
            "class": "logging.StreamHandler",
            "formatter": "console_short",
            "stream": "ext://pyrpg.core.managers.console_manager" # Module containing write function
        },
        "file_handler_proc": {
            "class": "logging.FileHandler",
            "formatter": "short",
            "filename": "pyrpg/logs/processors.log",
            "mode": "w",
            "encoding": "utf-8"
        },
        "null": {
            "class": "logging.NullHandler"
        }

    },

    "loggers" : {

        
        # Save all the logs from processor classes to the file
        "pyrpg.core.ecs.processors" : {
            "level" : "DEBUG", # Passes DEBUG and upper logs only, i.e. DEBUG, INFO, WARNING, ERROR, CRITICAL
            #"handlers" : ["file_handler_proc"], # uncomment to log all the processors
            "handlers" : ["null"],  # do not log to file for speed
            "propagate" : False # Do not send messages from these loggers to parent (root) logger
        },
        

        # Save all the logs other from processor classes to console
        "pyrpg" : {
            "level" : "INFO", # Passes INFO and upper logs only, i.e. INFO, WARNING, ERROR, CRITICAL
            #"level" : "DEBUG", # Passes DEBUG and upper logs only, i.e. DEBUG, INFO, WARNING, ERROR, CRITICAL
            "handlers" : ["in_game_console", "console"],
            "propagate" : False # Do not send messages from these loggers to parent (root) logger
        }
        

    },

    # Display all DEBUG - INFO - WARNING - ERROR - CRITICAL that are not covered by above loggers to console
    "root" : {
        "level" : "DEBUG",
        "handlers" : ["console"]
    }
}


########################################################
### Override with JSON configuration
########################################################

# Read config from config file
import json
import re # for removing C-style comments from JSON

try:
    with open(CONFIG_FILE, 'r') as config_file:
        json_config_data = config_file.read()
        config_data = json.loads(re.sub('//.*', '', json_config_data, flags=re.MULTILINE)) # Remove C-style comments before processing JSON
except FileNotFoundError:
    print(f"Config file '{CONFIG_FILE}' not found, using defaults.")
    config_data = {}

# Override MESSAGES with config messages
MSG_EVENT_FORMAT = {**MESSAGES.get('on_events'), **config_data.get('messages', {}).get('on_events', {})}
MSG_DEFAULT_TTL = config_data.get('messages', {}).get('default_ttl', MESSAGES.get('default_ttl'))

# Override KEYS with config keys
KEYS = {**KEYS, **config_data.get('keys', {})}

# Override DISPLAY with config display
DISPLAY = {**DISPLAY, **config_data.get('display', {})}

# Override PATHS with config paths
PATHS = {**PATHS, **config_data.get('paths', {})}

# Override CONSOLE with config console
CONSOLE = {**CONSOLE, **config_data.get('console', {})}

# Override DEBUG with config debug
DEBUG = {**DEBUG, **config_data.get('debug', {})}

# Override GAME config with data from config file
MOVE_SPEED = config_data.get('move_speed', MOVE_SPEED)
TILE_RES = config_data.get('tile_res', TILE_RES)
DEAD_TIME_TO_DISAPPEAR = config_data.get('dead_time_to_disappear', DEAD_TIME_TO_DISAPPEAR)
