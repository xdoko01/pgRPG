''' Module for handling dialogs with button

    -------------------------
    TODOs & Things to improve
    -------------------------
    - implement background color and transparency for the dialog
    - use the target reference to get the window dimensions and adequately adjust the dimensions of the dialog
      - dimensions can be [1, 0.5] ... full target width, half target height
    - position can be defined relatively
      - position [CENTER, CENTER], [CENTER, LEFT] etc.
    - padding should be possible to define
    - display_dlg function will handle key presses and ttls to display the whole dialog workflow
    - idealy display_dlg should be able to return some value that is specified in json - and based on returned
      value to generate event or direct the flow of the brain algorithm.
    - Add shadow to the window
    - New templates for SUBMIT/OK dialog, YES/NO dialog, NEXT dialog
    - implement grids for alignment
	- dialog
	 - grid>>alignment top (on top of the dialo)
	 	- grid>>alinment right
     - BACKGROUND as CLASS
       - self.surface - fill
       - selfimage as DlgImage can be none passing {}
       - dimension must be on input
'''

import json
import re # For removing C-style comments from JSON file

import pygame
import pprint as pp
from collections import namedtuple
from bitmap_font import BitmapFont

########################################################
### Module support functions
########################################################

def _intersect(surf_pos, surf_dim, parent_dim):
    ''' Return square that will be cut from surf and 
    used for displaying.
    '''

    surf_pos_x, surf_pos_y = surf_pos
    surf_dim_x, surf_dim_y = surf_dim
    par_dim_x, par_dim_y = parent_dim

    # x,y is left right corner in the surface area
    # dx, dy is the width and length in the surface area
    x = y = dx = dy = 0

    # First check that the area is totaly out for displaying
    if surf_pos_x + surf_dim_x <= 0: return (0, 0, 0, 0)
    if surf_pos_y + surf_dim_y <= 0: return (0, 0, 0, 0)

    if surf_pos_x > par_dim_x: return (0, 0, 0, 0)
    if surf_pos_y > par_dim_y: return (0, 0, 0, 0)

    # Now we know that the surf is partially visible (otherwise fction will return above)
    if surf_pos_x < 0: x = -surf_pos_x
    if surf_pos_y < 0: y = -surf_pos_y

    if surf_pos_x >= 0: x = 0
    if surf_pos_y >= 0: y = 0

    # Now calc the new dimensions of the surface
    if surf_pos_x + surf_dim_x > 0: dx = min(surf_pos_x + surf_dim_x, surf_dim_x)
    if surf_pos_y + surf_dim_y > 0: dy = min(surf_pos_y + surf_dim_y, surf_dim_y)

    if surf_pos_x + surf_dim_x > par_dim_x: dx = surf_dim_x - (surf_pos_x + surf_dim_x - par_dim_x)
    if surf_pos_y + surf_dim_y > par_dim_y: dy = surf_dim_y - (surf_pos_y + surf_dim_y - par_dim_y)

    return (x, y, dx, dy)

########################################################
### Module support classes (namedtuples)
########################################################

# Define position as a namedtuple
Pos = namedtuple('Pos', ['x', 'y'])

# Define tuple (surface, position) as a namedtuple
DlgSurf = namedtuple('DlgSurf', ['surf', 'pos'])

########################################################
### Private classes representing dialog elements
########################################################

class _DlgFont:

    __slots__ = ['_parent', '_font_obj', 'font_path', 'font_file', 'color', 'size']

    def __init__(self, parent, data_dict):
        '''
            "font" : {
                "font_path" : "some/path",      ... optional, if not present parent path is used
                "font_file" : "small_font.json",     ... mandatory
                "color" : "#FF0000",            ... optional
                "size" : 16,                    ... optional
            }
        '''

        self._parent = parent

        # Get font_path from the parent if not present
        self.font_path = data_dict.get('font_path', self._parent.get_font().font_path if self._parent is not None else '')

        # Translate to Path instance if necessary
        if not isinstance(self.font_path, Path): self.font_path = Path(self.font_path)

        # Get font file from the parent if not present
        self.font_file = data_dict.get('font_file', self._parent.get_font().font_file if self._parent is not None else '')

        # Get the color from parent, if there is no color
        self.color = data_dict.get('color', self._parent.get_font().color if self._parent is not None else None)
        if not isinstance(self.color, pygame.Color): self.color = pygame.Color(self.color)

        # Get size from the parent if there is no size
        self.size = data_dict.get('size', self._parent.get_font().size  if self._parent is not None else '')

        print(f'font_path:{self.font_path}, font_file:{self.font_file}, color:{self.color}, size:{self.size}')

        # Create a new font object based on the parameters above
        self._font_obj = BitmapFont(self.font_path / self.font_file, size=self.size, color=self.color)

    def render(self, text, align):
        ''' Returns rendered surface
        '''
        return self._font_obj.render(text, color=self.color, align=align)


class _DlgText:

    __slots__ = ['_parent', '_surf', 'text', 'font', 'align', 'dimensions', 'position']

    def __init__(self, parent, data_dict):
        '''
            {
                "font" : {                                      ... optional
                    "path" : "small_font.json",
                    "color" : "#FF0000",
                },

                "align" : "LEFT"                                ... optional
                "text" : "This is dialog level text no 1",      ... mandatory
                "position" : [0, 0]
            }
        '''

        self._parent = parent

        # Get font class instance of DlgFont either from definition or from parent
        # Text is created by dialog, frame or button - those can have definition of font
        self.font = _DlgFont(self._parent, data_dict.get('font')) if data_dict.get('font', None) else self._parent.get_font()

        # Get text (mandatory)
        self.text = data_dict.get('text')

        # Get alignment (optional)
        self.align = data_dict.get('align', None)

        # Render and store surface with the text
        self._surf = self.font.render(self.text, self.align)

        # Store the text dimensions
        self.dimensions = self._surf.get_size()

        # Store position which is relative to the parent position
        self.position = data_dict.get('position', [0, 0])
        self.position = Pos(x=self.position[0], y=self.position[1])

    def get_font(self):
        ''' Returns the DlgFont instance used to generate this text
        '''
        return self.font

    def display(self, target, parent_position):
        ''' Blit text on defined target and position
        Do not allow to display text out of the window
        '''
        # Crop the text surface so that it is displayable and blit it
        target.blit(
            self._surf,
            (max(0, self.position.x) + parent_position[0], max(0, self.position.y) + parent_position[1]),
            _intersect(self.position, self.dimensions, self._parent.dimensions)
            #(0, 0, min(self._parent.dimensions[0] - self.position.x, self.dimensions[0]), min(self._parent.dimensions[1] - self.position.y, self.dimensions[1]))
            )


class _DlgImage:

    __slots__ = ['_parent', '_surf', 'label', 'img_path', 'dimensions', 'position']

    def __init__(self, parent, data_dict):
        '''
            {
                "img_path" : "some/path"       ... optional, if not stated, parent path is used
                "file" : "quake.png",           ... mandatory
                "label" : "This is example",    ... optional, if not stated, it is set to None
                "alpha" : 128,                  ... optional, by default not transparent
                
                "dimensions" : [100, 100],      ... optional, if not stated, original image size is used

                "position" : [50, 50]           ... mandatory
            }
        '''


        # Remember the parent dlg element
        self._parent = parent

        self.label = data_dict.get('label', None)

        # Empty image implementation
        if not data_dict:
            self.img_path = ''
            self._surf = pygame.Surface((0, 0))
            self.dimensions = [0, 0]
            self.position = Pos(x=0, y=0)
        else:

            # If path is not specified, ask parent for the image path
            self.img_path = Path(data_dict.get('img_path', self._parent.get_img_path())) / data_dict.get('file')

            # Create and store surface and alpha
            self._surf = pygame.image.load(str(self.img_path)).convert()
            self._surf.set_alpha(data_dict.get('alpha', 255))

            # Resize image if dimensions are provided, else just remember current img dimensions
            if data_dict.get('dimensions', None):
                self.dimensions = data_dict.get('dimensions')
                self._surf = pygame.transform.scale(self._surf, self.dimensions)
            else:
                self.dimensions = list(self._surf.get_size())

            # Store position which is relative to the parent position
            self.position = data_dict.get('position', [0, 0])
            self.position = Pos(x=self.position[0], y=self.position[1])

    def display(self, target, parent_position):
        ''' Blit image on defined target and position
        DO not alow to blit it out of the parents dimensions
        '''

        #temp_surf = pygame.Surface((min(self._parent.dimensions[0] - self.position.x, self.dimensions[0]), min(self._parent.dimensions[1] - self.position.y, self.dimensions[1])))
        #temp_surf.set_alpha(self.alpha)
        #temp_surf.blit(self._surf, (0, 0))
        #target.blit(temp_surf, (self.position.x + parent_position[0], self.position.y + parent_position[1]))

        # Original - not cutting images
        target.blit(
            self._surf,
            (max(0, self.position.x) + parent_position[0], max(0, self.position.y) + parent_position[1]),
            _intersect(self.position, self.dimensions, self._parent.dimensions)
            )


class _DlgFrame:

    def __init__(self, parent, data_dict):
        '''
            {
                "font" : {
                    "path" : "small_font.json",
                    "size" : 8,
                    "color" : "#00FFFF",
                    "align" : "RIGHT"
                },

                "background" : {
                    "color" : "#FF0000",
                    "alpha" : 128
                },

                "images" : [
                    {
                        "path" : "quake.png",
                        "position" : [50, 50]
                    },
                    {
                        "path" : "bluesquare.png",
                        "position" : [100, 50]
                    }
                ],

                "texts" : [
                    {
                        "text" : "Once upon\nthe time",
                        "position" : [0, 100]
                    }
                ]
            }
        '''

        self._parent = parent

        self.dimensions = data_dict.get('dimensions', self._parent.dimensions)

        self.font = _DlgFont(self._parent, data_dict.get('font')) if data_dict.get('font', None) else self._parent.get_font()
        self.images = [_DlgImage(self, image_data) for image_data in data_dict.get('images', [])]
        self.texts = [_DlgText(self, text_data) for text_data in data_dict.get('texts', [])]

    def get_font(self):
        ''' Returns the DlgFont instance used for this DlgFrame instance
        '''
        return self.font
    
    def get_img_path(self):
        return self._parent.get_img_path()

    def display(self, target, parent_position):
        ''' Blit frame on defined target and position
        '''

        # Blit images
        for image in self.images: image.display(target, parent_position)

        # Blit texts
        for text in self.texts: text.display(target, parent_position)

class _DlgBackground:
    '''
     - BACKGROUND as CLASS
       - self.surface - fill
       - selfimage as DlgImage can be none passing {}
       - dimension must be on input
    '''

    def __init__(self, data_dict, dimensions):
        '''
          - dimensions
          - surface
          - image
        '''

    def display(self, target, parent_position):
        '''
            blit surface
            blit image
        '''


class DlgWindow:
    '''
        {
        "id" : "dlg_example",

        "templates" : ["basic_dlg"],

        "dimensions" : [400, 200],

        "background" : {
            "color" : "#FFFFFF",
            "image" : "quake.png",
            "alpha" : 128
        },

        "font" : {
            "path" : "small_font.json",
            "size" : 16,
            "color" : "#FFFFFF",
            "align" : "CENTER"
            },

        "texts" : [
            {
                "font" : {
                    "path" : "small_font.json",
                    "color" : "#FF0000",
                    "align" : "LEFT"
                },
                "text" : "This is dialog level text no 1",
                "position" : [0, 0]
            },
            {
                "text" : "This is dialog\nlevel text no 2",
                "position" : [0, 20]
            },
            {
                "text" : "This is dialog\nlevel text no 3",
                "position" : [50, 100],
                "font" : {
                    "path" : "good_neighbours_font.json"
                }
            }
        ]
        }
    '''

    def __init__(self, data_dict, img_path=None, font_path=None):

        self.id = data_dict.get('id')

        # Mandatory for DlgWindow
        self.dimensions = data_dict.get('dimensions')

        # Paths
        self.img_path = img_path

        # Font - create at least instance with font path - in order to propage font path to
        # every font instance in the downline
        font_data = { **data_dict.get('font', {}), **{ 'font_path' : font_path } }
        self.font = _DlgFont(None, font_data)

        # Prepare background color surface
        bcgrnd_color = data_dict.get('background', {}).get('color', None)
        if bcgrnd_color:
            self.bcgrnd_surf = pygame.Surface(self.dimensions)
            self.bcgrnd_surf.fill(pygame.Color(bcgrnd_color))
            self.bcgrnd_surf.set_alpha(data_dict.get('background', {}).get('alpha', 255))
        else:
            self.bcgrnd_surf = pygame.Surface((0, 0))

        # Prepare background image that is resized as the DlgWindow
        bcgrnd_img = data_dict.get('background', {}).get('image', {})
        if bcgrnd_img: 
            bcgrnd_img.update( {"dimensions" : self.dimensions})

        self.bcgrnd_img = _DlgImage(self, bcgrnd_img)

        self.images = [_DlgImage(self, image_data) for image_data in data_dict.get('images', [])]
        self.texts = [_DlgText(self, text_data) for text_data in data_dict.get('texts', [])]
        self.frames = [_DlgFrame(self, frame_data) for frame_data in data_dict.get('frames', [])]

    def get_font(self):
        ''' Returns the DlgFont instance used for this DlgFrame instance
        '''
        return self.font

    def get_img_path(self):
        return self.img_path

    def display(self, target, position, frame_id=None):
        ''' Blit frame on defined target and position
            DO not allow to show anything out of the dialog window
        '''

        # Blit background color
        target.blit(self.bcgrnd_surf, position)

        # Blit background image
        self.bcgrnd_img.display(target, position)

        # Blit images on temp surface
        for image in self.images: image.display(target, position)

        # Blit texts
        for text in self.texts: text.display(target, position)

        # Blit frame if frame_id defined
        try:
            if frame_id is not None:
                self.frames[frame_id].display(target, position)
        except IndexError:
            raise ValueError(f'Frame no. {frame_id} is not defined for dialog "{self.id}".')

########################################################
### Module DEMO
########################################################

if __name__ == "__main__":

    from pprint import pprint
    from pathlib import Path

    ##############
    # INIT PYGAME
    ##############

    # Init pygame
    pygame.init()

    # Prepare the main window
    window = pygame.display.set_mode([850, 850], 0, 32)
    window.fill((50, 50, 0))

    ##############
    # PREPARE DIALOG
    ##############

    # Read the dialog data from JSON
    try:
        with open('pyrpg/utils/dlg_example_oop.json', 'r') as dlg_file:
            json_dlg_data = dlg_file.read()
            dlg_data = json.loads(re.sub("//.*", "", json_dlg_data, flags=re.MULTILINE))
    except FileNotFoundError:
        print(f"Dialog file '{file}' not found.")
        raise	

    pprint(dlg_data)

    # Create DlgWindow from the dictionary
    dlg_obj = DlgWindow(dlg_data, img_path=Path('pyrpg/resources/images'), font_path=Path('pyrpg/resources/fonts'))

    pprint(dlg_obj)

    ##############
    # DISPLAY DIALOG
    ##############

    dlg_obj.display(target=window, position=(50, 50), frame_id=None)
    #dlg_obj.display(target=window, position=(320, 10), frame_id=0)
    #dlg_obj.display(target=window, position=(10, 320), frame_id=1)
    #dlg_obj.display(target=window, position=(320, 320), frame_id=2)

    # Show the result
    pygame.display.update()

    # Quit - wait for closing of the window
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            pygame.quit()
