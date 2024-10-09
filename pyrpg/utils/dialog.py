''' Module for handling dialogs

    -------------------------------------------------------
    What is a dialog? Boxed entity with texts and pictures.
    -------------------------------------------------------

     DIALOG has template stored in json file
     DIALOG has position (external parameter)
     DIALOG has dimensions
     DIALOG has BACKGROUND
        BACKGROUND has color
        BACKGROUND has image
        BACKGROUND has transparency
     DIALOG has FONT
        FONT has path
        FONT has size
        FONT has color
        FONT has alignment
     DIALOG has TEXTS
        TEXT has text
        TEXT has FONT
            FONT has path
            FONT has size
            FONT has color
            FONT has alignment
        TEXT has position

     DIALOG has 0..* FRAMES
        FRAME has dimensions same as DIALOG
        FRAME has 0..1 BACKGROUND
            BACKGROUND has color
            BACKGROUND has image
            BACKGROUND has transparency
        FRAME has 0..* IMAGES
            IMAGE has file
            IMAGE has position relative to frame position
        FRAME has 0..* TEXTS
            TEXT has text
            TEXT has position

    ----------------------------------------------------------------------------------------
    What is the data structure of the dialog? Dict containing surfaces and other information
    ----------------------------------------------------------------------------------------
    {
        'background' : DlgSurf(<Surface>, position)
        'images' : [DlgSurf(<Surface>, position), DlgSurf(<Surface>, position), DlgSurf(<Surface>, position)],
        'texts' : [(<Surface>, position)],
        'frames' : [
            {
                'background' : DlgSurf(<Surface>, position)
                'images' : [DlgSurf(<Surface>, position), DlgSurf(<Surface>, position), DlgSurf(<Surface>, position)],
                'texts' : [DlgSurf(<Surface>, position)]
            },
            {
                'background' : DlgSurf(<Surface>, position)
                'images' : [DlgSurf(<Surface>, position), DlgSurf(<Surface>, position), DlgSurf(<Surface>, position)],
                'texts' : [DlgSurf(<Surface>, position)]
            }
        ]
    }

    ----------------------------------------
    How dialogs are incorporated into pyRPG?
    ----------------------------------------
    - dialog is defined as an inline json definition in scene data and stored with dialog_id on engine level
    - during initiation of the scene, dialogs are transformed from text definition to dict object containing
      surfaces and positions. This dialog object is stored on engine level in dialogs dictionary.
    - Using script or command, dialog can be found in engine.dialogs and dislpayed.

        "dialogs" : [
                {
                    "id" : "welcome_dlg",
                    "template" : "welcome.json",
                    "params" : {????},
                    "data" : {
                        "frames" : [
                            {
                                "dimensions" : [100, 100],
                                "background_color" : "#FFFFFF",
                                "background_alpha" : 128
                            }
                        ]
                    }
                }
            ]

    - dialog is then used during scene phase
        "actions" : [
            ["execute_script", {"script_body" : "print(f'QUEST HAS STARTED')"}],
            ["show_dialog", {"dialog_id" : "welcome_dlg"}]

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
import re # For removing C-style comments from JSON file

import pygame
from collections import namedtuple
from .bitmap_font import BitmapFont

# Define position as a namedtuple
Pos = namedtuple('Pos', ['x', 'y'])

# Define tuple (surface, position) as a namedtuple
DlgSurf = namedtuple('DlgSurf', ['surf', 'pos'])

########################################################
### Module public functions
########################################################

def get_no_of_frames(dlg_obj):
    ''' Return number of frames in the dialog.
    '''

    return len(dlg_obj.get('frames', []))

def prepare_dlg_obj_from_data(dlg_data, img_path=None, font_path=None):
    ''' Prepares dictionary with surfaces based on dlg_data specification.
    Details about the structure od dlg_data can be found in 
    resources/dialogs/_DialogJSONStructure.md.

    Parameters:

        :param dlg_data: Data in a form of python dictionary
        :type dlg_data: dict

        :param img_path: Path where the images for dialog generation are found
        :type img_path: Path

        :param font_path: Path where font definitions are found
        :type font_path: Path

        :return: Dictionary with dialog objects containing surfaces and positions.
        :rtype: dict
    '''

    # New empty dialog object
    new_dlg_obj = {}

    ##########################################
    # Generate and Store dialog level surfaces
    ##########################################

    # Store dlg background surface
    if dlg_data.get('background', None):
        new_dlg_obj.update({'background' : _get_dlg_bckgrnd(dlg_data, img_path=img_path)})

    # Store dlg images - TBD
    new_dlg_obj.update({'images' : _get_dlg_images(dlg_data, img_path=img_path)})

    # Store dlg texts
    new_dlg_obj.update({'texts' : _get_dlg_texts(dlg_data, font_path=font_path)})

    ##########################################
    # Generate and Store frame level surfaces
    ##########################################

    # Prepare empty list of frames
    new_dlg_frames = []

    # Iterate all frames
    for frame_id, frame_data in enumerate(dlg_data.get('frames', [])):

        # Prepare empty frame object
        new_dlg_frame_obj = {}

        # Store dialog frame background if defined
        if frame_data.get('background', None):
            new_dlg_frame_obj.update({'background' : _get_dlg_frame_bckgrnd(dlg_data, frame=frame_id, img_path=img_path)})

        # Store dialog frame images
        new_dlg_frame_obj.update({'images' : _get_dlg_frame_images(dlg_data, frame=frame_id, img_path=img_path)})

        # Store dialog frame texts
        new_dlg_frame_obj.update({'texts' : _get_dlg_frame_texts(dlg_data, frame=frame_id, font_path=font_path)})

        # Add prepared frame to the list of all frames
        new_dlg_frames.append(new_dlg_frame_obj)

    # Add list of frames to the final dialog object
    new_dlg_obj.update({'frames' : new_dlg_frames})

    return new_dlg_obj

def display_dlg(target, position, dlg_obj, frame=None):
    ''' Blit prepared dialog object (or particular dialog frame)
    onto the target surface.

    {
        'background' : DlgSurf(<Surface>, position)
        'images' : [DlgSurf(<Surface>, position), DlgSurf(<Surface>, position), DlgSurf(<Surface>, position)],
        'texts' : [(<Surface>, position)],
        'frames' : [
            {
                'background' : DlgSurf(<Surface>, position)
                'images' : [DlgSurf(<Surface>, position), DlgSurf(<Surface>, position), DlgSurf(<Surface>, position)],
                'texts' : [DlgSurf(<Surface>, position)]
            },
            {
                'background' : DlgSurf(<Surface>, position)
                'images' : [DlgSurf(<Surface>, position), DlgSurf(<Surface>, position), DlgSurf(<Surface>, position)],
                'texts' : [DlgSurf(<Surface>, position)]
            }
        ]
    }

    Parameters:

        :param target: Target surface on which the dialog is displayed
        :type target: Surface

        :param position: Position of the top-left corner of the dialog on the target.
        :type position: tuple or list

        :param dlg_obj: Data in a form of python dictionary
        :type dlg_obj: dict

        :param frame: Frame number
        :type frame: integer
    '''

    ##########################################
    # Blit dialog level surfaces
    ##########################################

    # Blit dialog background
    if dlg_obj.get('background'):
        target.blit(dlg_obj.get('background').surf, position)

    # Blit dialog images
    for dlg_surf in dlg_obj.get('images', []):
        target.blit(dlg_surf.surf, (position[0] + dlg_surf.pos.x, position[1] + dlg_surf.pos.y))

    # Blit dialog texts
    for dlg_surf in dlg_obj.get('texts', []):
        target.blit(dlg_surf.surf, (position[0] + dlg_surf.pos.x, position[1] + dlg_surf.pos.y))

    ##########################################
    # Blit frame level surfaces
    ##########################################

    # Blit frame, if specified
    if frame is not None:

        try:
            frame_obj = dlg_obj.get('frames', [])[frame]

            # Blit frame background
            if frame_obj.get('background'):
                target.blit(frame_obj.get('background').surf, position)

            # Blit frame images
            for dlg_surf in frame_obj.get('images', []):
                target.blit(dlg_surf.surf, (position[0] + dlg_surf.pos.x, position[1] + dlg_surf.pos.y))

            # Blit frame texts
            for dlg_surf in frame_obj.get('texts', []):
                target.blit(dlg_surf.surf, (position[0] + dlg_surf.pos.x, position[1] + dlg_surf.pos.y))

        except:
            # In case frame is not defined
            raise ValueError

########################################################
### Module private functions
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

def _get_dlg_frame_bckgrnd(dlg_data, frame, img_path=None):
    ''' Get the background surface of the given frame in a form of
    Surface and position. This is further used in prepare_dlg_obj_from_data to
    correctly display the frame background with alpha channel.

    Parameters:

        :param dlg_data: Data in a form of python dictionary
        :type dlg_data: dict

        :param frame: Number of the frame
        :type dlg_data: int

        :param img_path: Path where the images for dialog generation are found
        :type img_path: Path

        :return: DlgSurf containing Surface with the dialog background and position [0,0]
        :rtype: DlgSurf
    '''

    # Get frame data
    frame_data = dlg_data.get('frames')[frame]

    # Get frame background data
    dlg_frame_bckgrnd_data = frame_data.get('background', {})

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

def _get_dlg_frame_images(dlg_data, frame, img_path=None):
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
    frame_data = dlg_data.get('frames')[frame]

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

def _get_dlg_frame_texts(dlg_data, frame, font_path=None):
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
    frame_data = dlg_data.get('frames')[frame]

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
    window.fill((50, 0, 0))

    ##############
    # PREPARE DIALOG
    ##############

    # Read the dialog data from JSON
    try:
        with open('pyrpg/utils/dlg_example.json', 'r') as dlg_file:
            json_dlg_data = dlg_file.read()
            dlg_data = json.loads(re.sub("//.*", "", json_dlg_data, flags=re.MULTILINE))
    except FileNotFoundError:
        print(f"Dialog file '{file}' not found.")
        raise

    pprint(dlg_data)

    # Convert the dialog data to dialog object containing surfaces and positions
    dlg_object = prepare_dlg_obj_from_data(dlg_data, img_path=Path('pyrpg/resources/images'), font_path=Path('pyrpg/resources/fonts'))

    pprint(dlg_object)

    ##############
    # DISPLAY DIALOG
    ##############

    display_dlg(target=window, position=(100, 100), dlg_obj=dlg_object, frame=None)

    # Show the result
    pygame.display.update()

    # Quit - wait for closing of the window
    pygame.event.clear()

    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            pygame.quit()
