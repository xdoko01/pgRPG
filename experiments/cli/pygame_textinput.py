"""
Copyright 2017, Silas Gyger, silasgyger@gmail.com, All rights reserved.
Borrowed from https://github.com/Nearoo/pygame-text-input under the MIT license.

Original above modified in the following way:
	- color input parameters changed to RGB
	- added font_file parameter/ removed font_family parameter
	- added buffer parameter
"""

import pygame
import pygame.locals as pl

pygame.font.init()


class TextInput:
	"""
	This class lets the user input a piece of text, e.g. a name or a message.
	This class let's the user input a short, one-lines piece of text at a blinking cursor
	that can be moved using the arrow-keys. Delete, home and end work as well.
	"""
	def __init__(
			self,
			width,
			config={
				'padding' : (0,0,0,0),
				'font_file' : 'experiments/cli/fonts/IBMPlexMono-Regular.ttf',
				'font_size' : 16,
				'font_antialias' : True,
				'font_color' : (255,0,0),
				'font_bck_color' : None,
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

		#if not os.path.isfile(font_family):
		#    font_family = pygame.font.match_font(font_family)

		#self.font_object = pygame.font.Font(font_family, font_size)

		# Text-surface will be created during the first update call:
		self.surface = pygame.Surface((0, 0), pygame.SRCALPHA)

		# Vars to make keydowns repeat after user pressed a key for some time:
		self.keyrepeat_counters = {}  # {event.key: (counter_int, event.unicode)} (look for "***")
		'''
		self.keyrepeat_intial_interval_ms = repeat_keys_initial_ms
		self.keyrepeat_interval_ms = repeat_keys_interval_ms
		'''

		# Things cursor:
		#self.cursor_surface = pygame.Surface((int(self.font_size / 20 + 1), self.font_size))
		self.cursor_surface = pygame.Surface((int(self.font_size), self.font_size*2))
		self.cursor_surface.fill(self.font_color)
		self.cursor_position = len(self.prompt)  # Inside text
		self.cursor_visible = True  # Switches every self.cursor_switch_ms ms
		self.cursor_switch_ms = 500  # /|\
		self.cursor_ms_counter = 0
		self.clock = pygame.time.Clock()

	def get_height(self):
		return self.surface.get_height()

	def update(self, events):
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

				elif event.key == pl.K_LEFT:
					# Subtract one from cursor_pos, but do not go below zero:
					self.cursor_position = max(self.cursor_position - 1, 0)

				elif event.key == pl.K_END:
					self.cursor_position = len(self.input_string)

				elif event.key == pl.K_HOME:
					self.cursor_position = 0

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

				# Scroll the buffer - to the future
				elif event.key == pl.K_DOWN:
					# Calc new buffer position
					if self.buffer_position < len(self.buffer) - 1:
						self.buffer_position = self.buffer_position + 1
						# restore previous input string - last in buffer
						self.input_string = self.buffer[self.buffer_position]
						# set cursor possition at the end of the string
						self.cursor_position = len(self.input_string)
		
				elif len(self.input_string) < self.max_string_length or self.max_string_length == -1:
					# If no special key is pressed, add unicode of key to input_string
					self.input_string = (
						self.input_string[:self.cursor_position]
						+ event.unicode
						+ self.input_string[self.cursor_position:]
					)
					self.cursor_position += len(event.unicode)  # Some are empty, e.g. K_UP

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
		(self.surface, _rect)  = self.font_object.render(self.prompt + self.input_string, self.font_color, None)

		# Update self.cursor_visible
		self.cursor_ms_counter += self.clock.get_time()
		if self.cursor_ms_counter >= self.cursor_switch_ms:
			self.cursor_ms_counter %= self.cursor_switch_ms
			self.cursor_visible = not self.cursor_visible
		
		if self.cursor_visible:
			cursor_y_pos = _rect.width
			# Without this, the cursor is invisible when self.cursor_position > 0:
			if self.cursor_position > 0:
				cursor_y_pos -= self.cursor_surface.get_width()
			self.surface.blit(self.cursor_surface, (cursor_y_pos, 0))
		
		self.clock.tick()
		return False

	def get_surface(self):
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

if __name__ == "__main__":
	pygame.init()

	# Create TextInput-object
	textinput = TextInput()

	screen = pygame.display.set_mode((1000, 200))
	clock = pygame.time.Clock()

	while True:
		screen.fill((225, 225, 225))

		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				exit()

		# Feed it with events every frame
		# If Enter is pressed
		if textinput.update(events):
			#print the text on the console
			textinput.read(textinput.get_text())
			# reset the text
			textinput.clear_text()

		# Blit its surface onto the screen
		screen.blit(textinput.get_surface(), (10, 10))

		pygame.display.update()
		clock.tick(30)