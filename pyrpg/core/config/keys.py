
# Init logging config
import logging
logger = logging.getLogger(__name__)

from pyrpg.core.config import KEYS


_INIT: bool = False

def get_init() -> bool:
    """Return True, if console config is already initiated.
    """
    return _INIT

#def _trans_key_from_str(key_string):
#    """ Returns pygame code of the key.
#    """
#    import pygame
#    return eval('pygame.' + key_string) if key_string is not None else pygame.K_CLEAR # Clear key should not be currently supported so ideal to use

def init() -> None:
    """Prepare the config data.
    """
    # Iterate through key schemas defined in config file and assign the keyboard keys
    #k_profile = dict()
    #for key_profile in KEYS.copy().get('KEY_PROFILES', []):
    #    k_profile.update({key_profile: {k: _trans_key_from_str(v) for k, v in KEYS[key_profile].items()}})
    #KEYS["K_PROFILE"] = k_profile

    # Clear the original pre-conversion config
    #for profile in KEYS["KEY_PROFILES"]: del(KEYS[profile])
    #del(KEYS["KEY_PROFILES"])

    # Convert the rest of the keys
    #for k,v in KEYS.items(): KEYS[k] = _trans_key_from_str(v) if k not in ("K_PROFILE") else KEYS[k]

    import pprint
    logger.debug(f"Keys config initiated. {pprint.pformat(KEYS)}")

    global _INIT
    _INIT = True


def convert_dict_conf_to_vars() -> None:
    """ Add access to KEYS dictionary keys as variables of this module.
    Now it is able to get the configuration as follows:
    
        from pyrpg.core.config.keys import K_SUBMIT

    Without this, you would always need to use the following way

        from pyrpg.core.config.keys import KEYS
        K_SUBMIT = FILEPATHS["K_SUBMIT"]
    """
    globals().update((k,v) for k, v in KEYS.items())

    logger.debug(f"Keys config values initiated as vars.")


