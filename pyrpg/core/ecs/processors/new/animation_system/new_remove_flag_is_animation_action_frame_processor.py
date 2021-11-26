__all__ = ['NewRemoveFlagIsAnimationActionFrameProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.new_flag_is_animation_action_frame import NewFlagIsAnimationActionFrame

# Logger init
logger = logging.getLogger(__name__)

class NewRemoveFlagIsAnimationActionFrameProcessor(Processor):
    ''' Removes the flag that fighter has fired a projectile.

    Involved components:
        -   NewFlagIsAnimationActionFrame

    Related processors:
        -   NewPerformFrameUpdateProcessor

    What if this processor is disabled?
        -   projectiles are constantly generated

    Where the processor should be planned?
        -   after NewPerformFrameUpdateProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.animation_system.new_perform_frame_update_processor:NewPerformFrameUpdateProcessor'
    ]

    def __init__(self):
        ''' Init the processor.
        '''
        super().__init__()

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Removes the flag that the projectile needs to be generated.
        '''
        self.cycle += 1

        for ent, (_) in self.world.get_components(NewFlagIsAnimationActionFrame):

            self.world.remove_component(ent, NewFlagIsAnimationActionFrame)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "NewFlagIsAnimationActionFrame" was removed.')

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

