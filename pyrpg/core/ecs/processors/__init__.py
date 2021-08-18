#####################################################################
## Package core.ecs.processors
#####################################################################


# Load all processor modules
from .remove_depleted_ammo_pack_processor import *
from .disarm_depleted_ammo_pack_processor import *
from .generate_projectile_processor import *
from .clear_temporary_entity_processor import *
from .renderable_model_animation_action_processor import *
from .renderable_model_animation_update_processor import *
from .render_model_world_processor import *
from .render_talk_processor import *
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
from .collision_ammo_pack_processor import *
from .collision_wearable_processor import *
from .collision_item_processor import *
from .collision_entity_processor import *
from .collision_deletion_processor import *
from .brain_processor import *
from .game_events_processor import *
from .command_processor import *
from .game_messages_processor import *
from .calculate_score_processor import *
from .remove_flag_add_score_processor import *
from .calculate_damage_processor import *
from .remove_flag_add_damage_processor import *
from .handle_destroyed_entities_processor import *
from .remove_flag_no_health_processor import *
from .generate_score_damage_processor import *
from .generate_score_destroy_processor import *
from .debug_processor import *

###
# NEW COMMAND SYSTEM
###
from .command_system import *

###
# New MOVEMENT SYSTEM
###
from .movement_system import *

###
# New ANIMATION SYSTEM
###
from .animation_system import *

###
# New COLLISION SYSTEM
###
from .collision_system import *

###
# New PICKUP SYSTEM
###
from .pickup_system import *


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
    'DisarmDepletedAmmoPackProcessor',
    'RemoveDepletedAmmoPackProcessor',

    'PrepareProjectileProcessor',
    'CreateEntityOnPositionProcessor',

    'GenerateProjectileProcessor',
    'ClearTemporaryEntityProcessor',
    'RenderableModelAnimationActionProcessor',
    'RenderableModelAnimationUpdateProcessor',
    'RenderModelWorldProcessor',
    'RenderTalkProcessor',
    'RenderTalkProcessor2',
    'UpdateCameraOffsetProcessor',

    'LinearMovementProcessor',	
    'MovementProcessor',

    'RenderMapProcessor',
    'RenderDebugProcessor',
    'RenderWorldProcessor',
    'RenderBackgroundProcessor',
    'RenderCameraBackgroundProcessor',
    'InputProcessor',
    'CollisionMapProcessor',
    'CollisionEntityGeneratorProcessor',
    'CollisionTeleportProcessor',
    'CollisionDamageProcessor',
    'CollisionWeaponProcessor',
    'CollisionAmmoPackProcessor',
    'CollisionWearableProcessor',
    'CollisionItemProcessor',
    'CollisionEntityProcessor',
    'CollisionDeletionProcessor',
    'BrainProcessor',
    'GameEventsProcessor',
    'GameEventsExProcessor',
    'CommandProcessor',
    'RenderModelWorldProcessor',
    'GameMessagesProcessor',
    'CalculateScoreProcessor',
    'RemoveFlagAddScoreProcessor',
    'CalculateDamageProcessor',
    'RemoveFlagAddDamageProcessor',
    'HandleDestroyedEntitiesProcessor',
    'RemoveFlagNoHealthProcessor',
    'GenerateScoreDamageProcessor',
    'GenerateScoreDestroyProcessor',
    'DebugProcessor',

    ###
    # NEW COMMAND SYSTEM
    ###
    'NewGenerateCommandFromInputProcessor',
    'NewGenerateCommandFromBrainProcessor',
    'NewPerformCommandProcessor',
    'NewRecordCommandToFileProcessor',
    'NewGenerateCommandFromFileProcessor',

    ###
    # New MOVEMENT SYSTEM
    ###
    'NewPerformMovementProcessor',
    'NewRemoveFlagDoMoveProcessor',

    ###
    # New ANIMATION SYSTEM
    ###
    'NewPerformIdleAnimationProcessor',
    'NewPerformMovementAnimationProcessor',
    'NewPerformFrameUpdateProcessor'

    ###
    # New COLLISION SYSTEM
    ###
    'NewGenerateEntityCollisionsProcessor',
    'NewResolveMapCollisionsProcessor',
    'NewResolveEntityCollisionsProcessor',
    'NewResolveEntityCollisionsExProcessor',
    'NewRemoveFlagHasCollidedProcessor',

    ###
    # New PICKUP SYSTEM
    ###
    'NewGeneratePickupProcessor',
    'NewPerformPickupProcessor',
    'NewRemoveFlagIsAboutToPickEntityProcessor',
    'NewRemoveFlagWasPickedByProcessor',
    'NewRemoveFlagHasPickedProcessor',

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

PROC_DICT = {
    'DisarmDepletedAmmoPackProcessor' : DisarmDepletedAmmoPackProcessor,
    'RemoveDepletedAmmoPackProcessor' : RemoveDepletedAmmoPackProcessor,
    'PrepareProjectileProcessor' : PrepareProjectileProcessor,
    'CreateEntityOnPositionProcessor' : CreateEntityOnPositionProcessor,
    'GenerateProjectileProcessor' : GenerateProjectileProcessor,
    'ClearTemporaryEntityProcessor' : ClearTemporaryEntityProcessor,
    'RenderableModelAnimationActionProcessor' : RenderableModelAnimationActionProcessor,
    'RenderableModelAnimationUpdateProcessor' : RenderableModelAnimationUpdateProcessor,
    'RenderModelWorldProcessor' : RenderModelWorldProcessor,
    'RenderWorldProcessor' : RenderWorldProcessor,
    'RenderTalkProcessor' : RenderTalkProcessor,
    'RenderTalkProcessor2' : RenderTalkProcessor2,
    'UpdateCameraOffsetProcessor' : UpdateCameraOffsetProcessor,
    'LinearMovementProcessor' : LinearMovementProcessor,
    'MovementProcessor' : MovementProcessor,
    'RenderMapProcessor' : RenderMapProcessor,
    'RenderDebugProcessor' : RenderDebugProcessor,
    'RenderBackgroundProcessor' : RenderBackgroundProcessor,
    'RenderCameraBackgroundProcessor' : RenderCameraBackgroundProcessor,
    'InputProcessor' : InputProcessor,
    'CollisionMapProcessor' : CollisionMapProcessor,
    'CollisionEntityGeneratorProcessor' : CollisionEntityGeneratorProcessor,
    'CollisionTeleportProcessor' : CollisionTeleportProcessor,
    'CollisionDamageProcessor' : CollisionDamageProcessor,
    'CollisionWeaponProcessor' : CollisionWeaponProcessor,
    'CollisionAmmoPackProcessor' : CollisionAmmoPackProcessor,
    'CollisionWearableProcessor' : CollisionWearableProcessor,
    'CollisionItemProcessor' : CollisionItemProcessor,
    'CollisionEntityProcessor' : CollisionEntityProcessor,
    'CollisionDeletionProcessor' : CollisionDeletionProcessor,
    'BrainProcessor' : BrainProcessor,
    'GameEventsProcessor' : GameEventsProcessor,
    'GameEventsExProcessor' : GameEventsExProcessor,
    'QuestEventsExProcessor' : GameEventsExProcessor, # same as above
    'CommandProcessor' : CommandProcessor,
    'RenderModelWorldProcessor' : RenderModelWorldProcessor,
    'GameMessagesProcessor' : GameMessagesProcessor,
    'CalculateScoreProcessor' : CalculateScoreProcessor,
    'RemoveFlagAddScoreProcessor' : RemoveFlagAddScoreProcessor,
    'CalculateDamageProcessor' : CalculateDamageProcessor,
    'RemoveFlagAddDamageProcessor' : RemoveFlagAddDamageProcessor,
    'HandleDestroyedEntitiesProcessor' : HandleDestroyedEntitiesProcessor,
    'RemoveFlagNoHealthProcessor' : RemoveFlagNoHealthProcessor,
    'GenerateScoreDamageProcessor' : GenerateScoreDamageProcessor,
    'GenerateScoreDestroyProcessor' : GenerateScoreDestroyProcessor,
    'DebugProcessor' : DebugProcessor,

    ###
    # NEW COMMAND SYSTEM
    ###
    'NewGenerateCommandFromInputProcessor' : NewGenerateCommandFromInputProcessor,
    'NewGenerateCommandFromBrainProcessor' : NewGenerateCommandFromBrainProcessor,
    'NewPerformCommandProcessor' : NewPerformCommandProcessor,
    'NewRecordCommandToFileProcessor' : NewRecordCommandToFileProcessor,
    'NewGenerateCommandFromFileProcessor' : NewGenerateCommandFromFileProcessor,

    ###
    # New MOVEMENT SYSTEM
    ###
    'NewPerformMovementProcessor' : NewPerformMovementProcessor,
    'NewRemoveFlagDoMoveProcessor' : NewRemoveFlagDoMoveProcessor,

    ###
    # New ANIMATION SYSTEM
    ###
    'NewPerformIdleAnimationProcessor' : NewPerformIdleAnimationProcessor,
    'NewPerformMovementAnimationProcessor' : NewPerformMovementAnimationProcessor,
    'NewPerformFrameUpdateProcessor' : NewPerformFrameUpdateProcessor,

    ###
    # New COLLISION SYSTEM
    ###
    'NewGenerateEntityCollisionsProcessor' : NewGenerateEntityCollisionsProcessor,
    'NewResolveMapCollisionsProcessor' : NewResolveMapCollisionsProcessor,
    'NewResolveEntityCollisionsProcessor' : NewResolveEntityCollisionsProcessor,
    'NewResolveEntityCollisionsExProcessor' : NewResolveEntityCollisionsExProcessor,
    'NewRemoveFlagHasCollidedProcessor' : NewRemoveFlagHasCollidedProcessor,

    ###
    # New PICK-UP SYSTEM
    ###
    'NewGeneratePickupProcessor' : NewGeneratePickupProcessor,
    'NewPerformPickupProcessor' : NewPerformPickupProcessor,
    'NewRemoveFlagIsAboutToPickEntityProcessor' : NewRemoveFlagIsAboutToPickEntityProcessor,
    'NewRemoveFlagWasPickedByProcessor' : NewRemoveFlagWasPickedByProcessor,
    'NewRemoveFlagHasPickedProcessor' : NewRemoveFlagHasPickedProcessor
}

def get_processor(proc_str):
    ''' Returns tuple - the class implementing processor that is represented by the string
    and the list of init parameters.
    In case the class string is not recognized, returns None
    '''
    try:
        proc_class = PROC_DICT.get(proc_str)
        assert proc_class is not None, f'Processor class "{proc_str}" not found.'
        
        proc_attrs = proc_class.__init__.__code__.co_varnames[1:]
        return (proc_class, proc_attrs)
    except AssertionError:
        raise ValueError