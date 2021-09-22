__all__ = ['NewPerformRenderArmedWeaponProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components

from ..functions import filter_only_visible # for filtering only entities with position on the cameras

# Logger init
logger = logging.getLogger(__name__)

class NewPerformRenderArmedWeaponProcessor(esper.Processor):
    ''' Draws the armed weapon in the world.

    It draws only armed weapons that are displayable on the screen
    by using filter function.
    
    Input parameters:

    Involved components:
        -   NewRenderDataFromParent
        -   Camera
        -   RenderableModel

    Related processors:
        -   UpdateCameraOffsetProcessor - adjust camera position to enable scrolling effect
        -   NewPerformRenderModelProcessor
        -   NewPerformRenderWearablesProcessor

    What if this processor is disabled?
        -   armed weapons will be not shown in the game
    
    Where the processor should be planned?
        -   before RenderDebugProcessor - in order not to overwrite the debug info
        -   after UpdateCameraOffsetProcessor - in order to display scrolling
        -   after RenderMapProcessor - in order to display map below the characters
        -   after NewPerformRenderWearablesProcessor - in order to properly wear clothes
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = []

    __slots__ = []

    def __init__(self):
        ''' Initiation of NewPerformRenderArmedWeaponProcessor processor.
        '''
        super().__init__()


    def process(self, *args, **kwargs):
        ''' Blit RenderableModel onto the screen.
        '''
        self.cycle += 1

        # For all camera screens in the game window
        for _, (camera) in self.world.get_component(components.Camera):

            # Blit all the Entities that have NewRenderDataFromParent + RenderableModel + Weapon
            for ent_weapon, (render_data, renderable, weapon) in filter(lambda x: filter_only_visible(camera, x), self.world.get_components(components.NewRenderDataFromParent, components.RenderableModel, components.Weapon)):

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
