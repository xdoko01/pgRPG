"""ECS framework based on esper 1.3 (MIT license) with extended features.

Extensions beyond the original esper:
    - Processor groups: processors can be assigned to named groups and
      processed independently via ``World.process(proc_group_id)``.
    - Execution throttling: ``Processor.exec_cycle_step`` lets a processor
      run every N cycles instead of every frame.
    - Extended queries: ``get_components_ex`` / ``get_components_exs`` /
      ``get_components_opt`` for include/exclude/optional component filtering.
    - ``SkipProcessorExecution`` exception to skip a processor's current
      cycle without treating it as an error.

See https://github.com/benmoran56/esper for the original esper project.
"""

import logging
logger = logging.getLogger(__name__)

import pygame # for get_ticks function

from functools import lru_cache as _lru_cache
from typing import List, Type, Any, Iterable, Optional

from collections import defaultdict # Added by xdoko01 to support processor groups

import sys

class Component(object):
    """Base class for all Components.

    Subclasses must use ``__slots__`` for memory efficiency. Inheriting
    from ``object`` explicitly is required for ``__slots__`` to work.
    """

    def __init__(self):
        """Initialize the component (override in subclasses)."""
        pass

    def reinit(self):
        """Reinitialize after a display configuration change."""
        pass

    def __str__(self):
        """Return a string representation including all slot values."""
        slots_dict = {k : getattr(self, k) for k in self.__slots__} # get content of slots for print
        return f"Component '{self.__class__.__name__}' at {hex(id(self))} ({sys.getsizeof(self)} bytes): {slots_dict}"

    def pre_save(self):
        """Prepare for serialization by removing non-serializable references."""
        pass

    def post_load(self):
        """Restore non-serializable references after deserialization."""
        pass

class SkipProcessorExecution(Exception): ...

class Processor:
    """Base class for all Processors to inherit from.

    Processor instances must contain a `process` method. Other than that,
    you are free to add any additional methods that are necessary. The process
    method will be called by each call to `World.process`, so you will
    generally want to iterate over entities with one (or more) calls to the
    appropriate world methods there, such as
    `for ent, (rend, vel) in self.world.get_components(Renderable, Velocity):`
    """
    world = None
    cycle = None # Added by xdoko01 to note the cycle of processor for debug reasons
    exec_cycle_step = None # Added by xdoko01 to note that the process fnc should be called every exec_cycle, ie. not every cycle

    def __init__(self, *args, **kwargs):
        """Initialize cycle counter and execution throttle.

        Args:
            **kwargs: Accepts ``step`` (int) to set ``exec_cycle_step``.
        """
        self.cycle = 0
        self.exec_cycle_step = kwargs.get('step', 1)

    def reinit(self):
        """Reinitialize after a display configuration change."""
        pass

    def initialize(self, register, proc_group_id: str='default'):
        """Register this processor with the World via the register callback.

        Args:
            register: Callable ``(processor, group_id)`` to add the processor.
            proc_group_id: Processor group to register into.
        """
        logger.debug(f'About to initialize Processor instance "{self}" using function "{register}" with the processor group "{proc_group_id}".')
        register(self, proc_group_id)
        logger.debug(f'Initialization of Processor instance "{self}" with the processor group "{proc_group_id}" is done.')
        #raise NotImplementedError

    def process(self, *args, **kwargs):
        """Advance the cycle counter and skip if not on the execution step.

        Subclasses must call ``super().process()`` first to handle throttling.

        Raises:
            SkipProcessorExecution: When the current cycle is not a
                multiple of ``exec_cycle_step``.
        """
        self.cycle += 1
        if self.cycle % self.exec_cycle_step != 0: raise SkipProcessorExecution


    def __str__(self):
        return f"Processor '{self.__class__.__name__}' at {hex(id(self))}: {self.__dict__}"

    def pre_save(self, *args, **kwargs):
        """Prepare for serialization by removing non-serializable references."""
        raise NotImplementedError

    def post_load(self, *args, **kwargs):
        """Restore references after deserialization."""
        raise NotImplementedError

    def finalize(self, *args, **kwargs):
        """Clean up resources before program exit (e.g. close open files)."""
        raise NotImplementedError

class World:
    """A World object keeps track of all Entities, Components, and Processors.

    A World contains a database of all Entity/Component assignments. The World
    is also responsible for executing all Processors assigned to it for each
    frame of your game.
    """
    def __init__(self, timed=False):
        # self._processors = []
        self._processors = defaultdict(list) # modified by xdoko01 to support processor groups
        self._next_entity_id = 0
        self._components = {}
        self._entities = {}
        self._dead_entities = set()
        if timed:
            self.process_times = defaultdict(int) # modified by xdoko01 to support summed times
            self._process = self._timed_process

    def clear_cache(self) -> None:
        self.get_component.cache_clear()
        self.get_components.cache_clear()
        self.get_components_ex.cache_clear() # additionally added
        self.get_components_exs.cache_clear() #additionally added
        self.get_components_opt.cache_clear() #additionally added


    def clear_database(self) -> None:
        """Remove all Entities and Components from the World."""
        self._next_entity_id = 0
        self._dead_entities.clear()
        self._components.clear()
        self._entities.clear()
        self.clear_cache()

    def add_processor(self, processor_instance: Processor, proc_group_id: str='default', priority=0) -> None:
        """Add a Processor instance to the World.

        Args:
            processor_instance: A Processor subclass instance.
            proc_group_id: Group to assign the processor to.
            priority: Higher number means processed first.
        """
        assert issubclass(processor_instance.__class__, Processor)
        processor_instance.priority = priority
        processor_instance.world = self

        self._processors[proc_group_id].append(processor_instance) # changed by xdoko01 to support processor groups
        self._processors[proc_group_id].sort(key=lambda proc: proc.priority, reverse=True) # changed by xdoko01 to support processor groups

        logger.debug(f'Processor instance "{processor_instance}" added to the processor group "{proc_group_id}".')
        logger.debug(f'Processor Group "{proc_group_id}" now contains the following processors: "{self._processors[proc_group_id]}".')

    def remove_processor(self, processor_type: Processor, proc_group_id: str='default') -> None:
        """Remove a Processor from the World by type.

        Args:
            processor_type: The class type of the Processor to remove.
            proc_group_id: Group to remove the processor from.
        """
        #for processor in self._processors:
        for processor in self._processors[proc_group_id]: # changed by xdoko01 to support processor groups
            if type(processor) == processor_type:
                processor.world = None
                self._processors[proc_group_id].remove(processor) # changed by xdoko01 to suppoet processor groups

    def clear_processors(self) -> None:
        """Remove all processors from all groups."""
        for proc_group_id, proc_group in self._processors.copy().items():
            for processor in proc_group:
                processor.world = None
                self._processors[proc_group_id].remove(processor)

    def get_processor(self, processor_type: type[Processor], proc_group_id: str='default') -> Processor:
        """Get a Processor instance by type.

        Args:
            processor_type: The Processor class type to retrieve.
            proc_group_id: Group to search in.

        Returns:
            The matching Processor instance, or None if not found.
        """

        for processor in self._processors[proc_group_id]:
            if type(processor) == processor_type:
                return processor

    def create_entity(self, *components) -> int:
        """Create a new Entity, optionally with initial Components.

        Args:
            *components: Component instances to assign to the new Entity.

        Returns:
            The new Entity's integer ID.
        """
        self._next_entity_id += 1

        # TODO: duplicate add_component code here for performance
        for component in components:
            self.add_component(self._next_entity_id, component)

        # self.clear_cache()
        return self._next_entity_id

    def delete_entity(self, entity: int, immediate=False) -> None:
        """Delete an Entity and all its Components from the World.

        By default deletion is deferred until the next ``World.process()``
        call. Use ``immediate=True`` only outside entity iteration.

        Args:
            entity: The Entity ID to delete.
            immediate: If True, delete immediately instead of deferring.

        Raises:
            KeyError: If the entity does not exist.
        """
        if immediate:

            for component_type in self._entities[entity]:
                self._components[component_type].discard(entity)

                if not self._components[component_type]:
                    del self._components[component_type]

            del self._entities[entity]
            self.clear_cache()

        else:
            self._dead_entities.add(entity)

    def component_for_entity(self, entity: int, component_type: type[Component]) -> Component:
        """Retrieve a specific Component instance for an Entity.

        Args:
            entity: The Entity ID.
            component_type: The Component class type to retrieve.

        Returns:
            The Component instance.

        Raises:
            KeyError: If the Entity or Component type does not exist.
        """
        return self._entities[entity][component_type]

    def components_for_entity(self, entity: int) -> tuple[Component, ...]:
        """Retrieve all Components for an Entity as a tuple.

        Args:
            entity: The Entity ID.

        Returns:
            Tuple of all Component instances assigned to the Entity.

        Raises:
            KeyError: If the entity does not exist.
        """
        return tuple(self._entities[entity].values())

    def has_component(self, entity: int, component_type: Any) -> bool:
        """Check if an Entity has a Component of a certain type."""
        return component_type in self._entities[entity]

    def has_components(self, entity: int, *component_types: Any) -> bool:
        """Check if an Entity has all of the specified Component types."""
        return all(comp_type in self._entities[entity] for comp_type in component_types)

    def add_component(self, entity: int, component_instance: Any) -> None:
        """Add a Component instance to an Entity (replaces if type exists).

        Args:
            entity: The Entity ID.
            component_instance: The Component instance to add.
        """
        component_type = type(component_instance)

        if component_type not in self._components:
            self._components[component_type] = set()

        self._components[component_type].add(entity)

        if entity not in self._entities:
            self._entities[entity] = {}

        self._entities[entity][component_type] = component_instance
        self.clear_cache()

    def remove_component(self, entity: int, component_type: Any) -> int:
        """Remove a Component from an Entity by type.

        Args:
            entity: The Entity ID.
            component_type: The Component class type to remove.

        Returns:
            The entity ID.

        Raises:
            KeyError: If the entity or component type does not exist.
        """
        self._components[component_type].discard(entity)

        if not self._components[component_type]:
            del self._components[component_type]

        del self._entities[entity][component_type]

        if not self._entities[entity]:
            del self._entities[entity]

        self.clear_cache()
        return entity

    def remove_component_force(self, entity: int, component_type: Any) -> int:
        """Remove a Component from an Entity, silently ignoring missing entries.

        Same as ``remove_component`` but returns None instead of raising
        KeyError if the entity or component type does not exist.

        Args:
            entity: The Entity ID.
            component_type: The Component class type to remove.

        Returns:
            The entity ID, or None if not found.
        """
        try:
            self._components[component_type].discard(entity)

            if not self._components[component_type]:
                del self._components[component_type]

            del self._entities[entity][component_type]

            if not self._entities[entity]:
                del self._entities[entity]

            self.clear_cache()
            return entity
        except KeyError:
            return None

    def _get_component(self, component_type: type[Component]) -> Iterable[tuple[int, Component]]:
        """Yield (entity_id, component) pairs for a single Component type."""
        entity_db = self._entities

        for entity in self._components.get(component_type, []):
            yield entity, entity_db[entity][component_type]

    def _get_components(self, *component_types: Type) -> Iterable[tuple[int, ...]]:
        """Yield (entity_id, [comp1, comp2, ...]) for entities having all types."""
        entity_db = self._entities
        comp_db = self._components

        try:
            for entity in set.intersection(*[comp_db[ct] for ct in component_types]):
                yield entity, [entity_db[entity][ct] for ct in component_types]
        except KeyError:
            pass

    def _get_components_ex(self, *component_types: Type, **kwargs) -> Iterable[tuple[int, ...]]:
        """Yield entities with all included types, excluding one type.

        Args:
            *component_types: Component types to require.
            **kwargs: ``exclude`` — a single Component type to exclude.

        Example:
            ``_get_components_ex(Pos, Move, Render, exclude=Ai)``
        """
        entity_db = self._entities
        comp_db = self._components
        exclude_component_type = kwargs.get('exclude', None)

        """
        comp_db ... is dictionary
        {
            <class 'pgrpg.core.ecs.components.collidable.Collidable'>: {1}, 
            <class 'pgrpg.core.ecs.components.renderable_model.RenderableModel'>: {1}, 
            <class 'pgrpg.core.ecs.components.controllable.Controllable'>: {1}, 
            <class 'pgrpg.core.ecs.components.position.Position'>: {1}, 
            <class 'pgrpg.core.ecs.components.movable.Movable'>: {1}, 
            <class 'pgrpg.core.ecs.components.camera.Camera'>: {1}
        }

        [comp_db[ct] for ct in component_types] ... ex. for 2 components in component types ... [{1}, {1,2}]
        set.intersection(*[comp_db[ct] for ct in component_types]) ... ex for 2 components above ... {1}

        .difference(comp_db.get(exclude_component_type, {})) ... must be done using get in case no entity has the component assigned, it will fail on KeyError
        """

        try:
            for entity in set.intersection(*[comp_db[ct] for ct in component_types]).difference(comp_db.get(exclude_component_type, {})):
                yield entity, [entity_db[entity][ct] for ct in component_types]
        except KeyError:
            pass

    def _get_components_exs(self, **kwargs) -> Iterable[tuple[int, ...]]:
        """Yield entities with all included types, excluding multiple types.

        Args:
            **kwargs: ``include`` — tuple of required Component types.
                ``exclude`` — tuple of Component types to exclude.

        Example:
            ``_get_components_exs(include=(Pos, Move), exclude=(Ai, Attack))``
        """
        entity_db = self._entities
        comp_db = self._components
        include_component_types = kwargs.get('include', None)
        exclude_component_types = kwargs.get('exclude', None)

        try:
            #It is important to specify the difference with .get(ct, {}). If component does not exist as a key in comp_db, it must return empty set otherwise exception is thrown and passed
            for entity in set.intersection(*[comp_db[ct] for ct in include_component_types]).difference(*[comp_db.get(ct, {}) for ct in exclude_component_types]):
                yield entity, [entity_db[entity][ct] for ct in include_component_types]
        except KeyError:
            pass

    def _get_components_opt(self, *component_types: Type, **kwargs) -> Iterable[tuple[int, ...]]:
        """Yield entities with required types plus an optional Component (or None).

        Args:
            *component_types: Required Component types.
            **kwargs: ``optional`` — a Component type returned as None if missing.
        """
        entity_db = self._entities
        comp_db = self._components
        optional_component_type = kwargs.get('optional')

        try:
            for entity in set.intersection(*[comp_db[ct] for ct in component_types]):
                # If the component for entity is not in the database, return None
                yield entity, [entity_db[entity].get(ct, None) for ct in [*component_types, optional_component_type]]
        except KeyError:
            pass

    @_lru_cache()
    def get_component(self, component_type: type[Component]) -> list[tuple[int, Component]]:
        return [query for query in self._get_component(component_type)]

    @_lru_cache()
    def get_components(self, *component_types: type):
        return [query for query in self._get_components(*component_types)]

    @_lru_cache()
    def get_components_exs(self, **kwargs):
        return [query for query in self._get_components_exs(**kwargs)]

    @_lru_cache()
    def get_components_ex(self, *component_types: type, **kwargs):
        return [query for query in self._get_components_ex(*component_types, **kwargs)]

    @_lru_cache()
    def get_components_opt(self, *component_types: type, **kwargs):
        return [query for query in self._get_components_opt(*component_types, **kwargs)]


    def try_component(self, entity: int, component_type: type[Component]) -> Optional[Component]:
        """Return a Component for an Entity, or None if it doesn't exist."""
        if component_type in self._entities[entity]:
            return self._entities[entity][component_type]
        else:
            return None

    def try_components(self, entity: int, *component_types: type):
        """Yield all requested Components for an Entity, or None if any are missing."""
        if all(comp_type in self._entities[entity] for comp_type in component_types):
            yield [self._entities[entity][comp_type] for comp_type in component_types]
        else:
            return None

    def _clear_dead_entities(self):
        """Finalize deletion of any Entities that are marked dead.
        
        In the interest of performance, this method duplicates code from the
        `delete_entity` method. If that method is changed, those changes should
        be duplicated here as well.
        """
        for entity in self._dead_entities:

            for component_type in self._entities[entity]:
                self._components[component_type].discard(entity)

                if not self._components[component_type]:
                    del self._components[component_type]

            del self._entities[entity]

        self._dead_entities.clear()
        self.clear_cache()

    def _process(self, proc_group_id: str='default', *args, **kwargs):
        
        for processor in self._processors[proc_group_id]:
            processor.process(*args, **kwargs)

    def _timed_process(self, proc_group_id: str='default', *args, **kwargs):
        """Track Processor execution time for benchmarking."""
        
        '''old code using time library
        for processor in self._processors[proc_group_id]:
            start_time = _time.process_time()
            processor.process(*args, **kwargs)
            process_time = int(round((_time.process_time() - start_time) * 1000, 2))
            self.process_times[processor.__class__.__name__] = process_time
        '''

        for processor in self._processors[proc_group_id]:
            start_time = pygame.time.get_ticks()
            processor.process(*args, **kwargs)
            process_time = pygame.time.get_ticks() - start_time
            self.process_times[processor.__class__.__name__] += process_time # cumulate the process times in ms

    def process(self, proc_group_id: str='default', *args, **kwargs) -> None:
        """Process all Processors in priority order, clearing dead entities first.

        Args:
            proc_group_id: Which processor group to run.
            *args: Forwarded to each Processor's ``process()`` method.
            **kwargs: Forwarded to each Processor's ``process()`` method.
        """
        self._clear_dead_entities()
        self._process(proc_group_id, *args, **kwargs)

    def _finalize(self, proc_group_id: str='default', *args, **kwargs) -> None:
        """Call finalize on all Processors in a group."""
        for processor in self._processors[proc_group_id]:
            try:
                processor.finalize(*args, **kwargs)
            except NotImplementedError:
                raise ValueError(processor)

    def finalize_group(self, proc_group_id: str='default', *args, **kwargs) -> None:
        """Call finalize on all Processors in a specific group."""
        self._finalize(proc_group_id=proc_group_id, *args, **kwargs)

    def finalize(self, *args, **kwargs) -> None:
        """Call finalize on all Processors across all groups."""
        for proc_group_id in self._processors:
            self.finalize_group(proc_group_id=proc_group_id, *args, **kwargs)
