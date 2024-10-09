__all__ = ['PerformRenderMessagesProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

from pyrpg.core.config.fonts import FONTS # for GAME_MSG_FONT 

# Logger init
logger = logging.getLogger(__name__)

import pygame

class PerformRenderMessagesProcessor(Processor):
    ''' For rendering messages on game window surface.

    Input parameters:
        -   window

    Involved components:
        -   NA

    Related processors:
        -   NA

    What if this processor is disabled?
        -   no messages are displayed

    Where the processor should be planned?
        -   before PerformRenderDebugInfoProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    __slots__ = ['window', 'game_messages', 'pos', 'align']

    def __init__(self, window, game_messages, *args, pos=[0, 0], align='LEFT', **kwargs):
        ''' Initiation of PerformRenderMessagesProcessor processor.

        Parameters:

            :param window: Reference to game window
            :type window: reference

            :param game_messages: Reference to function that returns list of msgs
            :type game_messages: reference

            :param pos: Top-left corner for messages to display on the game window
            :type pos: list

            :param align: Message text alignment - LEFT, RIGHT, CENTER
            :type align: str
        '''
        super().__init__(*args, **kwargs)

        self.window = window
        self.game_messages_fnc = game_messages
        self.pos = pos
        self.align = align

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        '''Display game messages on game window'''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # Get list of game messages to display
        messages = self.game_messages_fnc()

        # Start rendering on the desired position
        pos = self.pos.copy()

        # Blit the messages on window
        for msg in messages:

            # Generate surface for blitting
            msg_surf = FONTS["GAME_MSG_FONT"].render(msg.text, align=self.align)

            # Blit the surface
            self.window.blit(msg_surf, (pos[0], pos[1]))

            # Move the offset for the next message to display
            pos[1] += msg_surf.get_height()

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components (window)
        '''
        self.window = None

    def post_load(self, window):
        ''' Reconfigure the processor after de-serialization by attaching
        the reference to maps again
        '''
        self.window = window

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass
