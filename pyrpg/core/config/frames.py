from pyrpg.core.config.filepaths import FRAME_PATH # for frame path
from pyrpg.core.config import FRAMES, show

import pyrpg.utils as utils # for BitmapFrame class
import pygame # for pygame.Color

FRAMES["PLAYER_TALK_FRAME"] = utils.BitmapFrame(FRAME_PATH/ FRAMES["PLAYER_TALK_FRAME"], color=pygame.Color('blue'))
FRAMES["GAME_DEBUG_FRAME"] = utils.BitmapFrame(FRAME_PATH/ FRAMES["GAME_DEBUG_FRAME"], color=pygame.Color('blue'))

show(FRAMES)