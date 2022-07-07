import logging

from pyrpg.core.ecs.esper import World, Processor
from pyrpg.core.config.paths import Path, ENTITY_PATH
from pyrpg.core.ecs.components.component import Component
from pyrpg.functions import get_class_object # for dynamic creation of components and processors from json definition
from pyrpg.functions import translate # for creation of the component
from pyrpg.functions import get_dict_from_json # for loading of json without C-style comments
from pyrpg.functions import json_logic # for evaluating conditions for processor prerequisites
from pyrpg.functions import parse_fnc_str # for creation of entity from template with parameters

# Create logger
logger = logging.getLogger(__name__)

class ECSManager:

    def __init__(self) -> None:
        self._world = None
        self._entity_to_alias = {}
        self._alias_to_entity = {}
        self._game_functions = {}
        self._entity_definitions = {}
        self._template_definitions = {}

        logger.info(f'ECSManager created.')

    def initialize(self, timed: bool, game_functions: dict) -> None:
        self._world = World(timed=timed)
        self._game_functions = game_functions
        logger.info(f'ECSManager initiated.')

    def get_game_world(self) -> World:
        return self._world

    def get_entity_id(self, entity_alias: str) -> int:
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

    def get_entities_no_alias(self) -> list:
        '''Return list of entity ids without alias'''
        return [e for e in self.get_all_entities() if e not in self.get_entities_with_alias()]
    
    def check_lookup_tables(self):
        ''' Returns true if lookup tables are consistent among each other.
        '''
        return len(self._entity_to_alias) == len(self._alias_to_entity)

    def _create_component(self, comp_path: str, comp_params: dict) -> Component:
        ''' Returns new instance of component created.

        Parameters:

            :param comp_path: Path to the component class in format of path.to.module:ComponentClass
            :type comp_path: str

            :param comp_params: Parameters for initiation of component instance.
            :type comp_params: dict

            :return: Returns reference to the new component instance.
            :raises: ValueException, if component instance cannot be created
        '''

        # Get the definition of the component class
        try:
            # Spit the module path and the class name
            # For example: comp_path = 'new.movement:Movable' results to
            # comp_module = 'new.movement'
            # comp_class = 'Movable'
            comp_module, comp_class = comp_path.split(':')
            new_class = get_class_object(None, 'pyrpg.core.ecs.components.' + comp_module, comp_class)

        except ValueError:
            logger.error(f'Error during loading of component class "{comp_class}"')
            raise ValueError(f'Error during loading of component class "{comp_class}"')

        # Try to create instance of the component
        try:
            # Use alias_dict to seach the values and translate them from string to entity id integers here!!!
            # Every value is searched in alias_dict keys and if found, value is substituted with entity id 
            # integer from alias_dict values.

            # New dictionary containing aliases substituted with integer entity IDs
            comp_params_substituted = translate(self._alias_to_entity, comp_params)

            # Return the instance of the component
            return new_class(**comp_params_substituted)

        except ValueError:
            logger.error(f'Incorrect parameters while creating component "{comp_class}"')
            raise ValueError

    def store_template_definition(self, json_ent_obj: dict, template_id: str) -> None:
        '''Stores the template definition from which new templates can be created
        '''
        template_vars = json_ent_obj.pop("vars", []) # Store variables separatelly
        self._template_definitions.update({ template_id: { "definition": json_ent_obj, "vars": template_vars } })

    def store_entity_definition(self, json_ent_obj: dict, entity_id: int) -> None:
        '''Stores the up level definition of entity from the quest specification.
        Used for possibility to use existing entity definition as a template
        for creation of other entity.
        '''
        self._entity_definitions.update({ entity_id: json_ent_obj })

    def create_empty_entity(self, entity_alias: str=None) -> int:
        '''Create empty envelope for the entity where later components will be added'''
        
        # Create new entity and get its id
        entity_id = self._world.create_entity()

        # Registration requires entity alias
        if entity_alias:

            # Update the lookup dictionaries
            self._register_entity_lookup(entity_id=entity_id, entity_alias=entity_alias)

        logger.info(f'*Creating new empty entity id: "{entity_id}", entity alias: {entity_alias or "unknown"}')

        return entity_id

    def update_entity(self, json_ent_obj: dict, entity_id: int):
        '''Add components/templates specified in json_ent_object on specified entity_id.

            Parameters:
                :param json_ent_obj: Description of entity in JSON format (python dict).
                :type json_ent_obj: dict

                :param entity_id: Specifies entity id on which the update should be done
                :type entity_id: int
        '''
        # Read the components from the templates - order matters! latter has priority and overwrites
        # the previous components.
        for template in json_ent_obj.get("templates", []):

            # Template starts with &, i.e. creation from template, possibly using variables
            if template[0] == '&':
                # Get template name and variables as a list
                template_name, template_values = parse_fnc_str(template[1:])

                # Substitute the variables in template definition for the actual passed data
                
                # Get variable names as a list
                template_vars_defs = self._template_definitions[template_name]['vars']

                # Return the definition where variables are substituted with the actual values
                template_entity_data = translate(
                    dict(zip(template_vars_defs, template_values)), # Translation dictionary made from list of variables and their values
                    self._template_definitions[template_name]['definition']
                )


            # Template starts with #, i.e. copy of definition of other entity in quest def.
            elif template[0] == '#':
                template_entity_id = self.get_entity_id(entity_alias=template[1:])
                try:
                    if template_entity_id:
                        template_entity_data = self._entity_definitions[template_entity_id]
                    else:
                        raise KeyError
                except KeyError:
                    logger.error(f'Entity definition for entity "{template[1:]}" not found.')
            else:
                try:
                    template_path = Path(ENTITY_PATH / Path(template + '.json'))
                    template_entity_data = get_dict_from_json(template_path)
                except FileNotFoundError:
                    logger.error(f'Entity file "{template_path}" not found.')
                    raise

            logger.info(f'**Creating components from template ""{template}"".')
            self.update_entity(template_entity_data, entity_id=entity_id)
            logger.info(f'**Creating components from template ""{template}"" done.')

        # Initiate every component
        for component in json_ent_obj.get("components", []):

            # Get component type
            comp_type = component.get("type")

            # Get component params
            comp_params = component.get("params", {})

            # Create and add/overwrite component
            try:
                new_comp = self._create_component(comp_type, comp_params)

                self._world.add_component(entity_id, new_comp)

                logger.info(f'***{new_comp} for entity {entity_id} created.')

            except ValueError:
                logger.error(f'Error in creation of component "{comp_type}" with parameters "{comp_params}".')
                raise ValueError

    def create_entity_ex(self, json_ent_obj: dict, entity_alias: str=None) -> int:
        '''Alternative create_entity function using update_entity function

            Parameters:
                :param json_ent_obj: Description of entity in JSON format (python dict).
                :type json_ent_obj: dict

                :param entity_alias: Parameter overrides entity alias that is present in json_ent_obj definition under
                    key 'id'.
                :type entity_alias: str

                #:param register: Should the entity be globally registered with engine.
                #:type register: bool
                
                :returns: Integer specifying entity id

                :raise: ValueError - in case of problem with component creation
        '''

        # Create empty entity
        # First check for explicit alias then for id in json and if nothing found, do not register
        # problem when prescription has id and factory generator is returning none
        entity_id = self.create_empty_entity(entity_alias=entity_alias if entity_alias else json_ent_obj.get("id", None))

        '''
        # Create new entity and get its id
        entity_id = self._world.create_entity()

        # Registration requires entity alias
        if register:

            # Decide on entity alias - either from json dict or from fction call
            entity_alias = entity_alias if entity_alias else json_ent_obj["id"]

            # Update the lookup dictionaries
            self.register_entity_lookup(entity_id=entity_id, entity_alias=entity_alias)

        logger.info(f'*Creating new entity id: "{entity_id}", entity alias: {entity_alias or "unknown"}')
        '''

        # Now add components to this entity id empty envelope
        self.update_entity(json_ent_obj=json_ent_obj, entity_id=entity_id)

        return entity_id

    def copy_entity(self, entity_id: int) -> int:
        '''TBD - Copy entity from existing entity and return entity id 
        of the new entity.'''
        pass

    def delete_entity(self, entity_id: int=None, entity_alias: str=None) -> None:
        ''' Delete and un-register entity from the world.'''

        # Get alias and id
        entity_alias = entity_alias if entity_alias else self._entity_to_alias.get(entity_id, None)
        entity_id = entity_id if entity_id else self._alias_to_entity.get(entity_alias, None)

        # Delete it from Esper world
        self._world.delete_entity(entity_id)

        # Un-register the entity - ignore if not found, can be unregistered entity
        self._unregister_entity_lookup(entity_id=entity_id, entity_alias=entity_alias)

        logger.info(f'Entity id {entity_id} / {entity_alias or "unknown"} deleted.')

    def _clear_entities(self) -> None:
        '''Delete all entities and components from the world'''

        self._world.clear_database()
        logger.info(f'All entities and components cleared.')

    def _clear_processors(self) -> None:

        try:
            self._world.finalize()
        except ValueError as e:
            logger.warn(f'Processor "{e.args[0]}" does not have "finalize" method implemented.')

        logger.info(f'All processors finalized.')

        self._world.clear_processors()
        logger.info(f'All processors removed.')

    def clear_ecs(self) -> None:
        self._clear_entities()
        self._clear_processors()

    def _check_proc_in_world(self, proc: str) -> bool:
        ''' Checks, if the class represented by string exists and is already initiated in the
        game world. Returns True in case the prerequisit processor is present inthe game world.
        Else, returns False.
        '''

        # Unpack the prerequisity processor information
        proc_module, proc_class = proc.split(':')

        # Get the processor class
        try:
            check_class = get_class_object(None, 'pyrpg.core.ecs.processors.' + proc_module, proc_class)
        except ValueError:
            logger.warning(f'Processor class "{proc_module}.{proc_class}" cannot be checked.')
            return False

        # Verify that the processor class has been already instantiated in the game world
        if self._world.get_processor(check_class):
            logger.info(f'Processor "{proc_module}.{proc_class}" is instantiated in the game world.')
            return True
        else:
            logger.warning(f'Processor "{proc_module}.{proc_class}" is not instantiated in the game world.')
            return False

    def _check_proc_prereq(self, proc_class: Processor) -> bool:
        '''Checks if the processor has all necessary prerequisities for
        other processors in the game fulfilled.
        '''

        try:
            prereqs = proc_class.PREREQ
            if not prereqs: return True
        except AttributeError:
            return True    # no prerequisities hence the check is ok

        if json_logic(expr=prereqs, value_fnc=self._check_proc_in_world):
            logger.info(f'Processor "{proc_class.__name__}": Prerequisities are ok!')
            return True
        else:
            logger.warning(f'Processor "{proc_class.__name__}": Problem with prerequisities. Game might work incorrectly!')
            return False
            #raise ValueError(f'Processor "{proc_class.__name__}": Problem with prerequisities. Game might work incorrectly!')

        '''
        for prereq in prereqs:

            # Unpack the prerequisity processor information
            prereq_module, prereq_class = prereq.split(':')

            # Get the prerequisity processor class
            try:
                check_class = get_class_object(None, 'pyrpg.core.ecs.processors.' + prereq_module, prereq_class)
            except ValueError:
                logger.warning(f'Prerequisite class "{prereq_module}.{prereq_class}" cannot be loaded from definition of processor "{proc_class.__name__}".')
                raise ValueError(f'Prerequisite class "{prereq_module}.{prereq_class}" cannot be loaded from definition of processor "{proc_class.__name__}".')

            # Verify that the prerequisite processor class has been already instantiated
            if not self._world.get_processor(check_class):
                logger.warning(f'Processor "{proc_class.__name__}" is missing prereq. processor {prereq_class}. Game might work incorrectly!')
                raise ValueError(f'Processor "{proc_class.__name__}" is missing prereq. processor {prereq_class}. Game might work incorrectly!')
        '''

    def _check_processor(self, proc_class: Processor) -> bool:
        '''Checks if the class representing the processors contains all necessary
        parts in order to successfully work in the game.

        Checks are following:
            - Existence of prerequisited classes in the game world
        '''
        try:
            # Check the prerequisities
            if not self._check_proc_prereq(proc_class):
                return False
            else:
                return True
        except ValueError:
            logger.error(f'Error during checking or prerequisities of the processor class "{proc_class.__name__}".')
            raise ValueError(f'Error during checking or prerequisities of the processor class "{proc_class.__name__}".')

    def _load_processor(self, proc_module : str, proc_class : str, cust_proc_class_attrs : dict) -> Processor:
        '''Imports the processor class and registers it into the world'''

        # Get the definition of the processor class
        try:
            new_class = get_class_object(None, 'pyrpg.core.ecs.processors.' + proc_module, proc_class)
        except ValueError:
            logger.error(f'Error during loading of processor class "{proc_class}".')
            raise ValueError(f'Error during loading of processor class "{proc_class}".')

        # Check that processor has everything that it needs to work in the game
        try:
            if not self._check_processor(new_class):
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

        # Overwrite the attributes with custom attributes from the json definition of the quest
        proc_attrs = {**proc_attrs, **cust_proc_class_attrs}

        # Initiate and return the processor class
        return new_class(**proc_attrs)

    def load_processor(self, processor: list) -> None:
        '''Takes processor definition from the JSON and registers
        it into the game world'''

        # Parse the JSON definition of the processor
        class_path, params = processor
        module_name, class_name = class_path.split(':')

        logger.info(f'Preparing load of processor "{class_name}" .')

        # Create instance of the processor
        new_proc = self._load_processor(module_name, class_name, params)

        # Registers processor at esper ECS World
        new_proc.initialize(register=self._world.add_processor)

        # Log the initiation of the processor
        logger.info(f'Processor "{class_name}" initiated.')

    """Should be obsolete now. It was substituted by load_processor and iteration done on load quest/phase level
    def load_processors(self, processors: list) -> None:
        '''Imports and registers to the world processors specified by the quest definition.'''

        for processor in processors:
            class_path, params = processor
            module_name, class_name = class_path.split(':')

            logger.info(f'Preparing load of processor "{class_name}" .')

            # Create instance of the processor
            new_proc = self._load_processor(module_name, class_name, params)

            # Registers processor at esper ECS World
            new_proc.initialize(register=self._world.add_processor)

            # Log the initiation of the processor
            logger.info(f'Processor "{class_name}" initiated.')
    """

    def process(self, events, keys, dt: float, debug: bool) -> None:
        '''Calls process method on all loaded processors.'''

        self._world.process(events=events, keys=keys, dt=dt, debug=debug)

    """
    def create_entity(self, json_ent_obj: dict, entity_alias: str=None, register: bool=True, child_ref: int=None) -> int:
        ''' OBSOLETE - substituted by create_entity_ex
        Create entity from json definition. See Quest for definitions 

            Parameters:
                :param json_ent_obj: Description of entity in JSON format (python dict).
                :type json_ent_obj: dict

                :param entity_alias: Parameter overrides entity alias that is present in json_ent_obj definition under
                    key 'id'.
                :type entity_alias: str

                :param register: Should the entity be globally registered with engine.
                :type register: bool

                :param child_ref: Used for recursive creation of entity from templates.
                :type child_ref: world.entity Object

                :returns: Integer specifying entity id

                :raise: ValueError - in case of problem with component creation
        '''

        entity_id, entity_alias = None, None

        # Create new entity obj for the root entity
        if not child_ref:
            entity_id = self._world.create_entity()

            # Registration requires entity alias
            if register:

                # Decide on entity alias - either from json dict or from fction call
                entity_alias = entity_alias if entity_alias else json_ent_obj["id"]

                # Update the lookup dictionaries
                self._alias_to_entity.update({entity_alias: entity_id})
                self._entity_to_alias.update({entity_id: entity_alias})

            logger.info(f'*Creating new entity id: "{entity_id}", entity alias: {entity_alias or "unknown"}')


        # Read the components from the templates - order matters! latter has priority and overwrites
        # the previous components
        for template in json_ent_obj.get("templates", []):

            # Read the entity.json
            try:
                template_path = Path(ENTITY_PATH / Path(template + '.json'))
                template_entity_data = get_dict_from_json(template_path)
            except FileNotFoundError:
                logger.error(f'Entity file "{template_path}" not found.')
                raise

            logger.info(f'**Creating components from template ""{template + ".json"}"" - entity_id: {entity_id} vs. child_ref: {child_ref}.')
            self.create_entity(template_entity_data, child_ref=entity_id if not child_ref else child_ref)
            logger.info(f'**Creating components from template ""{template + ".json"}"" done.')

        # Initiate every component
        for component in json_ent_obj.get("components", []):

            # Get component type
            comp_type = component.get("type")

            # Get component params
            comp_params = component.get("params", {})

            # Create component
            try:
                new_comp = self._create_component(comp_type, comp_params)

                # Add new component to the world
                self._world.add_component(entity_id if not child_ref else child_ref, new_comp)

                logger.info(f'***{new_comp} for entity {entity_id if not child_ref else child_ref} created.')

            except ValueError:
                logger.error(f'Error in creation of component "{comp_type}" with parameters "{comp_params}".')
                raise ValueError

        return entity_id
    """
