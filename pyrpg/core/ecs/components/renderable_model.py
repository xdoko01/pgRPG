''' Module "pyrpg.core.ecs.components.renderable_model" contains
RenderableModel component implemented as a RenderableModel class.

Use 'python -m pyrpg.core.ecs.components.renderable_model -v' to run
module tests.
'''

import pygame
import pyrpg.core.models as model # For cached animated model in RenderableModel entity
import pyrpg.core.config.config as config # For TILE_RES
from pyrpg.core.config.paths import Path, MODEL_PATH
from .component import Component

class RenderableModel(Component):
    ''' Entity is displayable as animated model on the game screen.

    Used by:
        - RenderModelWorldProcessor

    Examples of JSON definition:
        {"type" : "RenderableModel", "params" : {"model" : "darkfemale.json"}}
        {"type" : "RenderableModel", "params" : {"model" : "darkfemale.json", "action" : "idle"}}

    Tests:
        >>> c = RenderableModel(**{"model" : "darkfemale.json", "action" : "idle"})
    '''

    __slots__ = ['model', 'last_frame', 'last_time', 'is_action_frame', 'action']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new RenderableModel component.

        Parameters:
            :param model_name: Name of the model stored in MODEL_PATH directory (mandatory)
            :type model_name: str

            :param action: Initial animated action of the model (optional, default = idle)
            :type action: str

            :raise: ValueError - in case model file is not found or has problem
        '''

        super().__init__()

        # Get the model name
        model_file = kwargs.get('model', '')

        # Get the initial action of the model
        self.action = kwargs.get('action', 'idle')

        # Check the model name and the action name for validity
        try:
            assert isinstance(model_file, str), f'Model file name "{model_file}" is not valid.'
            assert isinstance(self.action, str) and self.action in model.Model.ACTIONS, f'Action "{self.action}" is not allowed animation.'
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError

        # Initiate new model
        try:
            #self.model = model.load_model(str(MODEL_PATH / model_file), (config.TILE_RES, config.TILE_RES))
            self.model = model.load_model(MODEL_PATH / Path(model_file), (config.TILE_RES, config.TILE_RES))
        except:
            print(f'Something went wrong during initiation of the model "{MODEL_PATH / Path(model_file)}"')
            # Notify component factory that initiation has failed
            raise ValueError

        # Time and frame must be remembered for animation
        self.last_frame = 0
        self.last_time = pygame.time.get_ticks()
        self.is_action_frame = False

    def set_action(self, action):
        ''' Reset frame and time in case new action is
        assigned.
        '''

        # In case of action change - reset the anim variables
        if action != self.action:
            self.action = action
            self.last_frame = 0
            self.last_time = pygame.time.get_ticks()

    def topleft(self, pos):
        ''' Returns correction of coordinates to display the sprite correctly

        Parameters:
            :param pos: Position on the map in pixels.
            :type pos: tuple, list

            :return: Position of the topleft corner of the image as a tuple.
        '''
        return pos - self.model.dim_2

    def get_current_frame(self, direction, action=None, frame_id=None):
        ''' Only get the frame, do not do any animation shifting
        In case frame, action or direction does not exist, returns empty frame.
        '''
        return self.model.get_frame_image(self.action if action is None else action, direction, self.last_frame if frame_id is None else frame_id)

    def update_frame(self, direction):
        ''' Update last_frame, last_time, is_action_frame based
        on elapsed time. 
        '''
        # Get the currect time and measure the delay from last_time
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.last_time
        frame_duration = self.model.get_frame_duration(self.action, direction, self.last_frame)

        # if delay is greater move to the next frame and reset timer (only in case duration of frame is > 0)
        if frame_duration and elapsed_time > frame_duration:
            self.last_time = current_time
            self.last_frame = self.model.get_next_frame(self.action, direction, self.last_frame)
            self.is_action_frame = self.model.is_action_frame(self.action, direction, self.last_frame)
            #print(f'elapsed time: {current_time - self.last_time}, frame duration: {self.model.get_frame_duration(self.action, direction, self.last_frame)}, to {self.last_frame}, {self.action}, {direction} action frame set to {self.is_action_frame}, for model {self.model.name}')
        else: 
            # Set the flag to False, I want to have it True only once when the animation changes. Otherwise
            # I will have multiple actions triggered.
            self.is_action_frame = False


    def pre_save(self):
        ''' Prepare component for saving - remove all references to
        non-serializable objects
        '''
        self.model = None

    def post_load(self):
        ''' Regenerate all non-serializable objects for the component
        '''
        try:
            #self.model = model.load_model(str(config.MODEL_PATH / model_file), (config.TILE_RES, config.TILE_RES))
            self.model = model.load_model(MODEL_PATH / model_file, (config.TILE_RES, config.TILE_RES))

        except:
            raise ValueError


if __name__ == '__main__':
    import doctest
    doctest.testmod()


### ORIGINAL CLASS WITH ORIGINAL MODEL
"""
class RenderableModel(Component):
	''' Entity is displayable as animated model on the game screen.

	Used by:
		-	RenderModelWorldProcessor

	Tests:
		>>> c = RenderableModel()
	'''

	__slots__ = ['model', 'last_frame', 'last_time', 'is_last_frame', 'action']

	def __init__(self, *args, **kwargs):
		''' Initiate values for the new RenderableModel component.

		Parameters:
			:param model_name: Name of the model stored in MODEL_PATH directory
			:type model_name: str

			:param action: Initial animated action of the model
			:type action: str
			
			:raise: ValueError - in case model file is not found or has problem
		'''

		super().__init__()

		# Get the model name
		model_file = kwargs.get('model', '')

		# Get the initial action of the model
		self.action = kwargs.get('action', 'default') 

		# Check the model name and the action name for validity
		try:
			assert isinstance(model_file, str), f'Model file name {model_file} is not valid.'
			assert isinstance(self.action, str) and self.action in model.Model.ACTIONS, f'Action "{self.action}" is not allowed animation.'
		except AssertionError:
			# Notify component factory that initiation has failed
			raise ValueError

		# Initiate new model
		try:
			self.model = model.Model(model_file)
		except:
			print(f'Something went wrong during initiation of the model {model_file}')
			# Notify component factory that initiation has failed
			raise ValueError

		# Time and frame must be remembered for animation
		self.last_frame = 0
		self.last_time = pygame.time.get_ticks()

		# In order to launch projectile, I need to know the last frame of animation
		self.is_last_frame = False

		print(self.model)

	def set_action(self, action):
		''' Check if action is supported and set it - reset the frame and time.
		If action is not supported then set action to 'default' action.
		'''
		# In case of non-supported action, change to default
		if action not in self.model.texture_actions: action = 'default'
		
		# In case of action change - reset the anim variables
		if action != self.action:
			self.action = action
			self.last_frame = 0
			self.last_time = pygame.time.get_ticks()

	def topleft(self, pos):
		''' Returns correction of coordinates to display the sprite correctly

		Parameters:
			:param pos: Position on the map in pixels.
			:type pos: tuple, list
			
			:return: Position of the topleft corner of the image as a tuple.
		'''
		return (pos[0] - self.model.d_w, pos[1] - self.model.d_h)

	def get_current_frame(self, direction, action=None, frame_id=None):
		''' Only get the frame, do not do any animation shifting
		In case frame does not exist, return empty frame.
		'''
		try:
			return self.model.texture_data.get(self.action if action is None else action).get(direction)[self.last_frame if frame_id is None else frame_id].get('tile')
		except:
			return self.model.no_tile
	
	def update_frame(self, direction):
		''' Update the animation of the model based on time 
		Just update the frame and that is it.
		'''

		# Get no of the animated frames for given action and direction - if direction not found, use down
		anim_length = self.model.texture_length.get(self.action).get(direction)
		
		# Fix the last_frame so it is always within 0 .. anim_length
		#self.last_frame = self.last_frame % anim_length

		# Get dictionary describing the current frame
		curr_frame = self.model.texture_data.get(self.action).get(direction)[self.last_frame]

		# If action is animated - then shift based on time
		if self.model.texture_dynamic.get(self.action).get(direction):

			# Get the currect time and measure the delay from last_time
			current_time = pygame.time.get_ticks()
		
			# if delay is greater move to the next frame and reset timer
			if current_time - self.last_time > curr_frame.get('duration'):
				self.last_time = current_time
				self.last_frame = (self.last_frame + 1) % anim_length
				
				# Set the flag if animation is on the last frame. Important for emitting projectiles
				self.is_last_frame = True if self.last_frame == anim_length - 1 else False

			else: 
				# Set the flag to False, I want to have it True only once when the animation changes
				self.is_last_frame = False


	def get_frame(self, direction, action=None, frame_id=None):
		''' This is OBSOLETE function
			Get the current frame for display. It is taking into account animated frames.
		'''
		# Get length of the animation and use it for modulo on last_frame.
		# This is needed because if action/direction is changed, last frame can be bigger
		# than number of frames in the animation - hence causing error.
		# TODO - Alternativelly, reset last_frame to 0 with every change of direction/action
		#	- but where is the right place to do it??
		
		####### check that tile exists for given action, direction and frame
		
		## If action is not specified, use action from component
		if not action: action = self.action

		########
		# In case of particular frame (used with Wearables to be synchronized with animation)
		if frame_id:
			# In case that action / direction does not exist for the model, do nothing
			try:
				return self.model.texture_data.get(action, {}).get(direction, [])[frame_id].get('tile')
			except:
				return self.model.no_tile
		########

		try:
			# Get no of the animated frames for given action and direction
			anim_length = self.model.texture_length.get(action).get(direction)
			
			# Fix the last_frame so it is always within 0 .. anim_length
			self.last_frame = self.last_frame % anim_length

			# Get dictionary describing the current frame
			curr_frame = self.model.texture_data.get(action).get(direction)[self.last_frame]

			# If action is animated - then shift based on time
			if self.model.texture_dynamic.get(action).get(direction):

				# Get the currect time and measure the delay from last_time
				current_time = pygame.time.get_ticks()
			
				# if delay is greater move to the next frame and reset timer
				if current_time - self.last_time > curr_frame.get('duration'):
					self.last_time = current_time
					self.last_frame = (self.last_frame + 1) % anim_length
					
					# Set the flag if animation is on the last frame. Important for emitting projectiles
					self.is_last_frame = True if self.last_frame == anim_length - 1 else False

				else: 
					# Set the flag to False, I want to have it True only once when the animation changes
					self.is_last_frame = False

			return self.model.texture_data.get(action).get(direction)[self.last_frame].get('tile')
		except:
			return self.model.no_tile

	#def set_next_frame(self, action, direction):
	#	''' Set the next frame for animation '''
	#	self.last_time = pygame.time.get_ticks() 
	#	self.last_frame = (self.last_frame + 1) % self.model.texture_length.get(action).get(direction)

	def pre_save(self):
		''' Prepare component for saving - remove all references to
		non-serializable objects
		'''
		self.model = None
	
	def post_load(self):
		''' Regenerate all non-serializable objects for the component
		'''
		try:
			self.model = model.Model(self.model_file)
		except:
			raise ValueError	
"""