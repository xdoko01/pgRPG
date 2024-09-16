from pyrpg.core.config.filepaths import FILEPATHS # for font path
from pyrpg.core.config import FONTS, show # for fonts modification

import pyrpg.utils as utils# for BitmapFont class
import pygame # for pygame.Color

# Font for in-game dialog bubbles
FONTS["GAME_DEBUG_FONT"] = utils.BitmapFont(FILEPATHS["FONT_PATH"] / FONTS["GAME_DEBUG_FONT"], color=pygame.Color('#000001'))
FONTS["PLAYER_TALK_FONT"] = utils.BitmapFont(FILEPATHS["FONT_PATH"] / FONTS["PLAYER_TALK_FONT"])

# Font for in-game messages such as 'item picked'
FONTS["GAME_MSG_FONT"]= utils.BitmapFont(FILEPATHS["FONT_PATH"] / FONTS["GAME_MSG_FONT"])

show(FONTS)