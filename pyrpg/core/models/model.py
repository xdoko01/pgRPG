''' Module for loading, handling and caching Tiled SW models
'''

__all__ = ['load_model', 'get_cache_info', 'clear_cache', 'Model']


import pygame           # for saving tiles from Tileset source image
import functools        # for cache decorator
import json             # necessary to parse json files
from collections import namedtuple # for Tile namedtuple used in the Model class
from pygame import Vector2 as vect # for width and height of the tile of the model
from pathlib import Path

########################################################
### Package init commands
########################################################


########################################################
### Module globals
########################################################


########################################################
### Module functions
########################################################

def load_model(filepath, dim):
    ''' Loads model from the Tiled SW tileset
    and returns the new model instance.

    Parameters:
        :param filepath: Path to JSON file with the model
        :type filepath: Path

        :param dim: Required dimensions of the model tiles
        :type dim: vect (pygame.Vector2)

        :return: Returns model instance if success

        :raises: ValueException, if model cannot be created

    Called from:
        components module -> RenderableModel init
    '''

    try:
        new_model = Model(filepath)
    except ValueError:
        print(f"Error during init of the model '{filepath}'")
        raise ValueError

    # If resize is needed, proceed
    if new_model.dim != dim:
        new_model.resize_model(dim)

    return new_model

def get_cache_info():
    print(Model.cache_info())

def clear_cache():
    Model.cache_clear()

########################################################
### Component classes
########################################################

# Namedtuple used in the model structure
Tile = namedtuple('Tile', ('tileid', 'duration'))


# Cached model class
@functools.lru_cache(maxsize=32)
class Model(object):
    ''' Animated model of the entity
    '''

    __slots__ = ['images', 'frames', 'actions', 'name', 'model_file', 'dim', 'dim_2', 'no_tile']

    # Allowed model directions and actions
    DIRECTIONS = ['up', 'down', 'left', 'right']
    ACTIONS = [ 'move', 'idle',
                'idle_thrust', 'thrust',
                'idle_slash', 'slash',
                'idle_shoot', 'shoot',
                'idle_spellcast', 'spellcast',
                'expire']

    def __init__(self, model_file):
        ''' Read the information about frames and animations from
        json and png files and store it into the internal variables

        Parameters:
            :param model_file: Path to the model json file
            :type model_file: str

            :raise: ValueError - in case model_file is not found or has problem
        '''

        super().__init__()

        # Get the model name
        self.model_file = model_file

        # Initiate variables
        self.name = None

        # Read this from the json Tileset file
        #self.d_w = self.d_h = self.w = self.h = None
        self.dim = self.dim_2 = None

        self.images = {}
        self.frames = {}
        self.actions = set()

        # No tile is used in case tile for given action / direction / frame is not found
        # see RenderableModel.get_frame
        self.no_tile = pygame.Surface((0, 0))

        try:

            # Load model from model file and fill the Model instance variables
            self._load_model(self.model_file)

            # Check that model is complete, i.e. for all actions contains all directions
            self._check_model()

        except:
            # Notify component factory that initiation has failed
            raise ValueError

    def _load_model(self, model_path):
        ''' Loads model from the json file located on the
        model_path.
        '''

        # Open the model json file
        try:
            with open(model_path, 'r') as model_file:
                json_model_data = model_file.read()
                model_data = json.loads(json_model_data)
        except FileNotFoundError:
            print(f"Model file '{model_path}' not found.")
            # Notify component factory that initiation has failed
            raise ValueError

        # Store name and dimensions of the model
        self.name = model_data.get('name')
        self.dim = vect(model_data.get('tilewidth'), model_data.get('tileheight'))
        self.dim_2 = self.dim / 2

        # Load image with all model tiles
        try:
            image = pygame.image.load(str(Path(self.model_file).parent / Path(model_data.get('image', '')))).convert()
        except AttributeError:
            print(f"Unexpected error while processing imige for model file '{model_data}'")
            raise ValueError

        # Set color for transparent key
        image.set_colorkey(pygame.Color(model_data.get('transparentcolor', '#000000')))

        # Read the picture data from texture file - necessary for saving tiles
        image_width = model_data.get('imagewidth', 0)

        #####
        # Store the tiles 
        #####

        # Go through the list of all tiles
        for anim_tile in model_data.get('tiles', []):

            ### 
            # 1. Read tile properties
            ###

            action = None
            direction = None
            repeat = True
            action_frame = None

            # Save the properties into locals - must be done in such ugly way due to json format
            for prop in anim_tile.get('properties', []):

                # Read all tile properties and store their values
                if prop.get('name') == 'action': action = prop.get('value')
                if prop.get('name') == 'direction': direction = prop.get('value')
                if prop.get('name') == 'repeat': repeat = prop.get('value')
                if prop.get('name') == 'action_frame': action_frame = prop.get('value')

            ###
            # 2. Read and save the tiles
            ###

            # Check that action is valid and hence we can proceed with saving
            if action in Model.ACTIONS:

                # Record that action is supported
                self.actions.add(action)

                # Prepare the list that will be added to list frames.tiles
                tiles = []

                # Check if tile is static (one tile) or animation - if static, save differently
                if not anim_tile.get('animation', None):

                    # Get ID of the tile
                    tileid = anim_tile.get('id', 0)

                    # Static tile has duration 0
                    duration = 0

                    # Do not repeat static tile
                    repeat = False

                    # Prepare the tile texture - rectangle from the image
                    rect = ((int(tileid) % (image_width // self.dim.x)) * self.dim.x,
                            (int(tileid) // (image_width // self.dim.y)) * self.dim.y,
                            self.dim.x, self.dim.y)

                    # Save the image of the tile to images dictionary
                    self.images.update({tileid : image.subsurface(rect)})

                    # Prepare the tile and out it into the tiles list
                    tiles.append(Tile(tileid=tileid, duration=duration))

                else:
                    # Iterate all the animation frames for given action and direction
                    for frame_dict in anim_tile.get('animation'):

                        # Get ID of the tile
                        tileid = frame_dict.get('tileid', 0)

                        # Read duration
                        duration = frame_dict.get('duration', 0)

                        # Prepare the tile texture - rectangle from the image
                        rect = ((int(tileid) % (image_width // self.dim.x)) * self.dim.x,
                                (int(tileid) // (image_width // self.dim.y)) * self.dim.y,
                                self.dim.x, self.dim.y)

                        # Save the image of the tile to images dictionary
                        self.images.update({tileid : image.subsurface(rect)})

                        # Prepare the tile and out it into the tiles list
                        tiles.append(Tile(tileid=tileid, duration=duration))


                ## Save the information in the frames dictionary properly

                # In case direction is not specified on the action
                if not direction:

                    # Reset completely the action
                    self.frames.update({action : {}})

                    # Create all existing directions automatically
                    for new_dir in Model.DIRECTIONS:

                        # Add new direction
                        self.frames.get(action).update(
                            {
                                new_dir : {
                                    'tiles' : tiles,
                                    'repeat' : repeat,
                                    'action_frame' : -1 if not action_frame else action_frame
                                }
                            })

                # In case that new direction is specified
                elif direction in Model.DIRECTIONS:

                    # In case action already exists, add new direction
                    if self.frames.get(action, None):
                        self.frames.get(action).update(
                            {
                                direction : {
                                    'tiles' : tiles,
                                    'repeat' : repeat,
                                    'action_frame' : -1 if not action_frame else action_frame
                                }
                            })
                    else:
                        self.frames.update(
                            {
                                action : {
                                    direction : {
                                        'tiles' : tiles,
                                        'repeat' : repeat,
                                        'action_frame' : -1 if not action_frame else action_frame
                                    }
                                }
                            })

                # In case direction is not defined
                else:
                    print(f'Not allowed direction {direction} for action {action}')
                    raise ValueError

    def _check_model(self):
        ''' Checks if all valid directions exist for all actions.
        Also checks that idle action exists.
        '''

        # Check that all actions have all directions
        for action, dir_dict in self.frames.items():
            for direction in Model.DIRECTIONS:
                if not dir_dict.get(direction, None):
                    print(f"Direction '{direction}' is not defined for action '{action}'")
                    raise ValueError

        # Check that 'idle' action is implemented
        if not self.frames.get('idle', None):
            print(f"Mandatory idle action is not defined for the model")
            raise ValueError

    def resize_model(self, new_tile_dim=(64, 64)):
        ''' Resize model if needed
        '''

        # Iterate to the images dictionary and resize
        for tileid, image in self.images.items():
            self.images.update({ tileid : pygame.transform.scale(image, (new_tile_dim)) })

        # Update model information about width and height
        self.dim = vect(new_tile_dim)
        self.dim_2 = self.dim / 2

    def get_frame(self, action, direction, frame_id):
        try:
            frame = self.frames.get(action).get(direction).get('tiles')[frame_id]
            return (self.images.get(frame.tileid), frame.duration)
        except (KeyError, AttributeError):
            return (self.no_tile, 0)

    def get_frame_duration(self, action, direction, frame_id):
        try:
            return self.frames.get(action).get(direction).get('tiles')[frame_id].duration
        except (KeyError, AttributeError):
            return 0

    def get_frame_image(self, action, direction, frame_id):
        try:
            return self.images.get(self.frames.get(action).get(direction).get('tiles')[frame_id].tileid)
        except (KeyError, AttributeError):
            return self.no_tile
    
    def get_idle_image(self):
        """Static image for usage in inventory and similar.
        """
        return self.get_frame_image(action='idle', direction='down', frame_id=0)


    def is_action_frame(self, action, direction, frame_id):
        try:
            return (frame_id == self.get_action_frame(action, direction))
        except (KeyError, AttributeError):
            return False

    def get_action_frame(self, action, direction):
        try:
            # If action frame is not defined for given action and direction, return -1
            return self.frames.get(action).get(direction).get('action_frame', -1)
        except (KeyError, AttributeError):
            return -1
    
    def get_next_frame(self, action, direction, frame_id):
        frame = self.frames.get(action).get(direction)
        return (frame_id + 1) % len(frame.get('tiles')) if frame.get('repeat', False) else min(frame_id + 1, len(frame.get('tiles')) - 1)


    def __str__(self):

        from pprint import pformat
        import ctypes           # to show number of references to an instance

        return f'\n*Instance of {self.__class__.__name__} ({hex(id(self))}) [{ctypes.c_long.from_address(id(self)).value}]:\n\
**name\t\t\t({hex(id(self.name))}) [{ctypes.c_long.from_address(id(self.name)).value}]:\t{self.name}\n\
**dim\t\t\t({hex(id(self.dim))}) [{ctypes.c_long.from_address(id(self.dim)).value}]:\t{self.dim}\n\
**images\t\t({hex(id(self.images))}) [{ctypes.c_long.from_address(id(self.images)).value}]:\t{len(self.images)}\n\
**actions\t\t({hex(id(self.actions))}) [{ctypes.c_long.from_address(id(self.actions)).value}]:\t{pformat(self.actions)}\n\
**frames\t\t({hex(id(self.frames))}) [{ctypes.c_long.from_address(id(self.frames)).value}]:\n{pformat(self.frames)}\n'


if __name__ == '__main__':

    # Init pygame
    pygame.init()
    window = pygame.display.set_mode((100, 100), 0, 32)

    # Load model in required resolution
    test_model = load_model('experiments/ecs/resources/models/orcfemale.json', (64, 64))

    # Calculate the new dimensions of the window in order to fit all the images and animations
    # based on model dimensions - show in display_columns_no columns + additional row fo info text
    display_columns_no = 8
    new_window_dim = (int(test_model.dim.x * display_columns_no), int(test_model.dim.y * (len(test_model.images) // display_columns_no + 1)))
    window = pygame.display.set_mode(new_window_dim, 0, 32)

    # Change the window heading
    pygame.display.set_caption(f' File: {test_model.model_file}, Dim: ({test_model.dim.x}, {test_model.dim.y}), No of images: {len(test_model.images)}, No of actions: {len(test_model.frames)}')

    # Print the details
    print(test_model)

    get_cache_info()
    clear_cache()
    get_cache_info()

    # Text font is based on model resolution
    font_size = int(test_model.dim.x / 4)
    font = pygame.font.Font('experiments/bitmap_font/good_neighbors.fnt', font_size)

    # Initiate dict for storing actual frame and duration
    last_time_frame = {}

    for action, dir_dict in test_model.frames.items():
        last_time_frame.update( { action : {} })
        for direction, dir_data in dir_dict.items():
            last_time_frame.get(action).update( {direction : { 'last_time' : pygame.time.get_ticks(), 'last_frame' : 0}})

    # Indicate that infinite loop should continue
    running = True

    # Switch between images and frames
    toggle_anim = True

    while running:

        # Reset the screen
        window.fill((0, 0, 0))

        # Check for End and keys
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_F1:
                    toggle_anim = not toggle_anim

        # Show either images or animations based on toggle (F1 key)
        if not toggle_anim:

            # Show images
            for i, (tileid, image) in enumerate(test_model.images.items()):
                # Blit image
                window.blit(image, ((i % display_columns_no) * test_model.dim.x, (i // display_columns_no) * test_model.dim.y))
                # Blit tileid
                tileid_text = font.render(str(tileid), True, pygame.Color('white'))
                window.blit(tileid_text, ((i % display_columns_no) * test_model.dim.x, (i // display_columns_no) * test_model.dim.y))

        else:

            # Show animations
            for i, (action, dir_dict) in enumerate(test_model.frames.items()):
                for j, (direction, dir_data) in enumerate(dir_dict.items()):

                    # Get current time
                    current_time = pygame.time.get_ticks()

                    # Get last frame id of the animation (if nothing found use 0)
                    last_frame = last_time_frame.get(action).get(direction).get('last_frame')

                    # Get last time of the animation update (if nothing found use current time)
                    last_time = last_time_frame.get(action).get(direction).get('last_time')

                    # Get the duration
                    duration = test_model.get_frame_duration(action, direction, last_frame)

                    # Set the correct frame if displayed long enough
                    if current_time - last_time > duration:
                        #last_frame = (last_frame + 1) % len(dir_data.get('tiles'))
                        last_frame = test_model.get_next_frame(action, direction, last_frame)
                        last_time = current_time

                        # Remember last time and frame of updated animation
                        last_time_frame.get(action).update( {direction : { 'last_time' : last_time, 'last_frame' : last_frame}})

                    # Get the correct frame
                    #frame = dir_data.get('tiles')[last_frame].tileid
                    #image = test_model.images.get(frame)
                    image = test_model.get_frame_image(action, direction, last_frame)

                    # Blit animation
                    window.blit(image, (j * test_model.dim.x, i * test_model.dim.y))

                    # Blit animation info
                    tileid_text1 = font.render(f'{action}', True, pygame.Color('white'))
                    tileid_text2 = font.render(f'{direction}', True, pygame.Color('white'))
                    tileid_text3 = font.render(str(dir_data.get('repeat')), True, pygame.Color('white'))
                    tileid_text4 = font.render(f'{last_frame}', True, pygame.Color('white'))
                    window.blit(tileid_text1, (j * test_model.dim.x, i * test_model.dim.y))
                    window.blit(tileid_text2, (j * test_model.dim.x, i * test_model.dim.y + font_size))
                    window.blit(tileid_text3, (j * test_model.dim.x, i * test_model.dim.y + 2 * font_size))
                    window.blit(tileid_text4, ((j+1) * test_model.dim.x - font_size, i * test_model.dim.y))
                    # Blit 'A' on action frame
                    if test_model.is_action_frame(action, direction, last_frame):
                        tileid_text5 = font.render('A', True, pygame.Color('white'))
                        window.blit(tileid_text5, ((j+1) * test_model.dim.x - font_size, (i+1) * test_model.dim.y - font_size))


        # Info text on the screen
        window.blit(font.render('Press F1 to toggle between images and animations.', True, pygame.Color('white')), (0, new_window_dim[1] - font_size))

        # Put everything on the screen
        pygame.display.flip()
