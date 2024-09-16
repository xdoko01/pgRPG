__all__ = ['GenerateVisualFXOnGenerationProcessor']

import logging
import copy

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.render_data_from_parent import RenderDataFromParent
from core.components.visual_fx_on_generation import VisualFXOnGeneration
from core.components.flag_create_from_factory import FlagCreateFromFactory

# Logger init
logger = logging.getLogger(__name__)

class GenerateVisualFXOnGenerationProcessor(Processor):
    ''' Creates new entity containing visual fx on the generation spot.

    Involved components:
        -   VisualFXOnGeneration
        -   FlagCreateFromFactory

    Related processors:
        -   PerformFactoryGenerationProcessor

    What if this processor is disabled?
        -   visual effect is not shown

    Where the processor should be planned?
        -   after PerformFactoryGenerationProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'new.factory_system:PerformFactoryGenerationProcessor'
    ]

    __slots__ = ['create_entity_fnc']

    def __init__(self, create_entity_fnc, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)
        self.create_entity_fnc = create_entity_fnc

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Creates new entity containing visual fx on the generation spot.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (render_data_from_parent, flag_create_from_factory, vfx_on_generation) in self.world.get_components(RenderDataFromParent, FlagCreateFromFactory, VisualFXOnGeneration):

            # Create new entity representing the effect
            new_entity = self.create_entity_fnc(
                {
                    "templates" : [vfx_on_generation.effect]
                }
            )

            # Add the correct position - either the position of the effect moves dynamically together with the entity
            # or position of the effect is fixed on one place
            self.world.add_component(
                new_entity, 
                copy.copy(render_data_from_parent.parent_pos_comp) if vfx_on_generation.fixed_position else render_data_from_parent.parent_pos_comp
            )

            logger.debug(f'({self.cycle}) - Entity {ent} - has produced visual fx entity {new_entity} upon generation.')

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to
        non-serializable components
        '''
        pass

    def post_load(self, window):
        ''' Reconfigure the processor after de-serialization by attaching
        the lost reference again
        '''
        pass

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass
