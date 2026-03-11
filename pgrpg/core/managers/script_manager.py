"""Lazy-load and execute Python script modules for event action handling.

Translates entity aliases to integer IDs, then evaluates JSON-encoded
action trees via ``json_logic``. Script modules are imported on first use
and cached for subsequent calls.

Module Globals:
    _scripts: Registry of script name -> callable mappings.
    _alias_to_entity_dict_fnc: Callback returning the alias-to-entity dict.
"""

import logging
logger = logging.getLogger(__name__)


from importlib import import_module

from pgrpg.core.events.event import Event
from pgrpg.core.config import MODULEPATHS
from pgrpg.functions import translate, json_logic

_scripts: dict = {}
_alias_to_entity_dict_fnc: callable = None
logger.info(f"ScriptManager created.")

def init(alias_to_entity_dict_fnc: callable) -> None:
    """Initialize the script manager with the alias resolution callback.

    Args:
        alias_to_entity_dict_fnc: Callable returning a dict mapping entity
            string aliases to integer ECS entity IDs.
    """
    global _alias_to_entity_dict_fnc
    _alias_to_entity_dict_fnc = alias_to_entity_dict_fnc
    logger.info(f"ScriptManager initiated.")

def register_script(fnc: callable, alias: str) -> None:
    """Register a script callable under the given alias.

    Args:
        fnc: The script's entry-point function.
        alias: Name used to reference this script in JSON action trees.
    """
    _scripts.update({alias: fnc})
    logger.info(f'Script function "{alias}" registered at ScriptManager.')

def execute_event_actions(event: Event, actions: any) -> None:
    """Translate entity aliases in the action tree and execute it.

    Args:
        event: The triggering Event whose params are passed as data context.
        actions: A JSON-logic action tree (list/dict structure).
    """

    # Translate entity aliases to entity IDs before processing the action
    translated_actions = translate(_alias_to_entity_dict_fnc(), actions)
    
    logger.debug(f"Using following translation dictionary for translation of aliases in action definition {_alias_to_entity_dict_fnc()}.")
    logger.info(f"Executing actions {translated_actions} for event {event}.")

    # Run the actions
    json_logic(
        expr=translated_actions, 
        value_fnc=lambda x: x, 
        script_fnc=lambda *args: execute_script(args[0], event, **args[1]), 
        data=event.params
    )

def execute_script(script_module_name: str, *script_args, **script_kwargs):
    """Run a script by module name, lazy-loading it on first call.

    Args:
        script_module_name: Dotted module name relative to SCRIPT_MODULE_PATH.
        *script_args: Positional arguments forwarded to the script function.
        **script_kwargs: Keyword arguments forwarded to the script function.

    Returns:
        The return value of the script function.

    Raises:
        ValueError: If the module cannot be loaded or registered.
    """

    # Check if script module is already registered
    script_fnc = _scripts.get(script_module_name, None)

    # Register the script
    if not script_fnc:

        script_module_path_absolute = f"{MODULEPATHS['SCRIPT_MODULE_PATH']}.{script_module_name}"

        # Try to find the script module and get its reference
        try:
            script_module = import_module(script_module_path_absolute)
        except ValueError:
            logger.error(f'Error during loading of script module "{script_module_path_absolute}".')
            raise ValueError(f'Error during loading of script module "{script_module_path_absolute}".')

        # Try to register the script
        try:
            script_module.initialize(register_script, script_module_name)
        except ValueError:
            logger.error(f'Error during initiating/registering of script "{script_module_path_absolute}".')
            raise ValueError(f'Error during initiating/registering of script module "{script_module_path_absolute}".')

        # Get the script function
        script_fnc = _scripts.get(script_module_name)
    
    # Run the script
    return script_fnc(*script_args, **script_kwargs)


def clear_scripts() -> None:
    """Clear all the scripts."""
    _scripts.clear()
    logger.info(f"Scripts were cleared.")


