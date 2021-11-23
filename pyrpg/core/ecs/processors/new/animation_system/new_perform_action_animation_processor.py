__all__ = ['NewPerformActionAnimationProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

from ..functions import filter_only_visible


# Logger init
logger = logging.getLogger(__name__)


class NewPerformActionAnimationProcessor(esper.Processor):
    ''' Sets action animation for RenderableModel entities that have performed attack
    and are displayed.

    Involved components:
        -   RenderableModel
        -   NewFlagDoAttack
        -   WeaponInUse

    Related processors:
        -   NewPerformIdleAnimationProcessor
        -   NewPerformFrameUpdateProcessor

    What if this processor is disabled?
        -   entities are not animated while attacking

    Where the processor should be planned?
        -   after NewPerformCommandProcessor - due to movement commands generating FlagDoMove
        -   after NewPerformIdleAnimationProcessor - so that entity switches to idle when not attacking
        -   after NewPerformMovementAnimationProcessor - so that entity switches to walking when not attacking
        -   before NewPerformFrameUpdateProcessor - so that attack is animated
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        ('new.command_system.new_perform_command_processor', 'NewPerformCommandProcessor'), 
        ('new.animation_system.new_perform_movement_animation_processor', 'NewPerformMovementAnimationProcessor')
        ]

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def process(self, *args, **kwargs):
        ''' Get all components with renderable model that have attacked and have some weapon in use 
        and update their action.
        '''
        self.cycle += 1

        # Iterate all cameras
        for _, (camera) in self.world.get_component(components.Camera):

            # Get all entities that are in the process of attacking
            for ent, (_, renderable_model, _, weapon_in_use) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(components.Position, components.RenderableModel, components.NewFlagDoAttack, components.NewWeaponInUse)):

                # Update to proper animation
                renderable_model.set_action(weapon_in_use.action)
                logger.debug(f'({self.cycle}) - Entity {ent} action animation updated to "{weapon_in_use.action}" action.')


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