''' Config module loading all related game configs
'''
########################################################
### Default configuration
########################################################

CONFIG_FILE = "experiments/ecs/config.json"

MOVE_SPEED = 120 # in px per second
TILE_RES = 64
DEAD_TIME_TO_DISAPPEAR = 10000 # in ms

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
			'WEAPON_ARMED' : ['Entity {} picked up weapon {}.', ['generator_obj', 'other_obj']],
			'DAMAGE' : ['Entity {} was hit.', ['other_obj']],
			'KILL' : ['Entity {} was killed.', ['other_obj']],
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
    "resolution" : [850, 850],
    "bitdepth" : 32,
    "fullscreen" : False,
    "max_fps" : 120,
    "show_fps" : True
}

PATHS = {
    "font_path" : "experiments/ecs/resources/fonts/",
    "frame_path" : "experiments/ecs/resources/frames/",
    "model_path" : "experiments/ecs/resources/models/",
    "image_path" : "experiments/ecs/resources/images/",
    "quest_path" : "experiments/ecs/resources/quests/",
    "entity_path" : "experiments/ecs/resources/entities/",
    "map_path" : "experiments/ecs/resources/maps/",
    "log_path" : "experiments/ecs/logs/",
    "save_path" : "experiments/ecs/save/"
}

CONSOLE = {
    'global' : {
        'cli_module' : None,
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

PROCESSORS = [
    'input_processor',
    'brain_processor',
    'command_processor',
    'linear_movement_processor',
    'movement_processor',
    'generate_projectiles_processor',
    'collision_map_processor',
    'collision_entity_generator_processor',
    'collision_damage_processor',
    'collision_teleport_processor',
    'collision_weapon_processor',
    'collision_wearable_processor',
    'collision_item_processor',
    'collision_entity_processor',
    'collision_deletion_processor',
    'game_events_processor',
    'update_camera_offset_processor',
    'render_model_anim_action_processor',
    'render_model_anim_update_processor',
    'render_background_processor',
    'render_camera_background_processor',
    'render_map_processor',
    'render_world_processor',
    'render_model_world_processor',
    'render_talk_processor',
    'render_debug_processor',
    'clear_temporary_entity_processor'
]

########################################################
### Override with JSON configuration
########################################################

# Read config from config file
import json

try:
    with open(CONFIG_FILE, 'r') as config_file:
        json_config_data = config_file.read()
        config_data = json.loads(json_config_data)
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

# Override PROCESSORS with config processors
PROCESSORS = [*PROCESSORS, *config_data.get('processors', [])]

# Override GAME config with data from config file
MOVE_SPEED = config_data.get('move_speed', MOVE_SPEED)
TILE_RES = config_data.get('tile_res', TILE_RES)
DEAD_TIME_TO_DISAPPEAR = config_data.get('dead_time_to_disappear', DEAD_TIME_TO_DISAPPEAR)
