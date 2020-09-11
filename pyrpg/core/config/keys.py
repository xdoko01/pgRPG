import pygame

def translate_key_from_str(key_string):
	''' Returns code of the key
	'''
	return eval('pygame.' + key_string) if key_string is not None else pygame.K_CLEAR # Clear key should not be currently supported so ideal to use

''' If some part of game requests controlling by the keyboard, it can import
keys module and reference the module variable holding the key value based on
default or json configuration.

E.g.
import pyrpg.core.config.keys as keys
player_1_up_key = keys.K_PROFILE['player1']['up']
'''

# Load definition of keyboard keys from config
from .config import KEYS

# Dictionary holding all key profiles for moving of characters
K_PROFILE = {}

# Iterate through key schemas defined in config file and assign the keyboard keys
for key_profile in KEYS.get('key_profiles', []):
	K_PROFILE.update({key_profile : {k: translate_key_from_str(v) for k, v in KEYS[key_profile].items()}})

# Game management hot keys
K_CONSOLE_TOGGLE = translate_key_from_str(KEYS['console_toggle'])
K_SAVE_GAME = translate_key_from_str(KEYS['save_game'])
K_LOAD_GAME = translate_key_from_str(KEYS['load_game'])
K_PAUSE_GAME = translate_key_from_str(KEYS['pause_game'])


# Game menu navigation keys
K_NAV_UP = translate_key_from_str(KEYS['nav_up'])
K_NAV_DOWN = translate_key_from_str(KEYS['nav_down'])
K_NAV_LEFT = translate_key_from_str(KEYS['nav_left'])
K_NAV_RIGHT = translate_key_from_str(KEYS['nav_right'])
K_SUBMIT = translate_key_from_str(KEYS['submit'])
