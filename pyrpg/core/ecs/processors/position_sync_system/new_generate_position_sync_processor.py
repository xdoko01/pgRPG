__all__ = ['NewGeneratePositionSyncProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

# Logger init
logger = logging.getLogger(__name__)


class NewGeneratePositionSyncProcessor(esper.Processor):
    ''' Detects entities that need to have position aligned with the 
    parent position in order to display animations correctly.

    Involved components:
        -   Position
        -   NewFlagSyncPosition
        -   NewFlagDoMove

    Related processors:
        -   NewPerformPositionSyncProcessor
        -   NewRemoveFlagSyncPositionProcessor

    What if this processor is disabled?
        -   wrong animated weapons and wearables

    Where the processor should be planned?
        -   before rendering
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['']


    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()


    def process(self, *args, **kwargs):
        '''  Detects entities that need to follow master entity position.
        '''
        self.cycle += 1


 - WeaponInUse + Position + HasWeapon + FlagDoMove -> on active weapon add FlagSyncPosition(x,y,map, dir, dir_name)

        # Get all entities that have Pickable and NewFlagHasCollided - those are candidates for pickup
        for ent_parent, (position, weapon_in_use, flag_do_move) in self.world.get_components(components.Position, components.NewWeaponInUse, components.NewFlagDoMove):

            # Assign the NewFlagSyncPosition to actively used weapon so that the animation is aligned (all is done because of rendering)
            TBContinued
            for ent_picker, _, _, _ in flag_has_collided.collisions:

                self.world.add_component(ent_picker, components.NewFlagIsAboutToPickEntity(entity_for_pickup=ent_pickable))
                logger.debug(f'({self.cycle}) - Entity {ent_picker} is trying to pick entity {ent_pickable}.')


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

