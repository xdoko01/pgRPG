import core.config.paths as paths # for font path
import utils # for BitmapFont class
import pygame # for pygame.Color

# Font for in-game dialog bubbles
GAME_DEBUG_FONT = utils.BitmapFont(paths.FONT_PATH / 'small_font.json', color=pygame.Color('#EFEFEF'))
PLAYER_TALK_FONT = utils.BitmapFont(paths.FONT_PATH / 'good_neighbours_font.json')

# Font for in-game messages such as 'item picked'
GAME_MSG_FONT = utils.BitmapFont(paths.FONT_PATH / 'good_neighbours_font.json')