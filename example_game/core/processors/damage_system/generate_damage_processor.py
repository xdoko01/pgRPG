__all__ = ['GenerateDamageSingleProcessor', 'GenerateDamageFullProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.damaging import Damaging
from core.components.flag_has_collided import FlagHasCollided
from core.components.flag_is_about_to_be_damaged_by import FlagIsAboutToBeDamagedBy

from collections import namedtuple # for representation of damages

# Class storing the damage information
Damage = namedtuple('Damage', ['entity', 'parent', 'damage'])

# Logger init
logger = logging.getLogger(__name__)

class GenerateDamageSingleProcessor(Processor):
    ''' Detects entities that are damaging + have collided and assigns
    the FlagIsAboutToBeDamagedBy to all entities that collided with them.

    This single version always overwrites existing FlagIsAboutToBeDamagedBy
    flag and hence entity can be damaged only by one other entity in one given
    cycle.

    Involved components:
        -   Damaging
        -   FlagIsAboutToBeDamagedBy

    Related processors:
        -   PerformDamageProcessor
        -   RemoveFlagIsAboutToBeDamagedByProcessor

    What if this processor is disabled?
        -   entities are not being damaged

    Where the processor should be planned?
        -   after GenerateEntityCollisionsProcessor
        -   before RemoveFlagIsAboutToBeDamagedByProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'collision_system:GenerateCollisionsProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        '''  Detects entities that are pickable + have collided and assigns
        the FlagIsAboutToPickEntity to their pickers
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all entities that have Damaging and FlagHasCollided - those are candidates for causing damage
        for ent_damaging, (damaging, flag_has_collided) in self.world.get_components(Damaging, FlagHasCollided):

            # Assign the FlagIsAboutToBeDamagedBy to ALL entities that collided with damaging entity ent_damaging
            for collision in flag_has_collided.collisions:

                self.world.add_component(
                    collision.entity, 
                    FlagIsAboutToBeDamagedBy(
                        damages=[Damage(entity=ent_damaging, parent=damaging.parent, damage=damaging.damage)]
                    )
                )

                logger.debug(f'({self.cycle}) - Entity {collision.entity} is trying to be damaged by {ent_damaging}.')

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

class GenerateDamageFullProcessor(Processor):
    ''' Detects entities that are damaging + have collided and assigns
    the FlagIsAboutToBeDamagedBy to all entities that collided with them.

    This full version always makes sure that in FlagIsAboutToBeDamagedBy
    all damaging entities are present.

    Involved components:
        -   Damaging
        -   FlagIsAboutToBeDamagedBy

    Related processors:
        -   PerformDamageProcessor
        -   RemoveFlagIsAboutToBeDamagedByProcessor

    What if this processor is disabled?
        -   entities are not being damaged

    Where the processor should be planned?
        -   after GenerateEntityCollisionsProcessor
        -   before RemoveFlagIsAboutToBeDamagedByProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'collision_system:GenerateCollisionsProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        '''  Detects entities that are pickable + have collided and assigns
        the FlagIsAboutToPickEntity to their pickers
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get all entities that have Damaging and FlagHasCollided - those are candidates for causing damage
        for ent_damaging, (damaging, flag_has_collided) in self.world.get_components(Damaging, FlagHasCollided):

            # Assign the FlagIsAboutToBeDamagedBy to ALL entities that collided with damaging entity ent_damaging
            for collision in flag_has_collided.collisions:

                # Check if the collision entity already has FlagIsAboutToBeDamagedBy assigned. If yes, then
                # get existing FlagIsAboutToBeDamagedBy.entities and add to the set also ent_damaging. Else,
                # add new FlagIsAboutToBeDamagedBy component with one set item = ent_damaging.
                flag_is_about_to_be_damaged_by = self.world.try_component(collision.entity, FlagIsAboutToBeDamagedBy)

                if flag_is_about_to_be_damaged_by:
                    flag_is_about_to_be_damaged_by.entities.append(Damage(entity=ent_damaging, parent=damaging.parent, damage=damaging.damage))
                else:
                    self.world.add_component(
                        collision.entity, 
                        FlagIsAboutToBeDamagedBy(
                            damages=[Damage(entity=ent_damaging, parent=damaging.parent, damage=damaging.damage)]
                        )
                    )
                
                logger.debug(f'({self.cycle}) - Entity {ent_damaging} is trying to damage entity {collision.entity}.')

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


