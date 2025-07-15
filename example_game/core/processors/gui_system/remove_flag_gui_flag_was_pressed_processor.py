__all__ = ['RemoveFlagGUIFLagWasPressedProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs import Processor, SkipProcessorExecution

# Used components
from core.components.gui_flag_was_pressed import GUIFlagWasPressed

# Logger init
logger = logging.getLogger(__name__)

class RemoveFlagGUIFLagWasPressedProcessor(Processor):
    ''' Removes FlagHasDamaged flag after the cycle.

    Involved components:
        -   GUIFlagWasPressed

    Related processors:
        -   PerformGUIPress

    What if this processor is disabled?

    Where the processor should be planned?
        -   after PerformGUIPress
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
    ]

    def __init__(self, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)


    def process(self, *args, **kwargs):
        ''' Removes the FlagHasDamaged flag.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (_) in self.world.get_components(GUIFlagWasPressed):

            self.world.remove_component(ent, GUIFlagWasPressed)
            logger.debug(f'({self.cycle}) - Entity {ent} - flag "GUIFlagWasPressed" was removed.')

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to
        non-serializable components
        '''
        pass

    def post_load(self, window):
        ''' Reconfigure the processor after de-serialization by attaching
        the lost reference again
        '''
        pass

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass
