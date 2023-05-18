__all__ = ['RenderableModelAnimationUpdateProcessor']

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.original.camera import Camera
from pyrpg.core.ecs.components.original.position import Position
from pyrpg.core.ecs.components.original.renderable_model import RenderableModel

from .functions import filter_only_visible_on_camera

class RenderableModelAnimationUpdateProcessor(Processor):
    ''' Shift the animation
        - only once on every displayed entity
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return
        # Remember updated entities - to prevent several updates on simgle entity
        already_updated = set()

        # Iterate all camaeras
        for cam, (camera) in self.world.get_component(Camera):
            
            # Get RenderableModels with Positions
            for ent, (position, renderable_model) in filter(lambda x: filter_only_visible_on_camera(camera, x), self.world.get_components(Position, RenderableModel)):
    
                # Call the update_frame function
                if ent not in already_updated:
                    renderable_model.update_frame(position.dir_name)

                # Remember that entity was updated
                already_updated.add(ent)
