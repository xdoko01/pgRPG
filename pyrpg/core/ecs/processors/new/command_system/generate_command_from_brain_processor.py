__all__ = ['GenerateCommandFromBrainProcessor']

import logging
import pygame	# for pygame.time.get_ticks()

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.brain import Brain

# Logger init
logger = logging.getLogger(__name__)

class GenerateCommandFromBrainProcessor(Processor):
    ''' Put command that is in the component Brain
    and that is about to be processed into the command queue.

    Involved components:
        -   Brain

    Related processors:
        -   GenerateCommandFromInputProcessor
        -   GenerateCommandFromFileProcessor
        -   PerformCommandProcessor

    What if this processor is disabled?
        -   commands stored in entity's brain are not processed

    Where the processor should be planned?
        -   after GenerateCommandFromInputProcessor
        -   before PerformCommandProcessor
    '''

    PREREQ = ['allOf',
        'new.command_system.generate_command_from_input_processor:GenerateCommandFromInputProcessor'
    ]

    def __init__(self, FNC_ADD_COMMAND):
        ''' Init the processor.

        Parameters:
            :param add_command_fnc: Reference to the function that adds command to the command queue.
            :param add_command_fnc: reference to fnc
        '''
        super().__init__()

        # Reference to function for adding to command queue
        self.add_command_fnc = FNC_ADD_COMMAND

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Puts the proper command to the command queue.
        '''
        self.cycle += 1

        for ent, (brain) in self.world.get_component(Brain):
            
            # Only continue processing if the brain is enabled
            if brain.enabled:

                # Get the command unit for processing
                try:
                    unit = brain.commands[brain.next_cmd_idx]
                except:
                    logger.debug(f'({self.cycle}) - Entity {ent} - No command found, disabling its brain.')
                    brain.enabled = False
                    return
                
                # Move pointers - next_cmd_idx is not yet decided, depends on the result of unit execution
                brain.last_cmd_idx = brain.current_cmd_idx
                brain.current_cmd_idx = brain.next_cmd_idx
                
                # Parse command unit - cmd_fnc is string
                _, cmd_fnc, cmd_params = unit

                # Put the command into the queue for processing - entity and brain can be override by the command
                # itself. It is used for global scripting functionality.
                # self.input_command_queue.append((cmd_fnc, {**{"entity" : ent, "brain" : brain}, **cmd_params}))
                self.add_command_fnc((cmd_fnc, {**{"entity" : ent, "brain" : brain}, **cmd_params}))
                logger.debug(f'({self.cycle}) - Entity {ent} - Command "{cmd_fnc}" with params {cmd_params} sent to the command queue.')

                # If the unit exist then check if it was previously called
                # remember the self.unit_first_call_time
                if brain.next_cmd_idx != brain.last_cmd_idx:
                    brain.cmd_first_call_time = pygame.time.get_ticks()
                    brain.cmd_first_call = True
                else:
                    brain.cmd_first_call = False

    def pre_save(self):
        ''' Prepare processor for serialization by disabling links to 
        non-serializable components
        '''
        pass

    def post_load(self):
        ''' Reconfigure the processor after de-serialization by attaching
        the removed references again.
        '''
        pass

    def finalize(self, *args, **kwargs):
        ''' Method called when closing the game. Put all necessary statements 
        such as closing of files/resources here, if necessary.
        '''
        pass
