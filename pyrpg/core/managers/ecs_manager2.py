import logging
from esper import World, Processor
from functools import lru_cache

# Create logger
logger = logging.getLogger(__name__)

class ECSManager:
    '''Facade over the esper.World class'''

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

    ###############
    ## ESPER PART
    ###############
    
    def esp_clear_cache(self) -> None:
        self._world.clear_cache()

    def esp_clear_database(self) -> None:
        self._world.clear_database()

    def esp_add_processor(self, processor_instance, priority=0) -> None:
        self._world.add_processor(processor_instance, priority)

    def esp_remove_processor(self, processor_type) -> None:
        self._world.remove_processor(processor_type)

    def esp_get_processor(self, processor_type) -> Processor:
        return self._world.get_processor(processor_type)

    def esp_create_entity(self, *components) -> int:
        return self._world.create_entity(*components)

    def esp_delete_entity(self, entity: int, immediate: bool = False) -> None:
        self._world.delete_entity(entity, immediate)

    def esp_entity_exists(self, entity: int) -> bool:
        return self._world.entity_exists(entity)

    def esp_component_for_entity(self, entity: int, component_type):
        return self._world.component_for_entity(entity, component_type)

    def esp_components_for_entity(self, entity: int) -> tuple:
        return self._world.components_for_entity(entity)

    def esp_has_component(self, entity: int, component_type) -> bool:
        return self._world.has_component(entity, component_type)

    def esp_has_components(self, entity: int, *component_types) -> bool:
        return self._world.has_components(entity, *component_types)

    def esp_add_component(self, entity: int, component_instance, type_alias=None) -> None:
        self._world.add_component(entity, component_instance, type_alias)

    def esp_remove_component(self, entity: int, component_type) -> int:
        return self._world.remove_component(entity, component_type)

    def esp_remove_component_force(self, entity: int, component_type) -> int:
        try:
            return self.esp_remove_component(entity, component_type)
        except KeyError:
            return None

    def _esp_get_component(self, component_type):
        yield self._world._get_component(component_type)

    def _esp_get_components(self, *component_types):
        yield self._world._get_components(*component_types)

    def _esp_get_components_ex(self, *component_types, **kwargs):
        """Get an iterator for Entity and multiple Component sets + excluding entities
        that have one specific component_type.

        :param component_types: Two or more Component types to include in a list.
        :param exclude: One Component type to exclude in a list.
        :return: An iterator for Entity, (Component1, Component2, etc)
        tuples.

        example:

        _get_components_ex(c.Pos, c.Move, c.Render, exclude=c.Ai)
        """
        entity_db = self._world._entities
        comp_db = self._world._components
        exclude_component_type = kwargs.get('exclude', None)

        try:
            for entity in set.intersection(*[comp_db[ct] for ct in component_types]).difference(comp_db.get(exclude_component_type, {})):
                yield entity, [entity_db[entity][ct] for ct in component_types]
        except KeyError:
            pass

    def _esp_get_components_exs(self, **kwargs):
        """Get an iterator for Entity and multiple Component sets + excluding entities
        that are in exclude_component_types.

        :param include: Two or more Component types to include in a list.
        :param exclude: Two or more Component types to exclude in a list.
        :return: An iterator for Entity, (Component1, Component2, etc)
        tuples.

        example:

        _get_components_exs(include=(c.Pos, c.Move, c.Render), exclude=(c.Ai, c.Attack))
        """
        entity_db = self._world._entities
        comp_db = self._world._components
        include_component_types = kwargs.get('include', None)
        exclude_component_types = kwargs.get('exclude', None)

        try:
            #It is important to specify the difference with .get(ct, {}). If component does not exist as a key in comp_db, it must return empty set otherwise exception is thrown and passed
            for entity in set.intersection(*[comp_db[ct] for ct in include_component_types]).difference(*[comp_db.get(ct, {}) for ct in exclude_component_types]):
                yield entity, [entity_db[entity][ct] for ct in include_component_types]
        except KeyError:
            pass

    def _esp_get_components_opt(self, *component_types, **kwargs):
        """Get an iterator for Entity and multiple Component sets.

        :param component_types: Two or more Component types.
        :param optional: Component type whose entity should be returned also or None if entity does not have it
        :return: An iterator for Entity, (Component1, Component2, etc)
        tuples.
        """
        entity_db = self._world._entities
        comp_db = self._world._components
        optional_component_type = kwargs.get('optional')

        try:
            for entity in set.intersection(*[comp_db[ct] for ct in component_types]):
                # If the component for entity is not in the database, return None
                yield entity, [entity_db[entity].get(ct, None) for ct in [*component_types, optional_component_type]]
        except KeyError:
            pass

    def esp_get_component(self, component_type):
        return self._world.get_component(component_type)

    def esp_get_components(self, *component_types):
        return self._world.get_components(*component_types)

    @lru_cache
    def esp_get_components_ex(self, *component_types, **kwargs):
        return [query for query in self._esp_get_components_ex(*component_types, **kwargs)]

    @lru_cache
    def esp_get_components_exs(self, **kwargs):
        return [query for query in self._esp_get_components_exs(**kwargs)]

    @lru_cache
    def esp_get_components_opt(self, *component_types, **kwargs):
        return [query for query in self._esp_get_components_opt(*component_types, **kwargs)]

    def esp_try_component(self, entity: int, component_type):
        return self._world.try_component(entity, component_type)

    def esp_try_components(self, entity: int, *component_types):
        return self._world.try_components(entity, *component_types)

    def _esp_clear_dead_entities(self):
        self._world._clear_dead_entities()

    def _esp_process(self, *args, **kwargs):
        self._world._process(*args, **kwargs)

    def _esp_timed_process(self, *args, **kwargs):
        self._world._timed_process(*args, **kwargs)

    def esp_process(self, *args, **kwargs):
        self._world.process(self, *args, **kwargs)
    
    def _esp_finalize(self, *args, **kwargs):
        for processor in self._world._processors:
            try:
                processor.finalize(*args, **kwargs)
            except NotImplementedError:
                raise ValueError(processor)
    
    def esp_finalize(self, *args, **kwargs):
        """ Added by xdoko01
        Call the finalize method on all Processors, in order of their priority.

        Call the *finalize* method on all assigned Processors, respecting their
        optional priority setting.

        :param args: Optional arguments that will be passed through to the
                     *finalize* method of all Processors.
        """
        self._esp_finalize(*args, **kwargs)


if __name__ == '__main__':

    class PosComp:
        def __init__(self):
            self.desc = 'I am Position Component'

    class RenModComp:
        def __init__(self):
            self.desc = 'I am RenderableModel Component'

    class MovComp:
        def __init__(self):
            self.desc = 'I am Movable Component'

    class FlagDoMoveComp:
        def __init__(self):
            self.desc = 'I am FlagDoMove Component'

    class FlagDoAttackComp:
        def __init__(self):
            self.desc = 'I am FlagDoAttack Component'

    class IsDeadComp:
        def __init__(self):
            self.desc = 'I am IsDead Component'


    ecs_manager = ECSManager()
    ecs_manager.initialize(timed=False, game_functions={})

    pos_comp_1 = PosComp()
    pos_comp_2 = PosComp()
    pos_comp_3 = PosComp()
    pos_comp_4 = PosComp()

    ren_mod_comp_1 = RenModComp()
    ren_mod_comp_2 = RenModComp()
    ren_mod_comp_3 = RenModComp()
    ren_mod_comp_4 = RenModComp()

    mov_comp_1 = MovComp()
    mov_comp_2 = MovComp()
    mov_comp_3 = MovComp()
    mov_comp_4 = MovComp()

    flag_do_move_comp_1 = FlagDoMoveComp()
    flag_do_move_comp_2 = FlagDoMoveComp()
    flag_do_move_comp_3 = FlagDoMoveComp()
    flag_do_move_comp_4 = FlagDoMoveComp()

    flag_do_attack_comp_1 = FlagDoAttackComp()
    flag_do_attack_comp_2 = FlagDoAttackComp()
    flag_do_attack_comp_3 = FlagDoAttackComp()
    flag_do_attack_comp_4 = FlagDoAttackComp()

    e1 = ecs_manager.esp_create_entity(pos_comp_1, 	ren_mod_comp_1, mov_comp_1, flag_do_move_comp_1)
    e2 = ecs_manager.esp_create_entity(				ren_mod_comp_2, mov_comp_2, flag_do_move_comp_2, flag_do_attack_comp_2)
    e3 = ecs_manager.esp_create_entity(				ren_mod_comp_3, mov_comp_3, flag_do_move_comp_3)
    e4 = ecs_manager.esp_create_entity(pos_comp_4,	ren_mod_comp_4, mov_comp_4)


    # Get all components for entity
    print(f'Components for e1 are: {ecs_manager.esp_components_for_entity(e1)}')

    # Get all entities that have PosComp
    print('*** Get all entities that have PosComp')
    for ent, pos in ecs_manager.esp_get_component(PosComp):
        print(f'Entity: {ent}, Component: {pos}')

    # Get all entities that have PosComp and FlagDoAttactComp
    print('*** Get all entities that have PosComp and FlagDoAttactComp')
    for ent, (pos, attack) in ecs_manager.esp_get_components(PosComp, FlagDoAttackComp):
        print(f'Entity: {ent}, Component: {pos}, Component: {attack}')

    # Get all entities that have PosComp, RenModComp  and do not have FlagDoAttactComp
    print('*** Get all entities that have PosComp, RenModComp and do not have FlagDoAttactComp')
    for ent, (pos, ren_mod) in ecs_manager.esp_get_components_ex(PosComp, RenModComp, exclude=FlagDoAttackComp):
        print(f'Entity: {ent}, Component: {pos}, Component: {ren_mod}')

    # Get all entities that have PosComp, RenModComp  and do not have FlagDoAttactComp, FlagDoMoveComp
    print('*** Get all entities that have PosComp, RenModComp and do not have FlagDoAttactComp, FlagDoMoveComp')
    for ent, (pos, ren_mod) in ecs_manager.esp_get_components_exs(include=(PosComp, RenModComp), exclude=(FlagDoAttackComp, FlagDoMoveComp)):
        print(f'Entity: {ent}, Component: {pos}, Component: {ren_mod}')

    # Get all entities that have RenModComp, MovComp and do not have FlagDoAttactComp, FlagDoMoveComp
    print('*** Get all entities that have RenModComp, MovComp and do not have FlagDoAttactComp, FlagDoMoveComp')
    for ent, (mov, ren_mod) in ecs_manager.esp_get_components_exs(include=(MovComp, RenModComp), exclude=(FlagDoAttackComp, FlagDoMoveComp, IsDeadComp)):
        print(f'Entity: {ent}, Component: {mov}, Component: {ren_mod}')





