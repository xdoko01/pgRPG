# Create logger
import logging
logger = logging.getLogger(__name__)

from typing import Tuple

from pyrpg.core.ecs import World, Processor
from pyrpg.core.config import FILEPATHS # ENTITY_PATH # for ENTITY_PATH
from pyrpg.core.config import MODULEPATHS # for COMPONENT_MODULE_PATH, PROCESSOR_MODULE_PATH
from pyrpg.core.config import PYRPG # for TIMED parameter

from pyrpg.core.ecs import Component
from pyrpg.functions import get_class_from_def
from pyrpg.functions import translate # for creation of the component
from pyrpg.functions import json_logic # for evaluating conditions for processor prerequisites
from pyrpg.functions import get_dict_params # for filling of template with variables
from pyrpg.functions import get_all_dict_values # for reinit oc components

# Keeping reference to ECS world
_world: World = None

# Keeping dictionaries of IDs and aliases of entities
_entity_to_alias: dict = {}
_alias_to_entity: dict = {}

# Keeping reference to external game functions that can be used in processors
_game_functions: dict = {}

# Keeping template definitions in dictionary instead of file
_template_definitions: dict = {}

logger.info(f"ECSManager created.")

#def initialize(timed: bool, game_functions: dict) -> None:
def initialize(game_functions: dict) -> None:
    """Fill ECS variables with initial values."""

    global _world, _game_functions
    _world = World(timed=PYRPG["TIMED"])
    _game_functions = game_functions

    logger.info(f"ECSManager initiated.")

#####################
## HELPERS - in order not to use _world in the commands
#####################

def component_for_entity(entity_id, component): return _world.component_for_entity(entity_id, component)
def add_component(entity_id, new_component): return _world.add_component(entity_id, new_component)
def try_component(entity_id, component): return _world.try_component(entity_id, component)
def remove_component(entity_id, component): return _world.remove_component(entity_id, component)
def process(proc_group_id, events, keys, dt: float, debug: bool):_world.process(proc_group_id=proc_group_id, events=events, keys=keys, dt=dt, debug=debug)

#####################
## PROCESSORS - START
#####################

def get_proc_class_from_def(proc_class_def):
    return get_class_from_def(proc_class_def, MODULEPATHS["PROCESSOR_MODULE_PATH"])


def load_processor(processor_def: list) -> None:
    """Takes processor definition, creates instance and registers
    it into the game world."""

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
    """Used for re-init of processor parameters in case the configuration
    has changed.
    """
    # Call init function on all registered processors _world._processors
    for processor in _world._processors:
        processor.reinit()
        logger.info(f'Processor "{processor.__class__}" re-initiated.')

    logger.info(f'All processors re-initiated.')

def check_proc_in_world(proc_class_def: str) -> bool:
    """Checks, if the class represented by string exists and is already initiated in the
    game world. Returns True in case the prerequisit processor is present in the game world.
    Else, returns False.
    """
    check_class = get_proc_class_from_def(proc_class_def)

    # Verify that the processor class has been already instantiated in the game world
    if _world.get_processor(check_class):
        logger.info(f'Processor "{proc_class_def}" is instantiated in the game world.')
        return True
    else:
        logger.warning(f'Processor "{proc_class_def}" is not instantiated in the game world.')
        return False

def check_processor(proc_class: Processor) -> bool:
    """Checks if the processor has all necessary prerequisities for
    other processors in the game fulfilled.
    """
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
    """Creates the processor instance from list definition and identify the
    processor group."""

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
        else:
            logger.info(f'Processor "{new_class.__name__}" has passed all the checks successfully!')
    except ValueError:
        logger.error(f'Error during checking of the of processor "{new_class.__name__}".')
        raise ValueError(f'Error during checking of the of processor "{new_class.__name__}".')

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

#####################
## PROCESSORS - END
#####################

#####################
## COMPONENTS - START
#####################

def get_comp_class_from_def(comp_class_def: str) -> Component:
    """Returns class object of the component based on component path.
    Component class is used to create new component or delete component.

    :param comp_class_def: Path to the component class in format of path.to.module:ComponentClass
    :type comp_class_def: str

    :return: Returns reference to the component class.
    :raises: ValueException, if component class cannot be identified
    """
    return get_class_from_def(comp_class_def, MODULEPATHS["COMPONENT_MODULE_PATH"])

def create_component_from_def(component_def: dict) -> Component:
    """Returns new instance of component created.

    :param component_def: Dictionary specifying the component and its parameters
    :type component_def: dict

    :return: Returns reference to the new component instance.
    :raises: ValueException, if component instance cannot be created
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
    """Used for re-init of component parameters in case the configuration
    has changed.
    """
    # Call init function on all registered processors _world._processors
    for component in get_all_dict_values(_world._entities):
        component.reinit()
        logger.info(f'Component "{component.__class__}" re-initiated.')

    logger.info(f'All components re-initiated.')

def update_component(component_def: dict, entity_id: int) -> None:
    """Takes the definition of the component (dictionary), creates 
    the component in the world and adds it to the provided entity.
    
    :param component_def: Dictionary specifying the component and its parameters
    :type component_def: dict
    """

    # Create and add/overwrite component
    try:
        new_comp = create_component_from_def(component_def)
        add_component(entity_id, new_comp)
        logger.info(f"***{new_comp} for entity {entity_id} created.")
    except ValueError:
        logger.error(f'Error in creation of component "{component_def}".')
        raise ValueError

def remove_component(component_def: dict, entity_id: int) -> None:
    """Removes given component on given entity
    
    :param component_def: Dictionary specifying the component type
    :type component_def: dict

    :raises: ValueException, if component cannot be removed
    """
    try:
        comp_cls = get_comp_class_from_def(comp_class_def=component_def["type"])
        remove_component(entity_id, comp_cls)
        logger.info(f"***{comp_cls} removed from entity {entity_id}.")
    except ValueError:
        logger.error(f'Error while removing of component "{component_def}" from entity "{entity_id}".')
        raise ValueError

#####################
## COMPONENTS - END
#####################

#####################
## TEMPLATES - START
#####################

def load_template(template_def: dict) -> None:
    """Stores the template definition from which new templates can be created.
    """
    _template_definitions.update({template_def["id"]: template_def})
    logger.info(f'Template "{template_def["id"]}" was successfully stored.')

def delete_template(template_id: str) -> None:
    """Deletes template from internal template storage _template_definitions.
    """
    try:
        del _template_definitions[template_id]
    except KeyError:
        logger.error(f'Template "{template_id}" not found.')
        raise ValueError

    logger.info(f'Template "{template_id}" successfully removed.')

#####################
## TEMPLATES - END
#####################

#####################
## ENTITIES - START
#####################

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
    """For some reason it is necessary to pass the dictionary
    using this call to ScriptManager rather than passing reference to the dictionary directly.
    """
    return _alias_to_entity

def get_entity_id(entity_alias: str) -> int | None:
    """Translate entity alias (string) to entity id (integer)
    based on _alias_to_entity dictionary.
    """
    try:
        return _alias_to_entity.get(entity_alias, None)
    except TypeError:
        # If entity_alias is list or dictionary (non hashable)
        return None

def get_entity_alias(entity_id: int) -> str | None:
    """Translate entity id (integer) to entity alias (str)
    based on _entity_to_alias dictionary.
    """
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
    """Clear the dictionaries holding mapping between entity alias
    and entity id."""
    global _entity_to_alias, _alias_to_entity
    _entity_to_alias = {}
    _alias_to_entity = {}
    logger.info(f"All entity alias lookup dictionaries were cleared.")

def _clear_entities_and_components() -> None:
    '''Delete all entities and components from the world'''
    _clear_entity_alias_lookup()  # ADDING THIS IS CAUSING THAT no translation dictionary is passed to the ScriptManager!!!
    _world.clear_database()
    logger.info(f'All entities and components cleared.')

def _create_empty_entity(entity_alias: str=None) -> int:
    """Create empty envelope for the entity where later components will be added.
    If entity already exists in the game world, return its existing entity_id and
    do not create new empty entity.
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
    """Creates empty entity and registers it into the lookup tables.
    
    It is called from the engine as a first step of loading of entities in
    order to be able to use entity aliases in definition of other entity
    components.

    :param entity_def: Description of entity in JSON format (python dict).
    :type entity_def: dict
    """
    _create_empty_entity(entity_alias=entity_def["id"])

def _update_entity(entity_def: dict, entity_id: int) -> None:
    """Add and remove components/templates specified in entity_def on specified entity_id.

    Parameters:
        :param entity_def: Description of entity in JSON format (python dict).
        :type entity_def: dict

        :param entity_id: Specifies entity id on which the update should be done
        :type entity_id: int
    """

    # Read the components from the templates - order matters! latter has priority and overwrites
    # the previous components.
    for template_id in entity_def.get("templates", []):

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
            remove_component(component_def=component, entity_id=entity_id)
        except ValueError:
            logger.error(f'Error in removal of component of entity {entity_id} from definition "{component}".')
            raise ValueError

def load_update_empty_entity(entity_def: dict, add_to_templates: bool=True) -> None:
    """Fills the empty entity with components.
    
    It is called from the engine as the second step of loading entities.
    It is vital that register_empty_entity is called before to ensure that
    all game entity aliases that might be referenced in the component definition
    already exists in the lookup tables
    
    :param entity_def: Description of entity in JSON format (python dict).
    :type entity_def: dict

    :param add_to_templates: Whether to add entity definition automatically to the templates
                                where it can be used for creation of other entities.
    :type add_to_templates: bool
    """

    # Find the entity_id that is associated with the alias stored in entity_def["id"]
    entity_id = get_entity_id(entity_alias=entity_def["id"])

    # Now add components to this entity id empty envelope
    _update_entity(entity_def=entity_def, entity_id=entity_id)

    # Additionally, add every entity to the template_definitions so every created entity can
    # be used as a template. (see sokoban_new_level01 scene for examples).
    if add_to_templates: load_template(template_def=entity_def)

def create_entity(entity_def: dict, entity_alias: str=None) -> int:
    """Creates brand new entity with components - called from game logic to factory 
    new entities during the game - projectiles etc.
    Entities that are created from scene file are created using load_register_empty_entity
    and load_update_empty_entity function.

    :param entity_def: Description of entity in JSON format (python dict).
    :type entity_def: dict

    :param entity_alias: Parameter overrides entity alias that is present in entity_def definition under
        key 'id'.
    :type entity_alias: str

    :returns: Integer specifying entity id

    :raise: ValueError - in case of problem with component creation
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

#####################
## ENTITIES - END
#####################

def clear_ecs() -> None:
    _clear_entities_and_components()
    clear_processors()

def __str__(self):
    """Print the state of the entities, components and processors at any given
    time.
    """
    import pprint
    return pprint.pformat({ 
        "ECSManagerParams": {
            "_world": self._world,
            "_alias_to_entity": self._alias_to_entity,
            "_entity_to_alias": self._entity_to_alias,
            "_game_functions": self._game_functions
        },
        "EsperWorldParams": {
            "_entities": self._world._entities,
            "_next_entity_id": self._world._next_entity_id,
            "_dead_entities": self._world._dead_entities,
            "_components": self._world._components,
            "_processors": self._world._processors
        }
    })

###
"""
class ECSManager:
    '''Encapsulates functionalities needed to create, maintain and remove components
    entities and processors in the game world.'''

    def __init__(self) -> None:
        '''Initiates key ECS variables'''

        # Keeping reference to ECS world
        self._world = None

        # Keeping dictionaries of IDs and aliases of entities
        self._entity_to_alias = {}
        self._alias_to_entity = {}
        
        # Keeping reference to external game functions that can be used in processors
        self._game_functions = {}

        # Keeping template definitions in dictionary instead of file
        self._template_definitions = {}

        logger.info(f'ECSManager created.')

    def initialize(self, timed: bool, game_functions: dict) -> None:
        '''Fill ECS variables with initial values'''

        self._world = World(timed=timed)
        self._game_functions = game_functions
        logger.info(f'ECSManager initiated.')

    #####################
    ## HELPERS - in order not to use _world in the commands
    #####################
    def component_for_entity(self, entity, component): return self._world.component_for_entity(entity, component)
    def add_component(self, entity, new_component): return self._world.add_component(entity, new_component)
    def try_component(self, entity, component): return self._world.try_component(entity, component)

    #####################
    ## PROCESSORS - START
    #####################
    def get_proc_class_from_def(self, proc_class_def):
        return get_class_from_def(proc_class_def, MODULEPATHS["PROCESSOR_MODULE_PATH"])

    def load_processor(self, processor_def: list) -> None:
        '''Takes processor definition and registers
        it into the game world'''

        logger.info(f'Preparing load of processor "{processor_def}" .')

        # Create instance of the processor
        new_proc = self.create_processor(processor_def)

        # Registers processor at esper ECS World
        new_proc.initialize(register=self._world.add_processor)

        # Log the initiation of the processor
        logger.info(f'Processor "{processor_def}" initiated.')

    def create_processor(self, processor_def: list) -> Processor:
        '''Imports the processor class and registers it into the world'''

        class_def, cust_proc_class_attrs = processor_def

        # Get the definition of the processor class
        new_class = self.get_proc_class_from_def(class_def)
        assert new_class is not None, f'Unable to create class from definition {class_def = }'

        # Check that processor has everything that it needs to work in the game
        try:
            if not self.check_processor(new_class):
                logger.warning(f'Processor "{new_class.__name__}" did not pass all the checks. Game might work incorrectly!')
            else:
                logger.info(f'Processor "{new_class.__name__}" has passed all the checks successfully!')
        except ValueError:
            logger.error(f'Error during checking of the of processor "{new_class.__name__}".')
            raise ValueError(f'Error during checking of the of processor "{new_class.__name__}".')

        # Get all attributes of the processor class
        proc_attrs = new_class.__init__.__code__.co_varnames[1:]

        # Substitute the attributes with reference to specifice engine functions
        proc_attrs = { arg : self._game_functions.get(arg) for arg in proc_attrs if self._game_functions.get(arg) is not None}

        # Overwrite the attributes with custom attributes from the json definition of the scene
        proc_attrs = {**proc_attrs, **cust_proc_class_attrs}

        # Initiate and return the processor class
        return new_class(**proc_attrs)

    def check_processor(self, proc_class: Processor) -> bool:
        '''Checks if the processor has all necessary prerequisities for
        other processors in the game fulfilled.
        '''
        try:
            prereqs = proc_class.PREREQ
            if not prereqs: return True
        except AttributeError:
            return True    # no prerequisities hence the check is ok

        if json_logic(expr=prereqs, value_fnc=self.check_proc_in_world):
            logger.info(f'Processor "{proc_class.__name__}": Prerequisities are ok!')
            return True
        else:
            logger.warning(f'Processor "{proc_class.__name__}": Problem with prerequisities. Game might work incorrectly!')
            return False

    def check_proc_in_world(self, proc_class_def: str) -> bool:
        ''' Checks, if the class represented by string exists and is already initiated in the
        game world. Returns True in case the prerequisit processor is present in the game world.
        Else, returns False.
        '''
        check_class = self.get_proc_class_from_def(proc_class_def)

        # Verify that the processor class has been already instantiated in the game world
        if self._world.get_processor(check_class):
            logger.info(f'Processor "{proc_class_def}" is instantiated in the game world.')
            return True
        else:
            logger.warning(f'Processor "{proc_class_def}" is not instantiated in the game world.')
            return False

    def clear_processors(self) -> None:
        '''Finalize and remove all processors from the game'''
        try:
            self._world.finalize()
        except ValueError as e:
            logger.warn(f'Processor "{e.args[0]}" does not have "finalize" method implemented.')

        logger.info(f'All processors finalized.')

        self._world.clear_processors()
        logger.info(f'All processors removed.')

    def delete_processor(self, proc_class_def: str) -> None:
        '''Deletes the processor from the world'''

        proc_class = self.get_proc_class_from_def(proc_class_def)
        proc_class.finalize()
        self._world.remove_processor(proc_class)
        logger.info(f'Processor "{proc_class_def}" successfully removed.')

    #####################
    ## PROCESSORS - END
    #####################

    #####################
    ## COMPONENTS - START
    #####################

    def get_comp_class_from_def(self, comp_class_def: str) -> Component:
        '''Returns class object of the component based on component path.
        Component class is used to create new component or delete component.

        :param comp_class_def: Path to the component class in format of path.to.module:ComponentClass
        :type comp_class_def: str

        :return: Returns reference to the component class.
        :raises: ValueException, if component class cannot be identified
        '''
        return get_class_from_def(comp_class_def, MODULEPATHS["COMPONENT_MODULE_PATH"])

    def create_component_from_def(self, component_def: dict) -> Component:
        '''Returns new instance of component created.

        :param component_def: Dictionary specifying the component and its parameters
        :type component_def: dict

        :return: Returns reference to the new component instance.
        :raises: ValueException, if component instance cannot be created
        '''
        # Get component type
        comp_class_def = component_def.get("type")

        # Get component params
        comp_params = component_def.get("params", {})

        # Try to create instance of the component
        try:
            # Get the definition of the component class
            new_class = self.get_comp_class_from_def(comp_class_def=comp_class_def)

            # Use _alias_to_entity dict to seach the values and translate them from string to entity id integers here!!!
            # Every value is searched in alias_dict keys and if found, value is substituted with entity id 
            # integer from alias_dict values.

            # New dictionary containing aliases substituted with integer entity IDs
            comp_params_substituted = translate(self._alias_to_entity, comp_params)

            # Return the instance of the component
            return new_class(**comp_params_substituted)

        except ValueError:
            logger.error(f'Error while creating component "{comp_class_def}" with parameters "{comp_params}".')
            raise ValueError

    def update_component(self, component_def: dict, entity_id: int) -> None:
        '''Takes the definition of the component (dictionary), creates 
        the component in the world and adds it to the provided entity.
        
        :param component_def: Dictionary specifying the component and its parameters
        :type component_def: dict
        '''

        # Create and add/overwrite component
        try:
            new_comp = self.create_component_from_def(component_def)
            self._world.add_component(entity_id, new_comp)
            logger.info(f'***{new_comp} for entity {entity_id} created.')
        except ValueError:
            logger.error(f'Error in creation of component "{component_def}".')
            raise ValueError

    def remove_component(self, component_def: dict, entity_id: int) -> None:
        '''Removes given component on given entity
        
        :param component_def: Dictionary specifying the component type
        :type component_def: dict

        :raises: ValueException, if component cannot be removed
        '''
        try:
            comp_cls = self.get_comp_class_from_def(comp_class_def=component_def["type"])
            self._world.remove_component(entity_id, comp_cls)
            logger.info(f'***{comp_cls} removed from entity {entity_id}.')
        except ValueError:
            logger.error(f'Error while removing of component "{component_def}" from entity "{entity_id}".')
            raise ValueError

    #####################
    ## COMPONENTS - END
    #####################

    #####################
    ## TEMPLATES - START
    #####################

    def load_template(self, template_def: dict) -> None:
        '''Stores the template definition from which new templates can be created
        '''
        self._template_definitions.update({template_def["id"]: template_def})

        logger.info(f'Template "{template_def["id"]}" was successfully stored.')

    def delete_template(self, template_id: str) -> None:
        '''Deletes template from internal template storage _template_definitions'''
        try:
            del self._template_definitions[template_id]
        except KeyError:
            logger.error(f'Template "{template_id}" not found.')
            raise ValueError

        logger.info(f'Template "{template_id}" successfully removed.')

    #####################
    ## TEMPLATES - END
    #####################

    #####################
    ## ENTITIES - START
    #####################

    def load_register_empty_entity(self, entity_def: dict) -> None:
        '''Creates empty entity and registers it into the lookup tables.
        
        It is called from the engine as a first step of loading of entities in
        order to be able to use entity aliases in definition of other entity
        components.

        :param entity_def: Description of entity in JSON format (python dict).
        :type entity_def: dict
        '''
        self._create_empty_entity(entity_alias=entity_def["id"])

    def load_update_empty_entity(self, entity_def: dict, add_to_templates: bool=True) -> None:
        '''Fills the empty entity with components.
        
        It is called from the engine as the second step of loading entities.
        It is vital that register_empty_entity is called before to ensure that
        all game entity aliases that might be referenced in the component definition
        already exists in the lookup tables
        
        :param entity_def: Description of entity in JSON format (python dict).
        :type entity_def: dict

        :param add_to_templates: Whether to add entity definition automatically to the templates
                                 where it can be used for creation of other entities.
        :type add_to_templates: bool
        '''

        # Find the entity_id that is associated with the alias stored in entity_def["id"]
        entity_id = self.get_entity_id(entity_alias=entity_def["id"])

        # Now add components to this entity id empty envelope
        self._update_entity(entity_def=entity_def, entity_id=entity_id)

        # Additionally, add every entity to the template_definitions so every created entity can
        # be used as a template. (see sokoban_new_level01 scene for examples).
        if add_to_templates: self.load_template(template_def=entity_def)

    def create_entity(self, entity_def: dict, entity_alias: str=None) -> int:
        '''Creates brand new entity with components - called from game logic to factory 
        new entities during the game - projectiles etc.
        Entities that are created from scene file are created using load_register_empty_entity
        and load_update_empty_entity function.

        :param entity_def: Description of entity in JSON format (python dict).
        :type entity_def: dict

        :param entity_alias: Parameter overrides entity alias that is present in entity_def definition under
            key 'id'.
        :type entity_alias: str

        :returns: Integer specifying entity id

        :raise: ValueError - in case of problem with component creation
        '''
        # Create empty entity
        # First check for explicit alias then for id in json and if nothing found, do not register
        # problem when prescription has id and factory generator is returning none
        entity_id = self._create_empty_entity(entity_alias=entity_alias if entity_alias else entity_def.get("id", None))

        # Now add components to this entity id empty envelope
        self._update_entity(entity_def=entity_def, entity_id=entity_id)

        return entity_id

    def _create_empty_entity(self, entity_alias: str=None) -> int:
        '''Create empty envelope for the entity where later components will be added.
        If entity already exists in the game world, return its existing entity_id and
        do not create new empty entity.
        '''
        
        # If entity_alias already exists in the world, do not create new empty entity.
        # (Such entities will be only updated by the new components)
        entity_id = self.get_entity_id(entity_alias=entity_alias) 
        if entity_id is not None: 
            logger.info(f'Entity alias "{entity_alias}" already exists for {entity_id=}. Skipping creation of new empty entity.')
            return entity_id

        # Create new entity and get its id
        entity_id = self._world.create_entity()

        # Registration requires entity alias
        if entity_alias:

            # Update the lookup dictionaries
            self._register_entity_lookup(entity_id=entity_id, entity_alias=entity_alias)

        logger.info(f'*Creating new empty entity id: "{entity_id}", entity alias: {entity_alias or "unknown"}')

        return entity_id

    def _update_entity(self, entity_def: dict, entity_id: int):
        '''Add and remove components/templates specified in entity_def on specified entity_id.

            Parameters:
                :param entity_def: Description of entity in JSON format (python dict).
                :type entity_def: dict

                :param entity_id: Specifies entity id on which the update should be done
                :type entity_id: int
        '''

        # Read the components from the templates - order matters! latter has priority and overwrites
        # the previous components.
        for template_id in entity_def.get("templates", []):

            # Get the template data
            logger.info(f'**Preparing data for entity_id {entity_id} from template "{template_id}".')
            template_entity_data = get_dict_params(definition=template_id, storage=self._template_definitions, dir=ENTITY_PATH)

            # Create all entities from the template
            logger.info(f'**Creating components for entity_id {entity_id} from template "{template_id}".')
            try:
                self._update_entity(template_entity_data, entity_id=entity_id)
            except ValueError:
                logger.error(f'Error in creation of entity {entity_id} from template "{template_id}".')
                raise ValueError

        # Add/update components
        for component in entity_def.get("components", []):
            try:
                self.update_component(component_def=component, entity_id=entity_id)
            except ValueError:
                logger.error(f'Error in update of component of entity {entity_id} from definition "{component}".')
                raise ValueError

        # Remove components
        for component in entity_def.get("remove", []):
            try:
                self.remove_component(component_def=component, entity_id=entity_id)
            except ValueError:
                logger.error(f'Error in removal of component of entity {entity_id} from definition "{component}".')
                raise ValueError

    def delete_entity(self, entity_alias: str=None, entity_id: int=None) -> None:
        ''' Delete and un-register entity from the world.'''

        logger.debug(f'About to delete entity id {entity_id=} / {entity_alias or "unknown"}.')

        # Get alias and id
        entity_alias = entity_alias if entity_alias else self._entity_to_alias.get(entity_id, None)
        entity_id = entity_id if entity_id else self._alias_to_entity.get(entity_alias, None)

        logger.debug(f'After lookup for delete entity id {entity_id=} / {entity_alias or "unknown"}.')

        # Delete it from Esper world
        self._world.delete_entity(entity=entity_id)

        # Un-register the entity - ignore if not found, can be unregistered entity
        self._unregister_entity_lookup(entity_id=entity_id, entity_alias=entity_alias)

        logger.info(f'Entity id {entity_id=} / {entity_alias or "unknown"} successfully removed.')

    #####################
    ## ENTITIES - END
    #####################

    def get_alias_to_entity_dict(self) -> dict:
        '''FOr some reason it is necessary to pass the dictionary
        using this call to ScriptManager rather than passing reference to the dictionary directly'''
        return self._alias_to_entity

    def get_entity_id(self, entity_alias: str) -> int | None:
        ''' Translate entity alias (string) to entity id (integer)
        based on _alias_to_entity dictionary.
        '''
        try:
            return self._alias_to_entity.get(entity_alias, None)
        except TypeError:
            # If entity_alias is list or dictionary (non hashable)
            return None

    def get_entity_alias(self, entity_id: int) -> str:
        ''' Translate entity id (integer) to entity alias (str)
        based on _entity_to_alias dictionary.
        '''
        try:
            return self._entity_to_alias.get(entity_id, None)
        except TypeError:
            # If entity_id is list or dictionary (non hashable)
            return None

    def _register_entity_lookup(self, entity_id: int, entity_alias: str):
        '''Register entity alias and id for later lookup.'''

        self._alias_to_entity.update({entity_alias: entity_id})
        self._entity_to_alias.update({entity_id: entity_alias})

        logger.debug(f'Entity id: "{entity_id}" registered under alias: "{entity_alias}"')

    def _unregister_entity_lookup(self, entity_id: int, entity_alias: str):
        '''Unregister entity from lookup dictionaries.'''

        logger.debug(f'Deleting entity id {entity_id} / {entity_alias or "unknown"}. from lookup tables.')

        # Un-register the entity - ignore if not found
        try:
            del self._alias_to_entity[entity_alias]
            del self._entity_to_alias[entity_id]
        except KeyError:
            pass

        logger.debug(f'Entity id: "{entity_id}" unregistered from alias: "{entity_alias}"')

    def get_all_entities(self) -> list:
        '''Return all existing entity ids'''
        return list(self._world._entities.keys())

    def get_entities_with_alias(self) -> list:
        '''Return list of entity ids having alias'''
        return list(self._entity_to_alias.keys())

    def get_entities_wo_alias(self) -> list:
        '''Return list of entity ids without alias'''
        return [e for e in self.get_all_entities() if e not in self.get_entities_with_alias()]
    
    def check_lookup_tables(self):
        ''' Returns true if lookup tables are consistent among each other.
        '''
        return len(self._entity_to_alias) == len(self._alias_to_entity)

    def _clear_entity_alias_lookup(self) -> None:
        '''Clear the dictionaries holding mapping between entity alias
        and entity id.'''
        self._entity_to_alias = {}
        self._alias_to_entity = {}
        logger.info(f'All entity alias lookup dictionaries were cleared.')

    def _clear_entities_and_components(self) -> None:
        '''Delete all entities and components from the world'''
        self._clear_entity_alias_lookup()  # ADDING THIS IS CAUSING THAT no translation dictionary is passed to the ScriptManager!!!
        self._world.clear_database()
        logger.info(f'All entities and components cleared.')

    def clear_ecs(self) -> None:
        self._clear_entities_and_components()
        self.clear_processors()

    def process(self, events, keys, dt: float, debug: bool) -> None:
        '''Calls process method on all loaded processors.'''
        self._world.process(events=events, keys=keys, dt=dt, debug=debug)

    def __str__(self):
        '''Print the state of the entities, components and processors at any given
        time.
        '''
        import pprint
        return pprint.pformat({ 
            "ECSManagerParams": {
                "_world": self._world,
                "_alias_to_entity": self._alias_to_entity,
                "_entity_to_alias": self._entity_to_alias,
                "_game_functions": self._game_functions
            },
            "EsperWorldParams": {
                "_entities": self._world._entities,
                "_next_entity_id": self._world._next_entity_id,
                "_dead_entities": self._world._dead_entities,
                "_components": self._world._components,
                "_processors": self._world._processors
            }
        })

"""

from dataclasses import dataclass

@dataclass
class ECSManagerMock:

    add_component = lambda self,e,c: None
    try_component = lambda self,e,c: None

    def try_component(self, entity, comp):
        from core.components.position import Position, PositionMock
        if comp == Position:
            return PositionMock(x=0,y=0)
        else:
            return None

    def component_for_entity(self, entity, comp):
        from core.components.position import Position, PositionMock
        if comp == Position:
            return PositionMock(x=0,y=0)
        else:
            return None

    def fnc_get_map_mock(map_name):
        from pyrpg.core.managers.map_manager import MapManagerMock
        return MapManagerMock().get_map(map_name)

    _game_functions = {
        'FNC_GET_MAP': fnc_get_map_mock
    }

