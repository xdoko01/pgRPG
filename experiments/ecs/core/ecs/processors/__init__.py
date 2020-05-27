#####################################################################
## Package core.ecs.processors
#####################################################################


# Load all processor modules
from .generate_projectile_processor import *
from .clear_temporary_entity_processor import *
from .renderable_model_animation_action_processor import *
from .renderable_model_animation_update_processor import *
from .render_model_world_processor import *
from .update_camera_offset_processor import *
from .movement_processor import *
from .render_map_processor import *
from .render_debug_processor import *
from .render_background_processor import *
from .input_processor import *
from .collision_map_processor import *
from .collision_entity_generator_processor import *
from .collision_teleport_processor import *
from .collision_damage_processor import *
from .collision_weapon_processor import *
from .collision_wearable_processor import *
from .collision_item_processor import *
from .collision_entity_processor import *
from .brain_processor import *
from .game_events_processor import *
from .command_processor import *

# Not used
#from .render_map_processor_full_scan import *
#from .render_model_world_processor_different_frames_on_cameras import *
#from .render_model_world_processor_full_scan import *
#from .collision_map_processor_full_scan import *
#from .collision_entity_generator_processor_full_scan import *
#from .collision_corrector_processor import *
#from .render_debug_processor_full_scan import *

from .render_world_processor import *
from .functions import *


# Make only following modules visible in the  package
__all__ = [
	'GenerateProjectileProcessor',
	'ClearTemporaryEntityProcessor',
	'RenderableModelAnimationActionProcessor',
	'RenderableModelAnimationUpdateProcessor',
	'RenderModelWorldProcessor',
	'UpdateCameraOffsetProcessor',
	'MovementProcessor',
	'RenderMapProcessor',
	'RenderDebugProcessor',
	'RenderBackgroundProcessor',
	'InputProcessor',
	'CollisionMapProcessor',
	'CollisionEntityGeneratorProcessor',
	'CollisionTeleportProcessor',
	'CollisionDamageProcessor',
	'CollisionWeaponProcessor',
	'CollisionWearableProcessor',
	'CollisionItemProcessor',
	'CollisionEntityProcessor',
	'BrainProcessor',
	'GameEventsProcessor',
	'CommandProcessor',
	'RenderModelWorldProcessor',

	# Not used

	#'RenderMapProcessorFullScan',
	#'RenderModelWorldProcessorDifferentFramesOnCameras',
	#'RenderModelWorldProcessorFullScan',
	#'CollisiCollisionMapProcessorFullScan',
	#'CollisionEntityGeneratorProcessorFullScan',
	#'CollisionCorrectorProcessor',
	#'RenderDebugProcessorFullScan',
	
	'filter_only_visible'
	]
