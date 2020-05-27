#####################################################################
## Package init
#####################################################################

print(f'Processors init')

#####################################################################
## Package imports
#####################################################################

# Load all processor modules
from .input_processor import *
from .collision_processor import *
from .movement_processor import *
from .render_processor import *

# Make only following modules visible in the  package
__all__ = [
	'InputProcessor',
	'CollisionProcessor',
	'MovementProcessor',
	'RenderProcessor'
	]

