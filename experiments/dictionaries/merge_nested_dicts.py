
""" Merge nested dictionaries.
  - config dict is being merged into default dict.
  - values in default dict are overwriten by config dict.
  - if values do not exist in config, default values are used.

  Idea:
    iterate through config keys
    - if the key does not exist in default
    - if yes, copy completely to merged
    - if key exists in default iterate throug default
        - take first key
        - test if key is dict
        - if not test if key exists in config
        - if yes put it to the merged dictionary
        - if yes, repeat recurrntly
        test if value is dictionary
"""
        
default = {
    "b": {
      "c": 1,
      "d": 2
    },
    "e": 3
  }

config = {
    "b": {
      "c": 111,
      "z": 5
    }
  }

"""
merged = {
    b: {
      c: 111,
      d: 2
      z: 5
    },
    e:3
  }
"""

def merge(orig: dict, new: dict) -> dict:
    """ Merge 2 dictionaries original and new, so that
        - if key exists in both, value from new i sused
        - if key exists only in default, key: value from default is used
        - if key exists only in new, key: value from new is used
    """
    merged = dict()

    # key exists in new but not in original
    for new_key in new: 
        if not orig.get(new_key):
            merged[new_key] = new[new_key] 

    for orig_key in orig:
        # check if exists in orig dict 
        ## if NOT
        if not new.get(orig_key): # exists in original but not in new -> add original to the merged dict
            merged[orig_key] = orig[orig_key]
        else: 
            # key exists in both original and new
            # if in the new dict the value is not dict - merge it
            if not isinstance(new[orig_key], dict):
                merged[orig_key] = new[orig_key]
            else: # the value is again dict
                merged[orig_key] = merge(orig[orig_key], new[orig_key])
    
    return merged

import pprint

print(f"{default=}")
print(f"{config=}")
merged = merge(orig=default, new=config)
print(f"{merged=}")
print({**default, **config})

default = {
        "ON_EVENT": {
            "TELEPORTATION": ["Entity {} was teleported using teleport {}.", ["generator_obj", "other_obj"]],
            "ITEM_PICKUP": ["Entity {} was picked up by entity {}.", ["generator_obj", "other_obj"]],
            "WEARABLE_WEARED": ["Entity {} weared {}.", ["generator_obj", "other_obj"]],
            "WEAPON_ARMED": ["Entity {} picked up weapon {}.", ["other_obj", "generator_obj"]],
            "AMMO_PACK_ARMED": ["Entity {} picked up ammo pack {}.", ["other_obj", "generator_obj"]],
            "AMMO_PACK_DISARMED": ["Ammo pack {} was disarmed from {}.", ["generator_obj", "other_obj"]],
            "DAMAGE": ["Entity {} was hit by entity {}.", ["generator_obj", "other_obj"]],
            "SCORE": ["Entity {} has scored.", ["generator_obj"]],
            "KILL": ["Entity {} was killed by entity {}.", ["other_obj", "generator_obj"]],
            "QUEST_START": ["Quest {} has started.", ["generator_obj"]],
            "PHASE_START": ["Phase {} has started.", ["generator_obj"]]
        },
        "DEFAULT_TTL_MS" : 2000
    }

config = {
		"ON_EVENT" : {
			"ITEM_PICKUP" : ["FROM JSON: {} was picked up by entity {}", ["generator_obj", "other_obj"]]
		}
	}

merged = merge(orig={}, new=config)
pprint.pprint(merged)
