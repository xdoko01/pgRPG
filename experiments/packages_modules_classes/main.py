''' Testing of distribution classes to the modules and to the packages '''
##########################################################
# Option 1 - Load the whole package core.ecs.processors
#	- keep the same namespace
##########################################################

from core.ecs.processors import *

if __name__ =='__main__':
	print(f'Running the test')

	collision = CollisionProcessor()
	input = InputProcessor()
	movement = MovementProcessor()
	render = RenderProcessor()

	# This method is existing in package core.ecs.processors.input_processor
	# module. But it is not part of the core.ecs.processors package because
	# it is not define in __all__ variable neither on module level nor on
	# the package level.
	
	# example_method()

	# In order to call the method anyway, the whole package/module path must
	# be defined

	import core
	core.ecs.processors.input_processor.example_method()

##########################################################
# Option 2 - Load the whole package core.ecs.processors
#	- under new namespace 'proc'
##########################################################

import core.ecs.processors as proc

if __name__ =='__main__':
	print(f'Running the test')

	collision = proc.CollisionProcessor()
	input = proc.InputProcessor()
	movement = proc.MovementProcessor()
	render = proc.RenderProcessor()

	# This method is existing in package core.ecs.processors.input_processor
	# module. But it is not part of the core.ecs.processors package because
	# it is not define in __all__ variable neither on module level nor on
	# the package level.

	# proc.example_method()

	# In order to call the method anyway, the whole package/module path must
	# be defined
	proc.input_processor.example_method()
