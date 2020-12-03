''' Module for handling dialogs with button

    -------------------------
    TODOs & Things to improve
    -------------------------
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
'''

import json
import pygame
import pprint as pp
from collections import namedtuple
from bitmap_font import BitmapFont

########################################################
### Module support classes (namedtuples)
########################################################

# Define position as a namedtuple
Pos = namedtuple('Pos', ['x', 'y'])

# Define tuple (surface, position) as a namedtuple
DlgSurf = namedtuple('DlgSurf', ['surf', 'pos'])


############################################################################################################################################################################
########################################################
### Module private functions for surface preparation
########################################################

def _get_dlg_bckgrnd(dlg_data, img_path=None):
    ''' Get the background surface of the dialog in a form of
    pygame.Surface. This is further used in prepare_dlg_obj_from_data
    to fill dialog object.

    Parameters:

        :param dlg_data: Data in a form of python dictionary
        :type dlg_data: dict

        :param img_path: Path where the images for dialog generation are found
        :type img_path: Path

        :return: DlgSurf containing SUrface with the dialog background and position [0,0]
        :rtype: DlgSurf
    '''

    dlg_bckgrnd_data = dlg_data.get('background', {})

    # Prepare the frame for displaying

    # If there are some background data available process them.    
    if dlg_bckgrnd_data:

        # If image is defined use image otherwise use color
        if dlg_bckgrnd_data.get('image', None):
            # Get full image path
            img_path = str(img_path) + '/' if img_path is not None else ''

            dlg_bckgrnd_surf = pygame.image.load(img_path + dlg_bckgrnd_data.get('image')).convert() 
            dlg_bckgrnd_surf = pygame.transform.scale(dlg_bckgrnd_surf, dlg_data.get('dimensions'))

        else:
            dlg_bckgrnd_surf = pygame.Surface(dlg_data.get('dimensions'))
            dlg_bckgrnd_surf.fill(pygame.Color(dlg_bckgrnd_data.get('color', '#FFFFFF')))

        dlg_bckgrnd_surf.set_alpha(dlg_bckgrnd_data.get('alpha', 255))

        return DlgSurf(surf=dlg_bckgrnd_surf, pos=Pos(x=0, y=0))

    # Otherwise return empty surface (no background)
    else:

        return DlgSurf(surf=pygame.Surface((0,0)), pos=Pos(x=0, y=0))

def _get_dlg_images(dlg_data, img_path=None):
    ''' Get the images to be displayed on top of the dialog background.

    Parameters:

        :param dlg_data: Data in a form of python dictionary
        :type dlg_data: dict

        :param img_path: Path where the images for dialog generation are found
        :type img_path: Path

        :return: List of DlgSurf(Surface, position) containing images and positions to show.
        :rtype: list
    '''

    # Empty list of images and positions to start with
    dlg_images_obj = []

    # Generate dialog images and store them in the list with the positions
    for image_data in dlg_data.get('images', []):
        path = image_data.get('path', '')
        position = image_data.get('position', [0, 0])

        # Get full image path
        path = str(img_path) + '/' + str(path) if img_path is not None else path

        # Prepare image object
        dlg_image_surf = pygame.image.load(path).convert() 

        # Render and store the image surface as DlgSurf
        dlg_images_obj.append(DlgSurf(surf=dlg_image_surf, pos=Pos(position[0], position[1])))

    # Return the list of images
    return dlg_images_obj

def _get_dlg_texts(dlg_data, font_path=None):
    ''' Get the texts to be displayed on top of the dialog background and images.

    Parameters:

        :param dlg_data: Data in a form of python dictionary
        :type dlg_data: dict

        :param font_path: Path where the path for dialog generation is found
        :type font_path: Path

        :return: List of DlgSurf(Surface, position) containing text images and positions to show.
        :rtype: list
    '''

    # Empty list of text and positions to start with
    dlg_texts_obj = []

    # Generate dialog texts and store them in the list with the positions
    for text_data in dlg_data.get('texts', []):
        text = text_data.get('text', '')
        font = text_data.get('font', {}).get('path', dlg_data.get('font', {}).get('path'))
        size = text_data.get('font', {}).get('size', dlg_data.get('font', {}).get('size', None))
        color = text_data.get('font', {}).get('color', dlg_data.get('font', {}).get('color', None))
        color = pygame.Color(color) if color else None
        align = text_data.get('font', {}).get('align', dlg_data.get('font', {}).get('align', None))
        position = text_data.get('position', [0, 0])

        # Get the font path
        font = font_path / font if font_path is not None else font

        # Prepare font object
        text_font = BitmapFont(font, size=size, color=color)

        # Render and store the text surface as DlgSurf
        dlg_texts_obj.append(DlgSurf(surf=text_font.render(text, color=color, align=align), pos=Pos(position[0], position[1])))

    # Return the list of texts
    return dlg_texts_obj

def _get_dlg_frame_bckgrnd(dlg_data, frame_id, img_path=None):
    ''' Get the background surface of the given frame in a form of
    Surface and position. This is further used in prepare_dlg_obj_from_data to
    correctly display the frame background with alpha channel.

    Parameters:

        :param dlg_data: Data in a form of python dictionary
        :type dlg_data: dict

        :param frame_id: Number of the frame
        :type frame_id: int

        :param img_path: Path where the images for dialog generation are found
        :type img_path: Path

        :return: DlgSurf containing Surface with the dialog background and position [0,0]
        :rtype: DlgSurf
    '''

    # Get frame data
    frame_data = dlg_data.get('frames')[frame_id]

    # Get frame background data
    dlg_frame_bckgrnd_data = frame_data.get('background', {})

    # If there are some background data available process them.    
    if frame_data.get('background', {}):

        # If image is defined use image otherwise use color
        if dlg_frame_bckgrnd_data.get('image', None):
            # Get full image path
            img_path = str(img_path) + '/' if img_path is not None else ''

            dlg_frame_bckgrnd_surf = pygame.image.load(img_path + dlg_frame_bckgrnd_data.get('image')).convert()
            dlg_frame_bckgrnd_surf = pygame.transform.scale(dlg_frame_bckgrnd_surf, dlg_data.get('dimensions'))

        else:

            dlg_frame_bckgrnd_surf = pygame.Surface(dlg_data.get('dimensions'))
            dlg_frame_bckgrnd_surf.fill(pygame.Color(dlg_frame_bckgrnd_data.get('color', '#FFFFFF')))

        dlg_frame_bckgrnd_surf.set_alpha(dlg_frame_bckgrnd_data.get('alpha', 255))

        return DlgSurf(surf=dlg_frame_bckgrnd_surf, pos=Pos(x=0, y=0))

    # Otherwise return empty surface (no background)
    else:

        return DlgSurf(surf=pygame.Surface((0,0)), pos=Pos(x=0, y=0))

def _get_dlg_frame_images(dlg_data, frame_id, img_path=None):
    ''' Get the images to be displayed on top of the dialog frame background.

    Parameters:

        :param dlg_data: Data in a form of python dictionary
        :type dlg_data: dict

        :param frame: Number of the frame
        :type dlg_data: int

        :param img_path: Path where the images for dialog generation are found
        :type img_path: Path

        :return: List of DlgSurf(Surface, position) containing images and positions to show.
        :rtype: list
    '''

    # Get frame data
    frame_data = dlg_data.get('frames')[frame_id]

    # Empty list of images and positions to start with
    dlg_frame_images_obj = []

    # Generate dialog images and store them in the list with the positions
    for image_data in frame_data.get('images', []):
        path = image_data.get('path', '')
        position = image_data.get('position', [0, 0])

        # Get full image path
        path = str(img_path) + '/' + str(path) if img_path is not None else path

        # Prepare image object
        dlg_frame_image_surf = pygame.image.load(path).convert()

        # Render and store the image surface as DlgSurf
        dlg_frame_images_obj.append(DlgSurf(surf=dlg_frame_image_surf, pos=Pos(position[0], position[1])))

    # Return the list of images
    return dlg_frame_images_obj

def _get_dlg_frame_texts(dlg_data, frame_id, font_path=None):
    ''' Get the texts to be displayed on top of the dialog frame background and images.

    Parameters:

        :param dlg_data: Data in a form of python dictionary
        :type dlg_data: dict

        :param frame: Number of the frame
        :type dlg_data: int

        :param font_path: Path where the path for dialog generation is found
        :type font_path: Path

        :return: List of DlgSurf(Surface, position) containing text surfaces and positions to show.
        :rtype: list
    '''

    # Prepare empty list for storing surfaces and positions
    dlg_frame_texts_obj = []

    # Get frame data
    frame_data = dlg_data.get('frames')[frame_id]

    # Join list of dialog texts and frame texts
    for text_data in frame_data.get('texts',[]):
        text = text_data.get('text', '')
        font = text_data.get('font', {}).get('path', frame_data.get('font', {}).get('path', dlg_data.get('font', {}).get('path')))
        size = text_data.get('font', {}).get('size', frame_data.get('font', {}).get('size', dlg_data.get('font', {}).get('size', None)))
        color = text_data.get('font', {}).get('color', frame_data.get('font', {}).get('color', dlg_data.get('font', {}).get('color', None)))
        color = pygame.Color(color) if color else None
        align = text_data.get('font', {}).get('align', frame_data.get('font', {}).get('align', dlg_data.get('font', {}).get('align', None)))
        position = text_data.get('position', [0, 0])

        # Get the font path
        font = font_path / font if font_path is not None else font

        # Prepare font object
        text_font = BitmapFont(font, size=size, color=color)

        # Render and store the text surface as DlgSurf
        dlg_frame_texts_obj.append(DlgSurf(surf=text_font.render(text, color=color, align=align), pos=Pos(position[0], position[1])))

    # Return the list of texts surfaces
    return dlg_frame_texts_obj


########################################################
### Module classes
########################################################

class DlgWindowFrame:
    ''' Class implementing frame shown in the dialog.
    '''

    def __init__(self, dlg_data, frame_id, img_path=None, font_path=None):
        ''' Create object representing dialog window frame. One dialog
        can have one to many frames that can be switched between
        (e.g. wizard).

        Parameters:

            :param dlg_ref: Reference to the parent dialog object
            :type dlg_ref: ref

            :param frame_id: Data in a form of python dictionary
            :type frame_id: dict

            :param img_path: Path where the images for dialog generation are found
            :type img_path: Path

            :param font_path: Path where font definitions are found
            :type font_path: Path
        '''

        # Store dialog frame background if defined
        self.background = _get_dlg_frame_bckgrnd(dlg_data, frame_id=frame_id, img_path=img_path)

        # Store dialog frame images
        self.images = _get_dlg_frame_images(dlg_data, frame_id=frame_id, img_path=img_path)

        # Store dialog frame texts
        self.texts = _get_dlg_frame_texts(dlg_data, frame_id=frame_id, font_path=font_path)

    def __str__(self):
        ''' Print nicely DlgWindowFrame on the output
        '''
        return pp.pformat(self)

    def display(self, target, position):
        ''' Blit prepared dialog frame object onto the target surface.

        Parameters:

            :param target: Target surface on which the dialog frame is displayed
            :type target: Surface

            :param position: Position of the top-left corner of the dialog frame on the target.
            :type position: tuple or list

            :param frame_id: Frame number
            :type frame_id: integer
        '''

        # Blit dialog frame background
        target.blit(self.background.surf, position)

        # Blit dialog frame images
        for image in self.images:
            target.blit(image.surf, (position[0] + image.pos.x, position[1] + image.pos.y))

        # Blit dialog frame texts
        for text in self.texts:
            target.blit(text.surf, (position[0] + text.pos.x, position[1] + text.pos.y))


class DlgWindow:
    ''' Class implementing in-game dialog window with buttons
    '''

    def __init__(self, dlg_data, img_path=None, font_path=None):
        ''' Create object representing the dialog window from the 
        definition in dict form. Details about the structure of 
        dlg_data can be found in resources/dialogs/_DialogJSONStructure.md.

        Parameters:

            :param dlg_data: Data in a form of python dictionary
            :type dlg_data: dict

            :param img_path: Path where the images for dialog generation are found
            :type img_path: Path

            :param font_path: Path where font definitions are found
            :type font_path: Path
        '''
        
        # Store original json format data
        self.data = dlg_data

        # Store the paths
        self.img_path = img_path
        self.font_path = font_path

        # Store dialog dimensions
        self.dimensions = self.data.get('dimensions', [0, 0])

        ##########################################
        # Generate and Store dialog level surfaces
        ##########################################

        # Store dlg background surface
        self.background = _get_dlg_bckgrnd(dlg_data, img_path=img_path)

        # Store dlg images
        self.images = _get_dlg_images(dlg_data, img_path=img_path)
        
        # Store dlg texts
        self.texts = _get_dlg_texts(dlg_data, font_path=font_path)

        ##########################################
        # Generate and Store frame level surfaces
        ##########################################

        # Prepare empty list of frames
        self.frames = [DlgWindowFrame(self.data, frame_id, img_path=img_path, font_path=font_path) for frame_id, frame_data in enumerate(dlg_data.get('frames', []))]


    def __str__(self):
        ''' Print nicely DlgWindow on the output
        '''
        return pp.pformat(self)

    def get_no_of_frames(self):
        ''' Returns number of frames contained in the dialog
        '''
        return len(self.frames)

    def display(self, target, position, frame_id=None):
        ''' Blit prepared dialog object (or particular dialog frame)
        onto the target surface.

        Parameters:

            :param target: Target surface on which the dialog is displayed
            :type target: Surface

            :param position: Position of the top-left corner of the dialog on the target.
            :type position: tuple or list

            :param frame_id: Frame number
            :type frame_id: integer
        '''

        ##########################################
        # Blit dialog level surfaces
        ##########################################

        # Blit dialog background
        target.blit(self.background.surf, position)

        # Blit dialog images
        for image in self.images:
            target.blit(image.surf, (position[0] + image.pos.x, position[1] + image.pos.y))

        # Blit dialog texts
        for text in self.texts:
            target.blit(text.surf, (position[0] + text.pos.x, position[1] + text.pos.y))

        ##########################################
        # Blit frame level surfaces
        ##########################################

        # Blit frame, if specified
        if frame_id is not None:

            try:
                frame_obj = self.frames[frame_id].display(target, position)

            except:
                # In case frame on the position is not defined
                raise ValueError


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
        with open('pyrpg/utils/dlg_example.json', 'r') as dlg_file:
            json_dlg_data = dlg_file.read()
            dlg_data = json.loads(json_dlg_data)
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

    dlg_obj.display(target=window, position=(10, 10), frame_id=None)
    dlg_obj.display(target=window, position=(320, 10), frame_id=0)
    dlg_obj.display(target=window, position=(10, 320), frame_id=1)
    dlg_obj.display(target=window, position=(320, 320), frame_id=2)

    # Show the result
    pygame.display.update()

    # Quit - wait for closing of the window
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            pygame.quit()
