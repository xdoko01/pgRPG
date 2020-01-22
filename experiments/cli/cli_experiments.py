'''
	Experiment for implementation of in-game console
	supporting input and output in graphics(pygame)

	Features
	********
		-	command buffer on text input
		-	buffer on text output and scrolling up and down in it (pgUp, pgDown)
		-	console transparent background
		-	picture as a console background
		-	animation of showing/hiding console in the game
		-	console header and footer
		-	transparent header, output, input - by implementing show function in header, textoutput etc
		-	header and footer can display dynamic data from app reference - time, position, fps, ...
		-	possibility to run scripts

	TODO
	****
		-	colors in text output - commands with different color than script lines and results
		-	directory with scripts as console parameter
		-	handling tabs as spaces
		-	text input supports more than one line
		-	scrolling text in header/footer
		-	fix error with input buffer
		-	fix so that program does not quit upon incorrect move command
		-	breaking the text in text output - to support big outputs		
		-	fix cursor not showing when moving around the text
		-	nicer show/hide animation of the console

	How to incorporate in the code
	******************************
		-	create console instance in the main class/module - reference to main/module
		-	add game.console_enabled property to the game instance
		-	in the main game loop test if console key was pressed - if yes, game.console_enabled = True
		-	if game.console_enabled = True then after generating game screen, generate also console screen
		-	show_amim_console for animated spawn in main game class
'''

from io import StringIO # for redirection of commands output to the graphical console
import sys	# for redirection of stdout to the graphical console
import pygame # for Surface and graphics init
import pygame.freetype # for all the fonts
import pygame.locals as pl # for key names
import cmd	# for command line support https://docs.python.org/3/library/cmd.html

class CommandLineProcessor(cmd.Cmd):
	''' Class implementing the logic behind console commands.
	Code was taken, modified and adjsuted from original Tuxemon game 
	https://github.com/Tuxemon/Tuxemon
	'''

	def __init__(self, app, input=sys.stdin, output=sys.stdout):
		''' Inherit from Cmd class. Output will need to be redirected 
		to console graphical output, otherwise it would go to the text
		window.
		'''

		# Initiate the parent class
		cmd.Cmd.__init__(self, stdin=input, stdout=output)
		self.app = app
		self.output = output

	def emptyline(self):
		''' In case empty line is entered, nothing happens
		'''
		pass

	def do_exit(self, line):
		''' If "exit" was typed on the command line, set the app's exit variable to True.
		'''
		self.app.exit = True
		return True

	def do_quit(self, line):
		'''If "quit" was typed on the command line, set the app's exit variable to True.
		'''
		self.app.exit = True
		return True
	
	def do_EOF(self, line):
		'''If you press CTRL-D on the command line, set the app's exit variable to True.
		'''
		self.do_quit(line)
		return True

	def do_py(self, line):
		''' Executes python commands in the console. App entity can be accessed
		by referencing self. See examples of possible usage below:
		 
		 - py print('Hello world') ... prints Hello World at the console
		 - py game ... prints reference to main game instance TestObject
		 - py game.pos = [200, 200] ... assignes new position to the game rect
		 - py game.surf.fill((0,0,0)) ... changes the color of the game rect to black
		 - py game.console.padding = (20,20,20,20) ... changes padding on the console
		'''
		
		console_out = sys.stdout = StringIO()

		globals_param = {'__buildins__' : None}
		
		# Here you can name the reference to game object that is used. 
		# For example 'app', 'engine', 'game', ...
		locals_param = {'game' : self.app}
		
		Result = None

		try:
			exec('Result = ' + line, globals_param, locals_param)
			Result = locals_param.get('Result')			
		except Exception as E:
			self.output.write(str(E))
		finally:
			self.output.write(str(console_out.getvalue()))
			if Result: self.output.write(str(Result))
			sys.stdout = sys.__stdout__

	def do_script(self, script_file):
		''' Run custom scripts that contain commands implemented in this class.

		Script example:
			move 300,300
			py print('I have moved the brick')
			py game.surf.fill((0,0,0))
			py print('I have colored the brick')
		'''
		try:
			# Open script file
			with open(script_file) as f:
				# For each line execute self.onecmd(line)
				self.output.write('>S>Script ' + script_file + ' started.')

				script_line = f.readline()
				script_line_no = 1
				error = None

				while script_line:
					error = self.onecmd(script_line.strip())
					if error: raise
					else: script_line = f.readline()
			
			# Inform that script has ended
			self.output.write('>S>Script finished successfully.')
			return None

		except:
			self.output.write('Error (' + str(error) + ') on line '+ str(script_line_no) + '. Command: ' + str(script_line.strip()))
			return -1

	def do_move(self, arg):
		''' Example of custom command implementation
		It is important to return True if success and False
		'''
		try:
			self.app.move(arg)
			return None
		except Exception as E:
			self.output.write(str(E))
			return -1

class Header:
	def __init__(self,
				console,	# Reference to parent Console instance
				width,
				config={
					'text' : 'Console v0.1. Position: {}',
					'text_params' : ['get_pos'],					
					'layout' : 'TEXT_RIGHT',
					'padding' : (0,0,0,0),
					'font_file' : 'experiments/cli/fonts/IBMPlexMono-Regular.ttf',
					'font_size' : 16,
					'font_antialias' : True,
					'font_color' : (255,255,255),
					'font_bck_color' : None,
					'bck_color' : (255,0,0),
					'bck_image' : None,
					'bck_image_resize' : True,
					'bck_alpha' : 0
				}):
		
		# Save the params 		
		for key in config: setattr(self, key, config.get(key))
		
		self.width = width
		self.console = console
		
		# TODO - maybe check here if already initiated??
		pygame.freetype.init()
		self.font_object = pygame.freetype.Font(
			 self.font_file,
			 self.font_size)

		# Get the hight of the text font line and store it in line_spacing
		(_, rect_tmp) = self.font_object.render('|', self.font_color, None )
		self.line_spacing = rect_tmp.height

		# Create surface for text
		(self.text_surface, self.text_rect) = self.font_object.render(self.text, self.font_color, None )

		# Prepare surface for text background if needed
		if self.font_bck_color:
			self.font_bckgrnd = pygame.Surface((self.text_rect.width, self.line_spacing))
			self.font_bckgrnd.fill(self.font_bck_color)

		# Calculate the dimensions of header - you must have font surface
		self.dim = (width, self.line_spacing+ self.padding[0] + self.padding[1])

		# Create header surface
		self.surface = pygame.Surface(self.dim)

		# Fill the header surface with background color
		self.surface.fill(self.bck_color)
		
		# Fill the surface with picture	if necessary
		if self.bck_image:
			self.bck_image = pygame.image.load(self.bck_image).convert()
			if self.bck_image_resize:
				self.bck_image = pygame.transform.scale(self.bck_image, (self.dim))
			
			# Blit the background picture on the header surface
			self.surface.blit(self.bck_image, (0, 0))

		# Set alpha of the header surface
		self.surface.set_alpha(self.bck_alpha)

	def update(self):
		''' Called from console update function in order to generate the dynamic
		text in the header.
		'''

		# Only do something if dynamic params are needed. Otherwise, it is not necessary
		if self.text_params:
			
			# prepare the dynamic text
			text = self.text.format(*[getattr(self.console.app, method_name)() for method_name in self.text_params])

			# generate the new text in self.text_surface object
			(self.text_surface, self.text_rect) = self.font_object.render(text, self.font_color, None )


	def show(self, surf, pos=(0, 0)):
		
		# Blit the surface background
		surf.blit(self.surface, pos)

		# Blit text background and text on the right spot based on layout
		if self.layout == 'TEXT_RIGHT':
			if self.font_bck_color: surf.blit(self.font_bckgrnd, (pos[0] + self.width - self.padding[3] - self.text_rect.width, pos[1] + self.padding[0]))
			surf.blit(self.text_surface, (pos[0] + self.width - self.padding[3] - self.text_rect.width, pos[1] + self.padding[0]))
		if self.layout == 'TEXT_LEFT':
			if self.font_bck_color: surf.blit(self.font_bckgrnd, (pos[0] + self.padding[2], pos[1] + self.padding[0]))
			surf.blit(self.text_surface, (pos[0] + self.padding[2], pos[1] + self.padding[0]))
		if self.layout == 'TEXT_CENTRE':
			if self.font_bck_color: surf.blit(self.font_bckgrnd, (pos[0] + self.width // 2 - self.text_rect.width // 2, pos[1] + self.padding[0]))
			surf.blit(self.text_surface, (pos[0] + self.width // 2 - self.text_rect.width // 2, pos[1] + self.padding[0]))
		
		# TODO - more layouts such as running text 	

	def get_height(self):
		return self.surface.get_height()
	
	def get_surface(self):
		return self.surface

class TextOutput:

	def __init__(self,
				console,	# Reference to parent Console instance
				width,
				config={
					'padding' : (0,0,0,0),
					'font_file' : 'experiments/cli/fonts/IBMPlexMono-Regular.ttf',
					'font_size' : 16,
					'font_antialias' : True,
					'font_color' : (255,255,255),
					'font_bck_color' : None,
					'bck_color' : (255,0,0),
					'bck_alpha' : 120,
					'buffer_size' : 100,
					'prompt' : None,
					'display_lines' : 13,
					'display_columns' : 80,
					'line_spacing' : None}):

		'''	
		initial_string='',
		font_file='',
		font_size=12,
		antialias=True,
		text_color=(0, 0, 0),
		buffer_size=20,
		lines_to_display=10,
		line_spacing=20,
		columns_to_display=80):
		'''

		# Save the params 		
		for key in config: setattr(self, key, config.get(key))

		# Save the required width
		self.width = width

		# Additional vars
		self.log = []
		#self.buffer_size = buffer_size
		#self.lines_to_display = lines_to_display
		#self.columns_to_display = columns_to_display
		self.offset_position = 0	

		#self.font_size = font_size
		#self.font_file = font_file
		#self.initial_string = initial_string
		#self.antialias = antialias
		#self.text_color = text_color
		#self.line_spacing = line_spacing

		pygame.freetype.init()
		self.font_object = pygame.freetype.Font(
			 self.font_file,
			 self.font_size)

		# Determine automatically the hight of the row - height of '|' character
		# in case the spacing is not given
		if not self.line_spacing:
			(_, rect_tmp) = self.font_object.render('|', self.font_color, None )
			self.line_spacing = rect_tmp.height

		# Every output line is stored as a separate surface. 
		# Final output surface consists of those lines
		self.surface_line = []
		self.surface = pygame.Surface((0,0))
		self.surface_height = self.surface.get_height()

	def write(self, text):
		''' Handles adding output text into textoutput buffer
		and shifting of the buffer
		'''

		# Remove newline at the end
		text.rstrip()

		# Based on newline character put every output line on separate row
		for text_line in text.split('\n'):
			
			# Only print if there is something to print
			if text_line:
				self.log.append(text_line)

				# Remove old rows from the buffer
				if len(self.log) > self.buffer_size:
					# Shift the log
					for i in range(1,len(self.log)):
						self.log[i-1] = self.log[i]
					del self.log[len(self.log)-1]

	def get_surface(self):
		return self.surface
	
	def get_height(self):
		return self.surface.get_height()
	
	def get_max_height(self):
		return (self.line_spacing * self.display_lines) + self.padding[0] + self.padding[1]
		#if not self.line_spacing: return (self.font_size * self.display_lines) + self.padding[0] + self.padding[1]
		#else: return (self.line_spacing * self.display_lines) + self.padding[0] + self.padding[1]
	
	def get_max_width(self):
		return self.width

	def update(self, events):
		''' Handles scrolling the output buffer by pressing
		pgUP and pgDOWN keys
		'''

		for event in events:
			if event.type == pygame.KEYDOWN:

				if event.key == pl.K_PAGEUP:
					self.offset_position = max([0, self.offset_position - self.display_lines])
					self.prepare_surface()

				elif event.key == pl.K_PAGEDOWN:
					self.offset_position = min([max([0, len(self.log) - self.display_lines]), self.offset_position + self.display_lines])
					self.prepare_surface()

				elif event.key == pl.K_RETURN:
					self.offset_position = max([0, len(self.log) - self.display_lines])
					self.prepare_surface()

	def show(self, surf, pos=(0,0)):
		
		# Blit output background
		surf.blit(self.surface, pos)

		# Blit all the line surfaces to the surface
		height = self.padding[0]
		for i in range(len(self.surface_line)):
			(line_surface, line_rect) = self.surface_line[i]
			
			# Blit font background
			if self.font_bck_color:
				text_bckgrnd = pygame.Surface((line_rect.width, line_rect.height))
				text_bckgrnd.fill(self.font_bck_color)
				
				# The position is calculated so that individual lines are aligned to the centre of the line
				surf.blit(text_bckgrnd, 
						(pos[0] + self.padding[2], 
						pos[1] + height + self.line_spacing - (( self.line_spacing - line_rect.height) // 2) - line_rect.height))

			# Blit font text
			# The position is calculated so that individual lines are aligned to the centre of the line
			surf.blit(line_surface, 
					(pos[0] + self.padding[2], 
					pos[1] + height + self.line_spacing - (( self.line_spacing - line_rect.height) // 2) - line_rect.height))

			# If no spacing is defined, use the height of the line surface rect
			# Otherwise use the parameter
			#if self.line_spacing: height = height + self.line_spacing
			#else: height = height + line_rect.height
			height = height + self.line_spacing
		
		self.surface_height = height + self.padding[1]

	def prepare_surface(self):
		''' Takes the log and based on the log genertes output lines (self.surface_line) and
		surface (self.surface). Those are used in show function to blit to the screen.
		'''
		print('Called Output prepare_surface ...') # only if return PgUp, pgDown pressed

		# First we need to clear all the buffer surfaces surfaces
		self.surface_line = []

		# We fill the surface_line list with log surfaces
		# for i in range(max([0, len(self.log) - self.lines_to_display]), len(self.log)):
		# print('From:' + str(self.offset_position) + ' To: ' + str(min([len(self.log), self.offset_position + self.lines_to_display])))
		# print('Len(self.log): ' + str(len(self.log)))

		for i in range(self.offset_position, min([len(self.log), self.offset_position + self.display_lines])):
			(surface_line_tmp, rect_tmp) = self.font_object.render(self.prompt + self.log[i], self.font_color, None )
			self.surface_line.append( (surface_line_tmp, rect_tmp) )

		# Re-render text surface, calc how big it is from individual linesurfaces
		# for width get maximal width from all surface_lines
		# for height get sum of all heights of surface lines in surface_line list 
		#if not self.line_spacing: surf_height =  int(sum([i.height for (j,i) in self.surface_line]) + self.padding[0] + self.padding[1])
		#else: surf_height = (self.line_spacing * self.display_lines) + self.padding[0] + self.padding[1]
		surf_height = (self.line_spacing * self.display_lines) + self.padding[0] + self.padding[1]

		self.dim = (self.width, surf_height)
		self.surface = pygame.Surface( #(
			#int(max([i.width for (j,i) in self.surface_line])), 
			#self.width,
			#surf_height),
			self.dim
			)

		# Fill the output surface with background color
		self.surface.fill(self.bck_color)
		
		# Set alpha of the header surface
		self.surface.set_alpha(self.bck_alpha)

		'''
		# Blit all the line surfaces to the surface
		height = self.padding[0]
		for i in range(len(self.surface_line)):
			(surface, _) = self.surface_line[i]
			
			if self.font_bck_color:
				text_bckgrnd = pygame.Surface((_.width, _.height))
				text_bckgrnd.fill(self.font_bck_color)
				self.surface.blit(text_bckgrnd, (self.padding[0], height))

			self.surface.blit(surface, (self.padding[0], height))
			#height = height + self.font_object.get_sized_glyph_height()
			# this is the only correct one as it is consistent with the total surface hight calculation 
			# that is based on a rectancle

			# If no spacing is defined, use the height of the line surface rect
			# Otherwise use the parameter
			if self.line_spacing: height = height + self.line_spacing
			else: height = height + _.height
			#height = height + self.font_object.get_sized_height()
			#height = height + 10
			#height = height + self.font_size
		
		self.surface_height = height + self.padding[1]
		'''

class TextInput:
	"""
	Copyright 2017, Silas Gyger, silasgyger@gmail.com, All rights reserved.
	Borrowed from https://github.com/Nearoo/pygame-text-input under the MIT license.

	Original above modified in the following way:
		- color input parameters changed to RGB
		- added font_file parameter/ removed font_family parameter
		- added buffer parameter
	
	This class lets the user input a piece of text, e.g. a name or a message.
	This class let's the user input a short, one-lines piece of text at a blinking cursor
	that can be moved using the arrow-keys. Delete, home and end work as well.
	"""
	
	def __init__(
			self,
			console,	# Reference to parent Console instance
			width,
			config={
				'padding' : (0,0,0,0),
				'font_file' : 'experiments/cli/fonts/IBMPlexMono-Regular.ttf',
				'font_size' : 16,
				'font_antialias' : True,
				'font_color' : (255,0,0),
				'font_bck_color' : None,
				'bck_color' : (0,255,0),
				'bck_alpha' : 150,
				'buffer_size' : 10,
				'prompt' : '>>>',
				'max_string_length' : 70,
				'repeat_keys_initial_ms' : 400,
				'repeat_keys_interval_ms' :35
				}):

		'''
		initial_string='',
		font_file='',
		font_size=12,
		antialias=True,
		text_color=(0, 0, 0),
		cursor_color=(0, 0, 0),
		repeat_keys_initial_ms=400,
		repeat_keys_interval_ms=35,
		max_string_length=-1,
		buffer_size=10):
		'''
		"""
		:param initial_string: Initial text to be displayed
		:param font_family: name or list of names for font (see pygame.font.match_font for precise format)
		:param font_size:  Size of font in pixels
		:param antialias: Determines if antialias is applied to font (uses more processing power)
		:param text_color: Color of text (duh)
		:param cursor_color: Color of cursor
		:param repeat_keys_initial_ms: Time in ms before keys are repeated when held
		:param repeat_keys_interval_ms: Interval between key press repetition when held
		:param max_string_length: Allowed length of text
		"""

		# Save the params 
		for key in config: setattr(self, key, config.get(key))
		
		# Text related vars:
		'''
		self.antialias = antialias
		self.text_color = text_color
		self.font_file = font_file
		self.font_size = font_size
		self.max_string_length = max_string_length
		self.input_string = ''
		self.initial_string = initial_string
		'''

		self.buffer = []
		#self.buffer_size = buffer_size
		self.buffer_position = 0
		# Initiate input text
		self.input_string = ''

		self.width = width

		pygame.freetype.init()
		self.font_object = pygame.freetype.Font(self.font_file, self.font_size)

		# Determine automatically the hight of the row - height of '|' character
		# This prevents the surface to change its height upon different hight of 
		# characters in input_string.
		(_, rect_tmp) = self.font_object.render('|', self.font_color, None )
		self.line_spacing= rect_tmp.height

		# Initiate cursor dimensions
		#self.cursor_dim = (int(self.font_size / 20 + 1), self.line_spacing)
		self.cursor_dim = (int(self.font_size / 2 + 1), self.line_spacing)

		# Init Surface from prompt -  it is necessary to calculate height of the whole console
		(self.text_surface, _)  = self.font_object.render(' ' if not self.prompt else self.prompt, self.font_color, None)
		self.surface = pygame.Surface((self.width, self.padding[0] + self.line_spacing + self.padding[1]))
	
		# Vars to make keydowns repeat after user pressed a key for some time:
		self.keyrepeat_counters = {}  # {event.key: (counter_int, event.unicode)} (look for "***")
		'''
		self.keyrepeat_intial_interval_ms = repeat_keys_initial_ms
		self.keyrepeat_interval_ms = repeat_keys_interval_ms
		'''

		# Things cursor:
		#self.cursor_surface = pygame.Surface((int(self.font_size / 20 + 1), self.font_size))
		self.cursor_surface = pygame.Surface(self.cursor_dim)
		self.cursor_surface.fill(self.font_color)
		# This is same rect as for text_input but it ends at the position of the cursor
		self.cursor_rect = pygame.Rect((0,0,0,0))

		self.cursor_position = len(self.prompt)  # Inside text
		self.cursor_visible = True  # Switches every self.cursor_switch_ms ms
		self.cursor_switch_ms = 500  # /|\
		self.cursor_ms_counter = 0
		self.clock = pygame.time.Clock()

	def get_height(self):
		return self.surface.get_height()

	def update(self, events):
		''' Processes keys pressed events
		'''

		for event in events:
			if event.type == pygame.KEYDOWN:
				self.cursor_visible = True  # So the user sees where he writes

				# If none exist, create counter for that key:
				if event.key not in self.keyrepeat_counters:
					self.keyrepeat_counters[event.key] = [0, event.unicode]

				if event.key == pl.K_BACKSPACE:
					self.input_string = (
						self.input_string[:max(self.cursor_position - 1, 0)]
						+ self.input_string[self.cursor_position:]
					)
					# Subtract one from cursor_pos, but do not go below zero:
					self.cursor_position = max(self.cursor_position - 1, 0)

				elif event.key == pl.K_DELETE:
					self.input_string = (
						self.input_string[:self.cursor_position]
						+ self.input_string[self.cursor_position + 1:]
					)

				elif event.key == pl.K_RETURN:
					# Only store if there is something to store
					if self.input_string:
						self.buffer.append(self.input_string)
						self.buffer_position = len(self.buffer)

						# Remove old rows from the buffer
						if len(self.buffer) > self.buffer_size:
							# Shift the log
							for i in range(1,len(self.buffer)):
								self.buffer[i-1] = self.buffer[i]
							del self.buffer[len(self.buffer)-1]
					
					return True

				elif event.key == pl.K_RIGHT:
					# Add one to cursor_pos, but do not exceed len(input_string)
					self.cursor_position = min(self.cursor_position + 1, len(self.input_string))
					print(self.cursor_position)

				elif event.key == pl.K_LEFT:
					# Subtract one from cursor_pos, but do not go below zero:
					self.cursor_position = max(self.cursor_position - 1, 0)
					print(self.cursor_position)

				elif event.key == pl.K_END:
					self.cursor_position = len(self.input_string)
					print(self.cursor_position)

				elif event.key == pl.K_HOME:
					self.cursor_position = 0
					print(self.cursor_position)

				# Scroll the buffer - to the history
				elif event.key == pl.K_UP:
					# Calc new buffer position
					if self.buffer_position >= 1:
						self.buffer_position = self.buffer_position - 1
					# restore previous input string - last in buffer
					print(self.buffer_position)
					self.input_string = self.buffer[self.buffer_position]
					# set cursor possition at the end of the string
					self.cursor_position = len(self.input_string)
					print(self.cursor_position)

				# Scroll the buffer - to the future
				elif event.key == pl.K_DOWN:
					# Calc new buffer position
					if self.buffer_position < len(self.buffer) - 1:
						self.buffer_position = self.buffer_position + 1
						# restore previous input string - last in buffer
						self.input_string = self.buffer[self.buffer_position]
						# set cursor possition at the end of the string
						self.cursor_position = len(self.input_string)
						print(self.cursor_position)
		
				elif len(self.input_string) < self.max_string_length or self.max_string_length == -1:
					# If no special key is pressed, add unicode of key to input_string
					self.input_string = (
						self.input_string[:self.cursor_position]
						+ event.unicode
						+ self.input_string[self.cursor_position:]
					)
					self.cursor_position += len(event.unicode)  # Some are empty, e.g. K_UP
					print(self.cursor_position)

			elif event.type == pl.KEYUP:
				# *** Because KEYUP doesn't include event.unicode, this dict is stored in such a weird way
				if event.key in self.keyrepeat_counters:
					del self.keyrepeat_counters[event.key]

		# Update key counters:
		for key in self.keyrepeat_counters:
			self.keyrepeat_counters[key][0] += self.clock.get_time()  # Update clock

			# Generate new key events if enough time has passed:
			if self.keyrepeat_counters[key][0] >= self.repeat_keys_initial_ms:
				self.keyrepeat_counters[key][0] = (
					self.repeat_keys_initial_ms
					- self.repeat_keys_interval_ms
				)

				event_key, event_unicode = key, self.keyrepeat_counters[key][1]
				pygame.event.post(pygame.event.Event(pl.KEYDOWN, key=event_key, unicode=event_unicode))

		# Re-render text surface:
		(self.text_surface, _rect)  = self.font_object.render(self.prompt + self.input_string, self.font_color, None)

		# Re-render the background surface
		self.surface = pygame.Surface((self.width, self.padding[0] + self.line_spacing + self.padding[1]))
		if self.bck_color: self.surface.set_alpha(self.bck_alpha)

		# Update self.cursor_visible
		self.cursor_ms_counter += self.clock.get_time()
		if self.cursor_ms_counter >= self.cursor_switch_ms:
			self.cursor_ms_counter %= self.cursor_switch_ms
			self.cursor_visible = not self.cursor_visible
		
		# Update self.cursor_x_pos = prompt + text_input width rounded to self.cursor_position characters
		( _ , self.cursor_rect) = self.font_object.render (self.prompt + self.input_string[:self.cursor_position], self.font_color, None) 
		# TODO - this must be moved to show function 
		#if self.cursor_visible:
		#	cursor_y_pos = _rect.width
		#	# Without this, the cursor is invisible when self.cursor_position > 0:
		#	if self.cursor_position > 0:
		#		cursor_y_pos -= self.cursor_surface.get_width()
		#	self.text_surface.blit(self.cursor_surface, (cursor_y_pos, 0))
		
		# self.surface.blit(self.text_surface, (self.padding[2], self.padding[0]))
		
		# clock must tick in order to see blinking cursor!
		self.clock.tick()
		return False

	def show(self, surf, pos=(0,0)):

		# Background
		surf.blit(self.surface, pos)
		
		# Input text
		surf.blit(self.text_surface, 
				(pos[0] + self.padding[2], 
				pos[1] + self.padding[0] + self.line_spacing - ((self.line_spacing - self.text_surface.get_height()) // 2) - self.text_surface.get_height()))
		
		# Cursor
		if self.cursor_visible:
			cursor_y_pos = self.cursor_rect.width
			# Without this, the cursor is invisible when self.cursor_position > 0:
			#if self.cursor_position > 0:
			#	cursor_y_pos -= self.cursor_surface.get_width()
			#self.text_surface.blit(self.cursor_surface, (cursor_y_pos, 0))
			surf.blit(self.cursor_surface,
					(pos[0] + self.padding[2] + cursor_y_pos, 
					pos[1] + self.padding[0] + self.line_spacing - ((self.line_spacing - self.cursor_surface.get_height()) // 2) - self.cursor_surface.get_height()))

	def get_surface(
		self):
		return self.surface

	def get_text(self):
		return self.input_string

	def get_cursor_position(self):
		return self.cursor_position

	def set_text_color(self, color):
		self.text_color = color

	def set_cursor_color(self, color):
		self.cursor_surface.fill(color)

	def clear_text(self):
		self.input_string = ""
		self.cursor_position = 0

class Console(pygame.Surface):
	''' Class implementing the game console. Console is compraised by other 
	objects such as header, footer, text input and output objects + class
	that processes the input commands
	'''

	def __init__(self,
				app, # Part of app accessible from console
				dim=(0,0),	# Console window dimensions
				config={
					'global' : {
						'layout' : 'INPUT_BOTTOM',
						'padding' : (10,10,20,20),
						'bck_color' : (125,125,125),
						'bck_image' : 'experiments/cli/bckground/quake.png',
						'bck_image_resize' : True,
						'bck_alpha' : 150,
						'welcome_msg' : 'Welcome to pyRPG\n***************\nType "exit" to quit.'
						},
					'header' : {
						'text' : 'Console v0.1. Position: {} Time: {}',
						'text_params' : ['cons_get_pos','cons_get_time'],												
						'layout' : 'TEXT_CENTRE',
						'padding' :(10,10,10,10),
						'font_file' : 'experiments/cli/fonts/IBMPlexMono-Regular.ttf',
						'font_size' : 12,
						'font_antialias' : True,
						'font_color' : (255,255,255),
						'font_bck_color' : None,
						'bck_color' : (255,0,0),
						'bck_image' : 'experiments/cli/bckground/quake.png',
						'bck_image_resize' : True,
						'bck_alpha' : 100
						},
					'output' : {
						'padding' : (10,10,10,10),
						'font_file' : 'experiments/cli/fonts/JackInput.ttf',
						'font_size' : 16,
						'font_antialias' : True,
						'font_color' : (255,255,255),
						'font_bck_color' : (55,0,0),
						'bck_color' : (55,0,0),
						'bck_alpha' : 120,
						'buffer_size' : 100,
						'prompt' : '',
						'display_lines' : 20,
						'display_columns' : 80,
						'line_spacing' : None
						},
					'input' : {
						'padding' : (10,10,10,10),
						'font_file' : 'experiments/cli/fonts/JackInput.ttf',
						'font_size' : 16,
						'font_antialias' : True,
						'font_color' : (255,0,0),
						'font_bck_color' : None,
						'bck_color' : (0,255,0),
						'bck_alpha' : 150,
						'buffer_size' : 10,
						'prompt' : '>>>',
						'max_string_length' : 70,
						'repeat_keys_initial_ms' : 400,
						'repeat_keys_interval_ms' :35
						},
					'footer' : {
						'text' : 'Copyright by pyRPG 2020',
						'text_params' : None,
						'layout' : 'TEXT_RIGHT',
						'padding' : (10,10,10,10),
						'font_file' : 'experiments/cli/fonts/IBMPlexMono-Regular.ttf',
						'font_size' : 10,
						'font_antialias' : True,
						'font_color' : (255,255,255),
						'font_bck_color' : None,
						'bck_color' : (0,0,0),
						'bck_image' : None,
						'bck_image_resize' : True,
						'bck_alpha' : 100
						}
					}):

		''' Initiates all console supporting objects - header, footer, 
		text_input and text_output.
		'''

		# Save the root object that COnsole is managing
		self.app = app
	
		# Save the params from config
		global_config = config.get('global')
		for key in global_config: setattr(self, key, global_config.get(key))

		# Initiate header object, use defaults if header params are not passed during initiation
		self.console_header = Header(self, (dim[0] - self.padding[2] - self.padding[3]), config.get('header')) if config.get('header', None) else None

		# Initiate input text object
		self.console_input = TextInput(self, (dim[0] - self.padding[2] - self.padding[3]), config.get('input')) if config.get('input', None) else None

		# Initiate output text object
		self.console_output = TextOutput(self, (dim[0] - self.padding[2] - self.padding[3]), config.get('output')) if config.get('output', None) else None

		# Initiate footer object
		self.console_footer = Header(self, dim[0] - self.padding[2] - self.padding[3], config.get('footer')) if config.get('footer', None) else None		

		# Initiace object for processing console commands - output of the class is redirected
		self.cli = CommandLineProcessor(self.app, output=self.console_output)

		# Initiate console as a Surface - calculate dimensions based on number of required output lines
		# TODO - Here I need to calculate the dimensions (height) based on required lines on the screen
		# text_output_lines

		#super().__init__(self.dim)
		#if dim[0] != 0: console_width = dim[0]
		#else: console_width = padding[2] + text_output_columns * self.console_output.get_max_width() + padding[3]

		# Correct the height dimension so that all the text rows are displayable
		self.dim = ( dim[0], self.padding[0] 
							+ (self.console_header.get_height() if self.console_header else 0)
							+ (self.console_output.get_max_height() if self.console_output else 0)
							+ (self.console_input.get_height() if self.console_input else 0)
							+ (self.console_footer.get_height() if self.console_footer else 0)
							+ self.padding[1])
		

		#self.dim = (600, console_height) 
		super().__init__(self.dim) 

		# If image is defined	
		if self.bck_image:
			self.bck_image = pygame.image.load(self.bck_image).convert()
			if self.bck_image_resize:
				self.bck_image = pygame.transform.scale(self.bck_image, (self.dim))

		# Set Console transparency
		self.set_alpha(self.bck_alpha)

		# Put the initial text on the console
		self.write(self.welcome_msg)

	def update(self, events):
		''' Generate console events
		'''
		# pass dynamic value to header
		#self.console_header.update()

		# If enter is pressed (entering command into the console)
		if self.console_input.update(events):
			# Put it into the textoutput
			self.console_output.write(self.console_input.get_text())

			# Process the entered line by CLI instance
			self.cli.onecmd(self.console_input.get_text())
			
			# Reset the text, so that new one can be entered
			self.console_input.clear_text()

		# Check if text output keys for scrolling the buffer were used
		self.console_output.update(events)

		# Update the header - in order to update the dynamic values shown in the header
		self.console_header.update()

		# Update the footer - in order to update the dynamic values shown in the footer
		self.console_footer.update()

	def show(self, surf, pos=(0, 0)):
		''' Manages bliting of console (background, textoutput, textinput)
		to the given surf surface and on given pos position.
		'''

		# Set the location of input prompt - must include header position and footer position
		if self.layout == 'INPUT_BOTTOM':
			self.header_position = (self.padding[2], self.padding[0])
			self.text_output_position = (self.padding[2], self.header_position[1] + self.console_header.get_height())
			self.text_input_position = (self.padding[2], self.text_output_position[1] + self.console_output.get_height())			
			self.footer_position = (self.padding[2], self.dim[1] - self.padding[1] - self.console_footer.get_height())

		# TODO - here implement other layouts such as INPUT_TOP etc.

		# Clear COnsole background surface		
		self.fill(self.bck_color)

		# If background image is defined, paste it to console surface
		if self.bck_image: self.blit(self.bck_image, (0, 0))

		# Blit console background to the surface
		surf.blit(self, pos)

		# Blit header onto the surface - by calling show and not blitting directly enables
		# transparent background and non transparent text displayed on it.
		self.console_header.show(
			surf,
			(pos[0] + self.header_position[0],
			pos[1] + self.header_position[1])
			)

		# Blit output onto the surface
		# Based on parameter text_input_position either on top or at the bottom of the console
		self.console_output.show(
			surf,
			(pos[0] + self.text_output_position[0],
			pos[1] + self.text_output_position[1])
			)
		
		# Blit input surface onto the surface
		# Based on parameter text_input_position either on top or at the bottom of the console
		self.console_input.show(
			surf,
			(pos[0] + self.text_input_position[0],
			pos[1] + self.text_input_position[1])
			)		

		# Blit footer onto the surface
		self.console_footer.show(
			surf,
			(pos[0] + self.footer_position[0],
			pos[1] + self.footer_position[1])
			)
	
	def write(self, text):
		''' Put some text onto a console by calling this function
		'''
		self.console_output.write(text)

		# Without calling prepare_surface the text will not be shown immediatelly
		self.console_output.prepare_surface()

	def reset(self):
		''' Method that reloads and resets the console
		'''
		pass

	def clear(self):
		''' Method that clears the output on the screen
		'''
		self.console_output.log = list()
		self.console_output.prepare_surface()

'''
	Example of the use of the Console
	For showing/hiding console press F1
'''
if __name__ == "__main__":

	from random import randint
	from datetime import datetime

	class TestObject:
		''' Testing object that will be govern by console.
		Print moving square on the screen with the console
		'''

		def __init__(self):

			pygame.init()
			self.screen = pygame.display.set_mode((800, 600))
			self.clock = pygame.time.Clock()

			self.pos = [0,0]
			self.exit = False
			self.surf = pygame.Surface((50, 50))
			self.surf.fill((255,255,255))

			self.console = Console(self, 
									# Height can be 0 because it is calculated based on font and rows
									dim=(self.screen.get_width(), 0), 
									)

			self.console_enabled = False

		def update(self):
			while not self.exit:
				
				# Reset the screen
				self.screen.fill((125, 125, 0))

				# Move the square randomly
				self.pos[0] += randint(-2,2) 
				self.pos[1] += randint(-2,2)

				# Test of puting something to the console
				#self.console.write('position X: ' + str(self.pos[0]))

				if self.pos[0] > 500: self.pos[0] = 500
				if self.pos[0] < 100: self.pos[0] = 100
				if self.pos[1] > 500: self.pos[1] = 500
				if self.pos[1] < 100: self.pos[1] = 100
				
				# Process the keys
				events = pygame.event.get()
				for event in events:
					
					# Exit on closing of the window
					if event.type == pygame.QUIT: self.exit = True
					elif event.type == pygame.KEYDOWN:
						# Escape is pressed
						if event.key == pygame.K_ESCAPE: self.exit = True
					elif event.type == pygame.KEYUP:
						# Toggle console 
						if event.key == pygame.K_F1: 
							if not self.console_enabled:
								self.console_enabled = True
								self.show_anim_console()
							else:
								self.console_enabled = False
								self.hide_anim_console()

				# Update the game situation - blit square on screen and position
				self.screen.blit(self.surf, self.pos)
				
				# Update the console if enabled
				if self.console_enabled:
					self.console.update(events)
					#self.console.convert_alpha()
					self.console.show(self.screen, (0, 0))
					#self.screen.blit(self.console, (20,300))

				pygame.display.update()
				self.clock.tick(30)

		def move(self, line):
			''' first argumet is movement on x-axis
				second argument is movement on y-axis
			''' 
			move_x, move_y = line.split(',')
			self.pos[0] += int(move_x) 
			self.pos[1] += int(move_y) 

		def show_anim_console(self):
			for anim_x in range(-self.console.get_height(), 0, 100):
				self.console.show(self.screen, (0, anim_x))
				pygame.display.update()
				self.clock.tick(30)

		def hide_anim_console(self):
			for anim_x in range(0, -self.console.get_height(), -100):
				self.console.show(self.screen, (0, anim_x))
				pygame.display.update()
				self.clock.tick(30)

		def cons_get_pos(self):
			''' Example of function that can be passed to console to show dynamic
			data in the console
			'''
			return str(self.pos)
		
		def cons_get_time(self):
			''' Example of function that can be passed to console to show dynamic
			data in the console
			'''
			return str(datetime.now())

	# Initiate testing 'game'
	t = TestObject()

	# Enter the infinite loop - press Esc to exit or type 'exit' into the console
	t.update()