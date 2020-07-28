''' Config module loading all related game configs
'''
########################################################
### Default configuration
########################################################

CONFIG_FILE = "experiments/ecs/config.json"

FPS = 120
MOVE_SPEED = 120 # in px per second
TILE_RES = 64
DEAD_TIME_TO_DISAPPEAR = 10000 # in ms

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

# Override PATHS with config paths
PATHS = {**PATHS, **config_data.get('paths', {})}

# Override DEBUG with config debug
DEBUG = {**DEBUG, **config_data.get('debug', {})}

# Override PROCESSORS with config processors
PROCESSORS = [*PROCESSORS, *config_data.get('processors', [])]

# Override GAME config with data from config file
FPS = config_data.get('fps', FPS)
MOVE_SPEED = config_data.get('move_speed', MOVE_SPEED)
TILE_RES = config_data.get('tile_res', TILE_RES)
DEAD_TIME_TO_DISAPPEAR = config_data.get('dead_time_to_disappear', DEAD_TIME_TO_DISAPPEAR)