__all__ = ['RemoveFlagIsAnimationActionFrameProcessor']

import logging

# Parent super-class
from pgrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.flag_is_animation_action_frame import FlagIsAnimationActionFrame

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagIsAnimationActionFrameProcessor(Processor):
    ''' Removes the flag that fighter has fired a projectile.

    Involved components:
        -   FlagIsAnimationActionFrame

    Related processors:
        -   PerformFrameUpdateProcessor

    What if this processor is disabled?
        -   projectiles are constantly generated

    Where the processor should be planned?
        -   after PerformFrameUpdateProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        #'allOf', 'animation_system.perform_frame_update_processor:PerformFrameUpdateProcessor'
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        ''' Removes the flag that the projectile needs to be generated.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_) in self.world.get_components(FlagIsAnimationActionFrame):

            self.world.remove_component(ent, FlagIsAnimationActionFrame)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "FlagIsAnimationActionFrame" was removed.')

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

