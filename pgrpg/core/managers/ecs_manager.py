"""Wrap the ECS World and manage processors, entities, components, and templates.

Provides the bridge between the scene loading pipeline and the esper-based
ECS World. Handles entity alias registration, component creation from JSON
definitions, processor lifecycle, and template-based entity factories.

Module Globals:
    _world: The esper World instance holding all entities and processors.
    _entity_to_alias: Dict mapping entity int IDs to string aliases.
    _alias_to_entity: Dict mapping string aliases to entity int IDs.
    _game_functions: Dict of engine function references passed to processors.
    _template_definitions: Dict of stored entity template definitions.
"""

import logging
logger = logging.getLogger(__name__)

from typing import Tuple

from fnmatch import fnmatchcase

from pgrpg.core.ecs import World, Processor
from pgrpg.core.config import FILEPATHS
from pgrpg.core.config import MODULEPATHS
from pgrpg.core.config import pgrpg

from pgrpg.core.ecs import Component
from pgrpg.functions import get_class_from_def
from pgrpg.functions import translate
from pgrpg.functions import json_logic
from pgrpg.functions import get_dict_params
from pgrpg.functions import get_all_dict_values

_world: World = None
_entity_to_alias: dict = {}
_alias_to_entity: dict = {}
_game_functions: dict = {}
_template_definitions: dict = {}

logger.info(f"ECSManager created.")

def initialize(game_functions: dict) -> None:
    """Fill ECS variables with initial values."""

    global _world, _game_functions
    _world = World(timed=pgrpg["TIMED"])
    _game_functions = game_functions

    logger.info(f"ECSManager initiated.")

# --- World delegation helpers (avoid exposing _world directly) ---

def component_for_entity(entity_id, component): return _world.component_for_entity(entity_id, component)
def add_component(entity_id, new_component): return _world.add_component(entity_id, new_component)
def try_component(entity_id, component): return _world.try_component(entity_id, component)
def remove_component(entity_id, component): return _world.remove_component(entity_id, component)
def process(proc_group_id, events, keys, dt: float, debug: bool):_world.process(proc_group_id=proc_group_id, events=events, keys=keys, dt=dt, debug=debug)

# --- Processors ---

def get_proc_perf(sort=False) -> dict:
    """Return processor execution times, optionally sorted descending."""
    return {k: v for k, v in sorted(_world.process_times.items(), key=lambda item: item[1], reverse=True)} if sort else _world.process_times

def get_proc_class_from_def(proc_class_def):
    return get_class_from_def(proc_class_def, MODULEPATHS["PROCESSOR_MODULE_PATH"])


def load_processor(processor_def: list) -> None:
    """Create a Processor from its JSON definition and register it with the World.

    Args:
        processor_def: List of [group_id (optional), class_path, params_dict].
    """

    logger.info(f'Preparing load of processor "{processor_def}" .')

    # Create instance of the processor
    new_proc_instance, new_proc_group = create_processor(processor_def)

    # Registers processor at esper ECS World
    new_proc_instance.initialize(register=_world.add_processor, proc_group_id=new_proc_group)

    # Log the initiation of the processor
    logger.info(f'Processor "{processor_def}" initiated in processor group "{new_proc_group}".')

    # Log all the processors in the processor group
    logger.info(f'Process group "{new_proc_group}" now contains following processors "{_world._processors[new_proc_group]}".')


def reinit_processors():
    """Reinitialize all processors after a configuration change."""
    # Call init function on all registered processors _world._processors
    for proc_group_id in _world._processors:
        for processor in _world._processors[proc_group_id]:
            processor.reinit()
            logger.info(f'Processor "{processor.__class__}" re-initiated.')

    logger.info(f'All processors re-initiated.')

def check_proc_in_world(proc_class_def: str) -> bool:
    """Check if a processor class (by string definition) is instantiated in the World.

    The special value ``'TRUE'`` always returns True (used for optional prerequisites).
    """
    # Special case of processor definition is string "TRUE" (always present). It is used in 
    # situations when some prerequisite is optional but still we want to have it specified for
    # readability.
    if proc_class_def.upper() == 'TRUE': return True
    
    # Get the class from string definition
    check_class = get_proc_class_from_def(proc_class_def)

    # Verify that the processor class has been already instantiated in the game world
    if _world.get_processor(check_class):
        logger.info(f'Processor "{proc_class_def}" is instantiated in the game world.')
        return True
    else:
        logger.warning(f'Processor "{proc_class_def}" is not instantiated in the game world.')
        return False

def check_processor(proc_class: Processor) -> bool:
    """Verify that a processor's PREREQ dependencies are satisfied."""
    try:
        prereqs = proc_class.PREREQ
        if not prereqs: return True
    except AttributeError:
        return True    # no prerequisities hence the check is ok

    if json_logic(expr=prereqs, value_fnc=check_proc_in_world):
        logger.info(f'Processor "{proc_class.__name__}": Prerequisities are ok!')
        return True
    else:
        logger.warning(f'Processor "{proc_class.__name__}": Problem with prerequisities. Game might work incorrectly!')
        return False

def create_processor(processor_def: list) -> Tuple[Processor, str]:
    """Create a Processor instance from its definition list.

    Args:
        processor_def: [group_id (optional), class_path, params_dict].

    Returns:
        Tuple of (processor_instance, group_id).
    """

    # Determine the processor group, if defined on the first position
    proc_group = 'default' if len(processor_def) == 2 else processor_def[0]

    # Determine the processor class path and processor class attributes - last 2 attributes of the processor_def
    class_def, cust_proc_class_attrs = processor_def[-2:]

    # Get the definition of the processor class
    new_class = get_proc_class_from_def(class_def)
    assert new_class is not None, f"Unable to create class from definition {class_def=}"


    # Check that processor has everything that it needs to work in the game
    try:
        if not check_processor(new_class):
            logger.warning(f'Processor "{new_class.__name__}" did not pass all the checks. Game might work incorrectly!')
            raise ValueError(f'Processor "{new_class.__name__}" did not pass all the checks.')
        else:
            logger.info(f'Processor "{new_class.__name__}" has passed all the checks successfully!')
    except ValueError:
        logger.error(f'Error during checking of the of processor "{new_class.__name__}".')
        raise ValueError(f'Error during checking of the of processor.')

    # Get all attributes of the processor class
    proc_attrs = new_class.__init__.__code__.co_varnames[1:]

    # Substitute the attributes with reference to specific engine functions
    proc_attrs = {arg: _game_functions.get(arg) for arg in proc_attrs if _game_functions.get(arg) is not None}

    # Overwrite the attributes with custom attributes from the json definition of the scene
    proc_attrs = {**proc_attrs, **cust_proc_class_attrs}

    # Log the successfull creation of the processor
    logger.info(f'Processor instance "{new_class}" created for group "{proc_group}".')

    # Initiate and return the processor class
    return new_class(**proc_attrs), proc_group

def clear_processors() -> None:
    """Finalize and remove all processors from the game."""
    try:
        _world.finalize()
    except ValueError as e:
        logger.warning(f'Processor "{e.args[0]}" does not have "finalize" method implemented.')

    logger.info(f"All processors finalized.")

    _world.clear_processors()
    logger.info(f"All processors removed.")

def delete_processor(proc_class_def: list) -> None:
    """Deletes the processor from the world."""

    # Extract the processor group and processor definition
    proc_group_id, proc_class_def = proc_class_def

    proc_class = get_proc_class_from_def(proc_class_def)
    proc_class.finalize()
    _world.remove_processor(proc_class, proc_group_id)
    logger.info(f'Processor "{proc_class_def}" successfully removed.')

# --- Components ---

def get_comp_class_from_def(comp_class_def: str) -> Component:
    """Return the Component class from a ``module_path:ClassName`` string.

    Args:
        comp_class_def: Path in ``module.path:ClassName`` format.

    Returns:
        The Component class object.

    Raises:
        ValueError: If the class cannot be resolved.
    """
    return get_class_from_def(comp_class_def, MODULEPATHS["COMPONENT_MODULE_PATH"])

def create_component_from_def(component_def: dict) -> Component:
    """Create a Component instance from its JSON definition dict.

    Entity aliases in params are translated to integer IDs before
    passing to the Component constructor.

    Args:
        component_def: Dict with ``type`` (class path) and ``params`` keys.

    Returns:
        A new Component instance.

    Raises:
        ValueError: If the component cannot be created.
    """
    # Get component type
    comp_class_def = component_def.get("type")

    # Get component params
    comp_params = component_def.get("params", {})

    # Try to create instance of the component
    try:
        # Get the definition of the component class
        new_class = get_comp_class_from_def(comp_class_def=comp_class_def)

        # Use _alias_to_entity dict to seach the values and translate them from string to entity id integers here!!!
        # Every value is searched in alias_dict keys and if found, value is substituted with entity id 
        # integer from alias_dict values.

        # New dictionary containing aliases substituted with integer entity IDs
        comp_params_substituted = translate(_alias_to_entity, comp_params)

        # Return the instance of the component
        return new_class(**comp_params_substituted)

    except ValueError:
        logger.error(f'Error while creating component "{comp_class_def}" with parameters "{comp_params}".')
        raise ValueError

def reinit_components():
    """Reinitialize all components after a configuration change."""
    # Call init function on all registered processors _world._processors
    for component in get_all_dict_values(_world._entities):
        component.reinit()
        logger.info(f'Component "{component.__class__}" re-initiated.')

    logger.info(f'All components re-initiated.')

def update_component(component_def: dict, entity_id: int) -> None:
    """Create a Component from its definition and add it to an entity.

    Args:
        component_def: Dict with ``type`` and ``params`` keys.
        entity_id: Target entity to receive the component.
    """

    # Create and add/overwrite component
    try:
        new_comp = create_component_from_def(component_def)
        add_component(entity_id, new_comp)
        logger.info(f"***{new_comp} for entity {entity_id} created.")
    except ValueError:
        logger.error(f'Error in creation of component "{component_def}".')
        raise ValueError

def delete_component(component_def: dict, entity_id: int) -> None:
    """Remove a Component from an entity by its definition dict.

    Args:
        component_def: Dict with a ``type`` key specifying the component class.
        entity_id: Entity to remove the component from.

    Raises:
        ValueError: If the component cannot be removed.
    """
    try:
        comp_cls = get_comp_class_from_def(comp_class_def=component_def["type"])
        remove_component(entity_id, comp_cls)
        logger.info(f"***{comp_cls} removed from entity {entity_id}.")
    except ValueError:
        logger.error(f'Error while removing of component "{component_def}" from entity "{entity_id}".')
        raise ValueError

# --- Templates ---

def load_stored_template(template_id: str, entity_id: int) -> None:
    """Apply a stored template's components to the given entity."""
    # Get the template data
    logger.info(f'**Preparing data for entity_id {entity_id} from template "{template_id}".')
    template_entity_data = get_dict_params(definition=template_id, storage=_template_definitions, dir=FILEPATHS["ENTITY_PATH"])

    # Create all entities from the template
    logger.info(f'**Creating components for entity_id {entity_id} from template "{template_id}".')
    try:
        _update_entity(template_entity_data, entity_id=entity_id)
    except ValueError:
        logger.error(f'Error in creation of entity {entity_id} from template "{template_id}".')
        raise ValueError


def load_template(template_def: dict) -> None:
    """Store a template definition for later entity creation."""
    _template_definitions.update({template_def["id"]: template_def})
    logger.info(f'Template "{template_def["id"]}" was successfully stored.')

def delete_template(template_id: str) -> None:
    """Remove a template from the registry by ID."""
    try:
        del _template_definitions[template_id]
    except KeyError:
        logger.error(f'Template "{template_id}" not found.')
        raise ValueError

    logger.info(f'Template "{template_id}" successfully removed.')

def delete_templates_pattern(template_pattern: str) -> None:
    """Delete all templates whose IDs match a UNIX-wildcard pattern.

    Args:
        template_pattern: fnmatch-style pattern (e.g. ``"t_crate*"``).
    """

    logger.debug(f'About to delete templates with name matching pattern "{template_pattern}".')

    match = lambda k: fnmatchcase(k, template_pattern)

    # Iterate the dictionary with templates _template_definitions
    # Perform delete_template on all those that match.
    for tid in _template_definitions.copy().keys():
        if match(tid):
            delete_template(template_id=tid)

# --- Entities ---

def _register_entity_lookup(entity_id: int, entity_alias: str) -> None:
    """Register entity alias and id for later lookup."""

    _alias_to_entity.update({entity_alias: entity_id})
    _entity_to_alias.update({entity_id: entity_alias})

    logger.debug(f'Entity id: "{entity_id}" registered under alias: "{entity_alias}"')

def _unregister_entity_lookup(entity_id: int, entity_alias: str) -> None:
    """Unregister entity from lookup dictionaries."""

    logger.debug(f'Deleting entity id {entity_id} / {entity_alias or "unknown"}. from lookup tables.')

    # Un-register the entity - ignore if not found
    try:
        del _alias_to_entity[entity_alias]
        del _entity_to_alias[entity_id]
    except KeyError:
        pass

    logger.debug(f'Entity id: "{entity_id}" unregistered from alias: "{entity_alias}"')

def get_alias_to_entity_dict() -> dict:
    """Return the alias-to-entity-ID mapping dict."""
    return _alias_to_entity

def get_entity_id(entity_alias: str) -> int | None:
    """Translate an entity alias string to its integer ID, or None."""
    try:
        return _alias_to_entity.get(entity_alias, None)
    except TypeError:
        # If entity_alias is list or dictionary (non hashable)
        return None

def get_entity_alias(entity_id: int) -> str | None:
    """Translate an entity integer ID to its alias string, or None."""
    try:
        return _entity_to_alias.get(entity_id, None)
    except TypeError:
        # If entity_id is list or dictionary (non hashable)
        return None

def get_all_entities() -> list:
    """Return all existing entity ids."""
    return list(_world._entities.keys())

def get_entities_with_alias() -> list:
    """Return list of entity ids having alias."""
    return list(_entity_to_alias.keys())

def get_entities_wo_alias() -> list:
    """Return list of entity ids without alias."""
    return [e for e in get_all_entities() if e not in get_entities_with_alias()]

def check_lookup_tables():
    """Returns true if lookup tables are consistent among each other."""
    return len(_entity_to_alias) == len(_alias_to_entity)

def _clear_entity_alias_lookup() -> None:
    """Clear both alias lookup dictionaries."""
    global _entity_to_alias, _alias_to_entity
    _entity_to_alias = {}
    _alias_to_entity = {}
    logger.info(f"All entity alias lookup dictionaries were cleared.")

def _clear_entities_and_components() -> None:
    """Delete all entities and components from the World."""
    _clear_entity_alias_lookup()  # ADDING THIS IS CAUSING THAT no translation dictionary is passed to the ScriptManager!!!
    _world.clear_database()
    logger.info(f'All entities and components cleared.')

def _create_empty_entity(entity_alias: str=None) -> int:
    """Create an empty entity (no components) and register its alias.

    If the alias already exists, returns the existing entity_id instead.
    """
    
    # If entity_alias already exists in the world, do not create new empty entity.
    # (Such entities will be only updated by the new components)
    entity_id = get_entity_id(entity_alias=entity_alias) 
    if entity_id is not None: 
        logger.info(f'Entity alias "{entity_alias}" already exists for {entity_id=}. Skipping creation of new empty entity.')
        return entity_id

    # Create new entity and get its id
    entity_id = _world.create_entity()

    # Registration requires entity alias
    if entity_alias:

        # Update the lookup dictionaries
        _register_entity_lookup(entity_id=entity_id, entity_alias=entity_alias)

    logger.info(f'*Creating new empty entity id: "{entity_id}", entity alias: {entity_alias or "unknown"}')

    return entity_id

def load_register_empty_entity(entity_def: dict) -> None:
    """Create an empty entity and register its alias (scene loading step 1).

    Called before components are filled so that all aliases exist in the
    lookup tables when other entities reference them.

    Args:
        entity_def: Entity definition dict with at least an ``id`` key.
    """
    _create_empty_entity(entity_alias=entity_def["id"])

def _update_entity(entity_def: dict, entity_id: int) -> None:
    """Apply templates, add components, and remove components on an entity.

    Args:
        entity_def: Entity definition dict with optional ``templates``,
            ``components``, and ``remove`` keys.
        entity_id: Target entity ID.
    """

    # Read the components from the templates - order matters! latter has priority and overwrites
    # the previous components.
    for template_id in entity_def.get("templates", []):

        load_stored_template(template_id=template_id, entity_id=entity_id)

    # Add/update components
    for component in entity_def.get("components", []):
        try:
            update_component(component_def=component, entity_id=entity_id)
        except ValueError:
            logger.error(f'Error in update of component of entity {entity_id} from definition "{component}".')
            raise ValueError

    # Remove components
    for component in entity_def.get("remove", []):
        try:
            delete_component(component_def=component, entity_id=entity_id)
        except ValueError:
            logger.error(f'Error in removal of component of entity {entity_id} from definition "{component}".')
            raise ValueError

def load_update_empty_entity(entity_def: dict, add_to_templates: bool=True) -> None:
    """Fill an empty entity with components (scene loading step 2).

    Must be called after ``load_register_empty_entity`` so that all
    entity aliases are available for cross-referencing.

    Args:
        entity_def: Entity definition dict.
        add_to_templates: If True, also store the definition as a template.
    """

    # Find the entity_id that is associated with the alias stored in entity_def["id"]
    entity_id = get_entity_id(entity_alias=entity_def["id"])

    # Now add components to this entity id empty envelope
    _update_entity(entity_def=entity_def, entity_id=entity_id)

    # Additionally, add every entity to the template_definitions so every created entity can
    # be used as a template. (see sokoban_new_level01 scene for examples).
    if add_to_templates: load_template(template_def=entity_def)

def create_entity(entity_def: dict, entity_alias: str=None) -> int:
    """Create a fully populated entity at runtime (e.g. projectiles).

    Unlike scene loading (which uses two-pass register/fill), this creates
    and populates an entity in a single call.

    Args:
        entity_def: Entity definition dict with components/templates.
        entity_alias: Optional alias override (otherwise uses ``entity_def["id"]``).

    Returns:
        The new entity's integer ID.

    Raises:
        ValueError: If component creation fails.
    """
    # Create empty entity
    # First check for explicit alias then for id in json and if nothing found, do not register
    # problem when prescription has id and factory generator is returning none
    entity_id = _create_empty_entity(entity_alias=entity_alias if entity_alias else entity_def.get("id", None))

    # Now add components to this entity id empty envelope
    _update_entity(entity_def=entity_def, entity_id=entity_id)

    return entity_id

def delete_entity(entity_alias: str=None, entity_id: int=None) -> None:
    """Delete and un-register entity from the world."""

    logger.debug(f'About to delete entity id {entity_id=} / {entity_alias or "unknown"}.')

    # Get alias and id
    entity_alias = entity_alias if entity_alias else _entity_to_alias.get(entity_id, None)
    entity_id = entity_id if entity_id else _alias_to_entity.get(entity_alias, None)

    logger.debug(f'After lookup for delete entity id {entity_id=} / {entity_alias or "unknown"}.')

    # Delete it from Esper world
    _world.delete_entity(entity=entity_id)

    # Un-register the entity - ignore if not found, can be unregistered entity
    _unregister_entity_lookup(entity_id=entity_id, entity_alias=entity_alias)

    logger.info(f'Entity id {entity_id=} / {entity_alias or "unknown"} successfully removed.')

def delete_entities_pattern(entity_alias_pattern: str) -> None:
    """Delete all entities whose aliases match a UNIX-wildcard pattern.

    Args:
        entity_alias_pattern: fnmatch-style pattern (e.g. ``"wall*"``).
    """

    logger.debug(f'About to delete entities with aliases matching pattern "{entity_alias_pattern}".')

    match = lambda k: fnmatchcase(k, entity_alias_pattern)

    # Get all entity aliases and entity IDs matching the pattern from _alias_to_entity dictionary.
    # Perform delete_entity on all those that match.
    for alias, id in _alias_to_entity.copy().items():
        if match(alias):
            delete_entity(entity_alias=alias, entity_id=id)


def clear_ecs() -> None:
    """Clear all entities, components, and processors."""
    _clear_entities_and_components()
    clear_processors()

def get_debug_info() -> str:
    """Return a formatted string with the state of entities, components and processors."""
    import pprint
    return pprint.pformat({
        "ECSManagerParams": {
            "_world": _world,
            "_alias_to_entity": _alias_to_entity,
            "_entity_to_alias": _entity_to_alias,
            "_game_functions": _game_functions
        },
        "EsperWorldParams": {
            "_entities": _world._entities,
            "_next_entity_id": _world._next_entity_id,
            "_dead_entities": _world._dead_entities,
            "_components": _world._components,
            "_processors": _world._processors
        }
    })

# --- Test mock (used by example_game/ command doctests) ---

class ECSManagerMock:
    """Mock ECS manager for use in command module doctests."""

    add_component = lambda self, e, c: None
    try_component = lambda self, e, c: None

    def try_component(self, entity, comp):
        from core.components.position import Position, PositionMock
        if comp == Position:
            return PositionMock(x=0, y=0)
        else:
            return None

    def component_for_entity(self, entity, comp):
        from core.components.position import Position, PositionMock
        if comp == Position:
            return PositionMock(x=0, y=0)
        else:
            return None

    def fnc_get_map_mock(map_name):
        from pgrpg.core.managers.map_manager import MapManagerMock
        return MapManagerMock().get_map(map_name)

    _game_functions = {
        'FNC_GET_MAP': fnc_get_map_mock
    }
