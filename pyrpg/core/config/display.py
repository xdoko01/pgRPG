from .config import DISPLAY

DISPLAY_RESOLUTION = DISPLAY.get('resolution')
DISPLAY_WIDTH = DISPLAY_RESOLUTION[0]
DISPLAY_HEIGHT = DISPLAY_RESOLUTION[1]
DISPLAY_BITDEPTH = DISPLAY.get('bitdepth')
DISPLAY_MAX_FPS =  DISPLAY.get('max_fps')
DISPLAY_SHOW_FPS = DISPLAY.get('show_fps')
DISPLAY_FULLSCREEN = bool(DISPLAY.get('fullscreen'))

DISPLAY_GUI_WINDOW_RATIO = 1.5 # Ratio of the gui window inside the main window

