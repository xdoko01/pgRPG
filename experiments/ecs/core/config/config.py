from collections import namedtuple # for Tile namedtuple used in the Model class
from pygame import Vector2 as vect # for width and height of the tile of the model
from pathlib import Path


FONT_PATH = Path('experiments/ecs/resources/fonts/')
MODEL_PATH = Path('experiments/ecs/resources/models/')
IMAGE_PATH = Path('experiments/ecs/resources/images/')
QUEST_PATH = Path('experiments/ecs/resources/quests/')
ENTITY_PATH = Path('experiments/ecs/resources/entities/')
MAP_PATH = Path('experiments/ecs/resources/maps/')
LOG_PATH = Path('experiments/ecs/logs/')
SAVE_PATH = Path('experiments/ecs/save/')

DEBUG = {
	'show_health' : True,
	'show_state' : True,
	'show_weapons' : True,
	'show_wearables' : True,
	'show_inventory' : True,
	'show_labels' : True,
	'show_position' : True,
	'show_brain' : True,
	'show_collision' : True,
	'show_direction' : True,
	'show_map_screen_area' : True
}
FPS = 120
MOVE_SPEED = 120 # in px per second
TILE_RES = 64

DEAD_TIME_TO_DISAPPEAR = 10000 # in ms
