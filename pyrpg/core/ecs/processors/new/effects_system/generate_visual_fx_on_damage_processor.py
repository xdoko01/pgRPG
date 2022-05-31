__all__ = ['GenerateVisualFXOnDamageProcessor']

import logging
import copy

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.position import Position
from pyrpg.core.ecs.components.new.visual_fx_on_damage import VisualFXOnDamage
from pyrpg.core.ecs.components.new.flag_was_damaged_by import FlagWasDamagedBy

# Logger init
logger = logging.getLogger(__name__)

class GenerateVisualFXOnDamageProcessor(Processor):
    ''' Creates new entity containing visual fx on the damage spot.

    Involved components:
        -   VisualFXOnDamage
        -   FlagWasDamagedBy

    Related processors:
        -   PerformDamageProcessor

    What if this processor is disabled?
        -   visual effect is not shown

    Where the processor should be planned?
        -   after PerformDamageProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = [
        'new.damage_system:PerformDamageProcessor'
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
        ''' Creates new entity containing visual fx on the damage spot.
        '''
        self.cycle += 1

        for ent, (position, flag_was_damaged_by, vfx_on_damage) in self.world.get_components(Position, FlagWasDamagedBy, VisualFXOnDamage):

            # Create new entity representing the effect
            new_entity = self.create_entity_fnc(
                {
                    "templates" : [vfx_on_damage.effect]
                },
                register=False
            )

            # Add the correct position - either the position of the effect moves dynamically together with the entity
            # or position of the effect is fixed on one place
            self.world.add_component(
                new_entity, 
                copy.copy(position) if vfx_on_damage.fixed_position else position
            )

            logger.debug(f'({self.cycle}) - Entity {ent} - has produced visual fx entity {new_entity} upon damage.')

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
