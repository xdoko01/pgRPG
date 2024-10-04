__all__ = ['GenerateDestroyOnNoHealthProcessor']

import logging

# Parent super-class
from pyrpg.core.ecs.esper import Processor, SkipProcessorExecution

# Used components
from core.components.flag_has_no_health import FlagHasNoHealth
from core.components.destroy_on_no_health import DestroyOnNoHealth
from core.components.is_destroyed import IsDestroyed
from core.components.brain_ai import BrainAI
from core.components.btree_ai import BTreeAI
from core.components.blist_ai import BListAI
from core.components.collidable import Collidable
from core.components.movable import Movable
from core.components.controllable import Controllable


# For creation of events
from pyrpg.core.events.event import Event 

# Logger init
logger = logging.getLogger(__name__)

class GenerateDestroyOnNoHealthProcessor(Processor):
    ''' Assigns IsDestroyed flag to the entity that has no health.

    Involved components:
        -   FlagHasNoHealth
        -   IsDestroyed
        -   Brain


    Related processors:
        -   PerformDestroyEntitiesProcessor

    What if this processor is disabled?
        -   entity is not destroyed upon no health

    Where the processor should be planned?
        -   after PerformDamageProcessor
        -   before Remove FlagHasNoHealthProcessor
    '''

    # Processors that need to be planned before this processor in order for it to work.
    PREREQ = ['allOf',
        'damage_system:PerformDamageProcessor'
    ]

    def __init__(self, add_event_fnc, *args, **kwargs):
        ''' Init the processor.
        '''
        super().__init__(*args, **kwargs)
        self.add_event_fnc = add_event_fnc

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Generates the IsDestroyed component.
        '''
        try:
            super().process(*args, **kwargs)
        except SkipProcessorExecution:
            return

        for ent, (flag_has_no_health, destroy_on_no_health) in self.world.get_components(FlagHasNoHealth, DestroyOnNoHealth):

            self.world.add_component(ent, IsDestroyed(ttl=destroy_on_no_health.ttl))

            # Generate the event
            killed_event = Event('KILLED', ent, ent, params={'killed' : ent})
            self.add_event_fnc(killed_event)

            # Kill the brain, btree, movemens and collisions on the entity, if those exist
            self.world.remove_component_force(ent, Movable)
            self.world.remove_component_force(ent, BrainAI)
            self.world.remove_component_force(ent, BListAI)
            self.world.remove_component_force(ent, BTreeAI)
            self.world.remove_component_force(ent, Collidable)
            self.world.remove_component_force(ent, Controllable)

            logger.debug(f'({self.cycle}) - Entity {ent} - flag "IsDestroyed" was added.')

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
