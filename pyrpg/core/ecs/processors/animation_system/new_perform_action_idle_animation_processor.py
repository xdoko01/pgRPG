__all__ = ['NewPerformActionIdleAnimationProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

from ..functions import filter_only_visible


# Logger init
logger = logging.getLogger(__name__)


class NewPerformActionIdleAnimationProcessor(esper.Processor):
    ''' Sets action idle animation for RenderableModel entities that are armed,
    idled, and displayed.

    Involved components:
        -   RenderableModel
        -   NewWeaponInUse

    Related processors:
        -   NewPerformIdleAnimationProcessor
        -   NewPerformActionAnimationProcessor
        -   NewPerformMovementAnimationProcessor
        -   NewPerformFrameUpdateProcessor

    What if this processor is disabled?
        -   entities are not animated while being idle wearing weapon

    Where the processor should be planned?
        -   see README.md
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['NewPerformCommandProcessor']

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def process(self, *args, **kwargs):
        ''' Get all components with renderable model that have weapon armed and at
        the same time did not move nor attack.
        '''
        self.cycle += 1

        # Iterate all cameras
        for _, (camera) in self.world.get_component(components.Camera):

            # Get all entities with Position, RenderableModel + are armed and did not move nor attack
            for ent, (_, renderable_model, weapon_in_use) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components_exs(include=(components.Position, components.RenderableModel, components.NewWeaponInUse), exclude=(components.NewFlagDoAttack, components.NewFlagDoMove))):

                # Update to proper animation
                renderable_model.set_action(weapon_in_use.idle_action)
                logger.debug(f'({self.cycle}) - Entity {ent} idle action animation updated to "{weapon_in_use.idle_action}" action.')


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