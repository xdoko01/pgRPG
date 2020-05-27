__all__ = ['MovementProcessor']

import core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import core.ecs.components as components # for definition of components
import pygame	# for pygame.time.get_ticks()

sign = lambda x: -1 if x < 0 else (1 if x > 0 else 0)

class MovementProcessor(esper.Processor):
	''' Updates Position component (position of an entity on the map) based on Motion
	component (movement).

	Input parameters:
		-	debug
		-	stand_delay_ms

	Involved components:
		-	Position
		-	Motion

	Related processors:
		-	CommandProcessor - movement commands generate movement

	What if this processor is disabled?
		-	movements on the map will not work

	Where the processor should be planned?
		-	before CollisionXXXProcessors - collisions are processed based on final movements
		-	before RenderXXXProcessor - camera must be updated before graphics is drawn
		-	after CommandProcessor - commands generate changes in positions
	'''

	__slots__ = ['stand_delay_ms', 'debug']

	def __init__(self, stand_delay_ms=1500, debug=False):
		''' Initiation of MovementProcessor processor.

		Parameters:
			:param stand_delay_ms: How long (ms) there must be no movement until direction is reset
			:type stand_delay_ms: int

			:param debug: Tag if processor should run in debug mode
			:type debug: bool
		'''

		super().__init__()

		self.debug = debug

		# How long entity stays without movement before reseting its direction to SOUTH
		self.stand_delay_ms = stand_delay_ms

	def process(self, *args, **kwargs):
		''' Process entities having Motion and Position components. Basically,
		add motion diffs to the position represented by Position component.
		'''

		# Get the time of processing of the frame from the game main loop in seconds
		dt = kwargs.get('dt') / 1000

		for _, (position, motion) in self.world.get_components(components.Position, components.Motion):

			# Motion can be disabled/enabled from script or brain by command
			if motion.enabled:

				# If the position of the entity needs to be updated
				if (motion.dx !=0 or motion.dy !=0):

					motion.has_moved = True

					# Save last position - used for collision resolution on Map
					position.lastx = position.x
					position.lasty = position.y
					position.lastmap = position.map
					#position.lastdir = position.direction
					motion.last_move = pygame.time.get_ticks()

					# Compensate the speed of the diagonal movement - division by sqrt(2)
					if motion.dx != 0 and motion.dy != 0:
						motion.dx *= 0.7071
						motion.dy *= 0.7071

					# Update the position by the velocity. Compensate by dt
					position.x += motion.dx * dt
					position.y += motion.dy * dt

					####
					## Update the direction
					####

					# Update the direction based on motion attributes
					position.direction = (sign(motion.dx), sign(motion.dy))

					# If movement is in both axises then use NORD-SOUTH direction
					if motion.dx != 0 and motion.dy != 0:
						position.direction = (0, position.direction[1])

					# Update dir_name
					if position.direction == (1,0): position.dir_name = 'right'
					if position.direction == (-1,0): position.dir_name = 'left'
					if position.direction == (0,1): position.dir_name = 'down'
					if position.direction == (0,-1): position.dir_name = 'up'

					# Return the velocity to 0 - movement has been processed
					motion.dx = 0
					motion.dy = 0

				# No update of velocity in this cycle
				else:
					motion.has_moved = False
					# if the time from the last movement is longer than given duration, change the direction to SOUTH
					if pygame.time.get_ticks() - motion.last_move > self.stand_delay_ms:
						position.direction = (0, 1)
						position.dir_name = 'down'
