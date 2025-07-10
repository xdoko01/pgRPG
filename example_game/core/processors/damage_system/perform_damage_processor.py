__all__ = ['PerformDamageSingleProcessor', 'PerformDamageFullProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.damageable import Damageable
from core.components.flag_has_no_health import FlagHasNoHealth
from core.components.flag_was_damaged_by import FlagWasDamagedBy
from core.components.flag_has_damaged import FlagHasDamaged
from core.components.flag_is_about_to_be_damaged_by import FlagIsAboutToBeDamagedBy

# For creation of events
from pyrpg.core.events.event import Event 


# Logger init
logger = logging.getLogger(__name__)

class PerformDamageSingleProcessor(Processor):
    ''' Detects entities that are about to be damaged and performs
    the actual damage if those are damageable.

    Involved components:
        -   Damageable
        -   FlagWasDamagedBy
        -   FlagHasDamaged
        -   FlagHasNoHealth
        -   FlagIsAboutToBeDamagedBy

    Related processors:
        -   GenerateDamageProcessor
        -   RemoveFlagIsAboutToBeDamagedByProcessor
        -   RemoveFlagWasDamagedByProcessor
        -   RemoveFlagHasDamagedProcessor
        -   RemoveFlagHasNoHealthProcessor


    What if this processor is disabled?
        -   entities are not being damaged

    Where the processor should be planned?
        -   after GenerateDamageProcessor
        -   before RemoveFlagWasDamageddByProcessor
        -   before RemoveFlagIsAboutToBeDamagedByProcessor
        -   before RemoveFlagHasNoHealthProcessor

    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'damage_system:GenerateDamageProcessor'
    ]

    def __init__(self, add_event_fnc, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

        # Function that queues new event for processing
        self.add_event_fnc = add_event_fnc


    def process(self, *args, **kwargs):
        ''' Detects entities that are about to be damaged and performs
        the actual damage if those are damageable.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all entities that have Damageable and FlagIsAboutToBeDamagedBy - those are candidates for successful damage
        for ent_damageable, (damageable, flag_is_about_to_be_damaged_by) in self.world.get_components(Damageable, FlagIsAboutToBeDamagedBy):

            # Iterate all entities that are trying to damage ent_damageable
            for damage in flag_is_about_to_be_damaged_by.damages:

                damage_source = damage.parent if damage.parent else damage.entity

                # Add FlagWasDamagedBy to ent_damageable entity
                #self.world.add_component(ent_damageable, FlagWasDamagedBy(entities={damage.entity, damage_source}))
                self.world.add_component(ent_damageable, FlagWasDamagedBy(entities={damage_source}))
                logger.debug(f'({self.cycle}) - Entity {ent_damageable} was damaged by entity {damage.entity}.')

                # Add FlagHasDamaged to ent_damaging entity
                self.world.add_component(damage.entity, FlagHasDamaged(entities={ent_damageable}))
                logger.debug(f'({self.cycle}) - Entity {damage.entity} has damaged entity {ent_damageable}.')

                # Generate the event
                damage_event = Event('DAMAGE', damage_source, ent_damageable, params={'damaging' : damage_source, 'damageable' : ent_damageable})
                self.add_event_fnc(damage_event)

                # Calculate the new damageable.health
                damageable.health = max(damageable.health - damage.damage, 0)
                logger.debug(f'({self.cycle}) - Entity {ent_damageable} health is {damageable.health}.')

                # Check if is destroyed
                if damageable.health == 0:
                    self.world.add_component(ent_damageable, FlagHasNoHealth())

                # Record the damage also on Damageable component - to be able to query this component in command checking if entity has been damaged by someone
                damageable.damages.append(damage)


    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components
        '''
        pass

    def post_load(self):
        ''' Reconfigure the processor after de-serialization by attaching
        the removed references again.
        '''
        pass

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass

class PerformDamageFullProcessor(Processor):
    ''' Detects entities that are about to be damaged and performs
    the actual damage if those are damageable.

    Involved components:
        -   Damageable
        -   FlagWasDamagedBy
        -   FlagHasDamaged
        -   FlagIsAboutToBeDamagedBy

    Related processors:
        -   GenerateDamageProcessor
        -   RemoveFlagIsAboutToBeDamagedByProcessor
        -   RemoveFlagWasDamagedByProcessor
        -   RemoveFlagHasDamagedProcessor

    What if this processor is disabled?
        -   entities are not being damaged

    Where the processor should be planned?
        -   after GenerateDamageProcessor
        -   before RemoveFlagWasDamageddByProcessor
        -   before RemoveFlagIsAboutToBeDamagedByProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'damage_system:GenerateDamageProcessor'
    ]

    def __init__(self, add_event_fnc, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)

        # Function that queues new event for processing
        self.add_event_fnc = add_event_fnc


    def process(self, *args, **kwargs):
        '''  Detects entities that are about to be teleported and performs
        the actual teleportation, if the picker is capable.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all entities that have Damageable and FlagIsAboutToBeDamagedBy - those are candidates for successful damage
        for ent_damageable, (damageable, flag_is_about_to_be_damaged_by) in self.world.get_components(Damageable, FlagIsAboutToBeDamagedBy):

            # Iterate all entities that are trying to damage ent_damageable
            for damage in flag_is_about_to_be_damaged_by.damages:

                damage_source = damage.parent if damage.parent else damage.entity

                # Add FlagWasDamagedBy to ent_damageable entity
                flag_was_damaged_by = self.world.try_component(ent_damageable, FlagWasDamagedBy)
                if flag_was_damaged_by:
                    flag_was_damaged_by.entities.add(damage.entity)
                    flag_was_damaged_by.entities.add(damage_source)
                else:
                    self.world.add_component(ent_damageable, FlagWasDamagedBy(entities={damage.entity, damage_source}))
                logger.debug(f'({self.cycle}) - Entity {ent_damageable} was damaged by entity {damage.entity}, source entity: {damage_source}.')

                # Add FlagHasDamaged to ent_damaging entity
                flag_has_damaged = self.world.try_component(damage.entity, FlagHasDamaged)
                if flag_has_damaged:
                    flag_has_damaged.entities.add(ent_damageable)
                else:
                    self.world.add_component(damage.entity, FlagHasDamaged(entities={ent_damageable}))
                logger.debug(f'({self.cycle}) - Entity {damage.entity} has damaged entity {ent_damageable}.')

                # Generate the event
                damage_event = Event('DAMAGE', damage_source, ent_damageable, params={'damaging' : damage_source, 'damageable' : ent_damageable})
                self.add_event_fnc(damage_event)

                # Calculate the new damageable.health
                damageable.health = max(damageable.health - damage.damage, 0)
                logger.debug(f'({self.cycle}) - Entity {ent_damageable} health is {damageable.health}.')

                # Check if is destroyed
                if damageable.health == 0:
                    self.world.add_component(ent_damageable, FlagHasNoHealth())


    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components
        '''
        pass

    def post_load(self):
        ''' Reconfigure the processor after de-serialization by attaching
        the removed references again.
        '''
        pass

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass

