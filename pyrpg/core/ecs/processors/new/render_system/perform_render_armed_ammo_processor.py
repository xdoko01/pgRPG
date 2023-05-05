__all__ = ['PerformRenderArmedAmmoProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.new.ammo_pack import AmmoPack
from pyrpg.core.ecs.components.new.render_data_from_parent import RenderDataFromParent
from pyrpg.core.ecs.components.new.camera import Camera
from pyrpg.core.ecs.components.new.renderable_model import RenderableModel

# For filtering only entities with position on the cameras
from ..functions import filter_only_visible

# Logger init
logger = logging.getLogger(__name__)

class PerformRenderArmedAmmoProcessor(Processor):
    ''' Draws the armed ammo in the world.

    It draws only armed ammos that are displayable on the screen
    by using filter function.

    Input parameters:

    Involved components:
        -   RenderDataFromParent
        -   Camera
        -   RenderableModel
        -   AmmoPack

    Related processors:
        -   UpdateCameraOffsetProcessor - adjust camera position to enable scrolling effect
        -   PerformRenderModelProcessor
        -   NewPerformRenderWearablesProcessor
        -   PerformRenderArmedWeaponProcessor

    What if this processor is disabled?
        -   armed ammos will be not shown in the game
    
    Where the processor should be planned?
        -   before RenderDebugProcessor - in order not to overwrite the debug info
        -   after UpdateCameraOffsetProcessor - in order to display scrolling
        -   after RenderMapProcessor - in order to display map below the characters
        -   after NewPerformRenderWearablesProcessor - in order to properly wear clothes
        -   after PerformRenderArmedWeaponProcessor - in order to properly show ammo animation
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    __slots__ = []

    def __init__(self, *args, **kwargs):
        ''' Initiation of PerformRenderArmedWeaponProcessor processor.
        '''
        super().__init__(*args, **kwargs)

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Blit RenderableModel onto the screen.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        # For all camera screens in the game window
        for _, (camera) in self.world.get_component(Camera):

            # Blit all the Entities that have RenderDataFromParent + RenderableModel + Ammo
            for ent_ammo, (render_data, renderable, ammo_pack) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(RenderDataFromParent, RenderableModel, AmmoPack)):
                camera.screen.blit(renderable.get_current_frame(render_data.dir_name, render_data.action, render_data.last_frame), camera.apply(renderable.topleft((render_data.x, render_data.y))))

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components.
        '''
        pass

    def post_load(self):
        ''' Reconfigure the processor after de-serialization.
        '''
        pass

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass
