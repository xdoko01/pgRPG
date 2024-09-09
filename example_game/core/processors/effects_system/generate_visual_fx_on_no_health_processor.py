__all__ = ['GenerateVisualFXOnNoHealthProcessor']

import logging
import copy

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.visual_fx_on_no_health import VisualFXOnNoHealth
from pyrpg.core.ecs.components.new.flag_has_no_health import FlagHasNoHealth

# Logger init
logger = logging.getLogger(__name__)

class GenerateVisualFXOnNoHealthProcessor(Processor):
    ''' Creates new entity containing visual fx on the entity that
    has no health.

    Involved components:
        -   VisualFXOnNoHealth
        -   FlagHasNoHealth

    Related processors:
        -   PerformDamageProcessor

    What if this processor is disabled?
        -   visual effect is not shown

    Where the processor should be planned?
        -   after PerformDamageProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'new.damage_system:PerformDamageProcessor'
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
        ''' Creates new entity containing visual fx on the entity that
        has no health.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (position, flag_has_no_health, vfx_on_no_health) in self.world.get_components(Position, FlagHasNoHealth, VisualFXOnNoHealth):

            # Create new entity representing the effect
            new_entity = self.create_entity_fnc(
                {
                    "templates" : [vfx_on_no_health.effect]
                }
            )

            # Add the correct position - either the position of the effect moves dynamically together with the entity
            # or position of the effect is fixed on one place
            self.world.add_component(
                new_entity, 
                copy.copy(position) if vfx_on_no_health.fixed_position else position
            )

            logger.debug(f'({self.cycle}) - Entity {ent} - has produced visual fx entity {new_entity} upon no health.')

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
