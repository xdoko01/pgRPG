
from pyrpg.core.config import KEYS, show
import pygame

def _trans_key_from_str(key_string):
	""" Returns pygame code of the key.
	"""
	return eval('pygame.' + key_string) if key_string is not None else pygame.K_CLEAR # Clear key should not be currently supported so ideal to use


# Iterate through key schemas defined in config file and assign the keyboard keys
k_profile = dict()
for key_profile in KEYS.copy().get('KEY_PROFILES', []):
	k_profile.update({key_profile: {k: _trans_key_from_str(v) for k, v in KEYS[key_profile].items()}})
KEYS["K_PROFILE"] = k_profile

# Clear the original pre-conversion config
for profile in KEYS["KEY_PROFILES"]: del(KEYS[profile])
del(KEYS["KEY_PROFILES"])

# Convert the rest of the keys
for k,v in KEYS.items(): KEYS[k] = _trans_key_from_str(v) if k not in ("K_PROFILE") else KEYS[k]

show(KEYS)