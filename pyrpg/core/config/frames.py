import pyrpg.core.config.paths as paths # for font path
import pyrpg.utils as utils # for BitmapFrame class
import pygame # for pygame.Color

PLAYER_TALK_FRAME = utils.BitmapFrame(paths.FRAME_PATH / 'small_frame.json', color=pygame.Color('blue'))
GAME_DEBUG_FRAME = utils.BitmapFrame(paths.FRAME_PATH / 'debug_frame.json', color=pygame.Color('blue'))