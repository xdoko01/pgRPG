import pygame
from pyrpg.core.config import MESSAGES # for DEFAULT_TTL_MS

class Message:
    ''' Class representing game message displayed to the players
    '''

    __slots__ = ['text', 'pos', 'created', 'ttl']

    def __init__(self, text, ttl=None, pos=None):
        ''' Initiate values for the Message component.

        Parameters:
            :param text: Text of the message
            :type text: str

            :param ttl: How long the message should be displayed on the screen (default 2s)
            :type ttl: integer

            :param pos: Position where to display the message (default None)
            :type pos: tuple
        '''

        self.text = text
        self.ttl = ttl if ttl else MESSAGES["DEFAULT_TTL_MS"]
        self.pos = pos
        self.created = pygame.time.get_ticks()

""" not needed anymore - rendering realized by new PerformRenderMessagesProcessor
def process(window, msg_list):
    ''' Do whatever needed with the message - store it into the file,
    display it on the screen ...
    '''

    pos = [0, 0]

    for msg in msg_list:

        # Generate surface for blitting
        msg_surf = GAME_MSG_FONT.render(msg.text, align='LEFT')

        # Blit the surface
        window.blit(msg_surf, (pos[0], pos[1]))

        # Move the offset
        pos[1] += msg_surf.get_height()
"""