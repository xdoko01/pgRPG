__all__ = ['GenerateVisualFXOnCreationProcessor']

import logging
import copy

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.visual_fx_on_creation import VisualFXOnCreation
from pyrpg.core.ecs.components.new.flag_generated_from_factory import FlagGeneratedFromFactory

# Logger init
logger = logging.getLogger(__name__)

class GenerateVisualFXOnCreationProcessor(Processor):
    ''' Creates new entity containing visual fx on the creation spot.

    Involved components:
        -   VisualFXOnCreation
        -   FlagGeneratedFromFactory

    Related processors:
        -   PerformFactoryGenerationProcessor

    What if this processor is disabled?
        -   visual effect is not shown

    Where the processor should be planned?
        -   after PerformFactoryGenerationProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.factory_system:PerformFactoryGenerationProcessor'
    ]

    __slots__ = ['create_entity_fnc']

    def __init__(self, create_entity_fnc):
        ''' Init the processor.
        '''
        super().__init__()
        self.create_entity_fnc = create_entity_fnc

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Creates new entity containing visual fx on the creation spot.
        '''
        self.cycle += 1

        for ent, (position, flag_generated_from_factory, vfx_on_creation) in self.world.get_components(Position, FlagGeneratedFromFactory, VisualFXOnCreation):

            # Create new entity representing the effect
            new_entity = self.create_entity_fnc(
                {
                    "templates" : [vfx_on_creation.effect]
                },
                register=False
            )

            # Add the correct position - either the position of the effect moves dynamically together with the entity
            # or position of the effect is fixed on one place
            self.world.add_component(
                new_entity, 
                copy.copy(position) if vfx_on_creation.fixed_position else position
            )

            logger.debug(f'({self.cycle}) - Entity {ent} - has produced visual fx entity {new_entity} upon creation.')

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
