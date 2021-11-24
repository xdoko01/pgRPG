__all__ = ['NewGenerateCommandFromBrainProcessor']

import logging
import pyrpg.core.ecs.esper as esper	# for esper.Processor - parent class of all processors
import pyrpg.core.ecs.components as components # for definition of components
import pygame	# for pygame.time.get_ticks()

# Logger init
logger = logging.getLogger(__name__)


class NewGenerateCommandFromBrainProcessor(esper.Processor):
    ''' Put command that is in the component Brain
    and that is about to be processed into the command queue.

    Involved components:
        -   Brain

    Related processors:
        -   NewGenerateCommandFromInputProcessor
        -   NewGenerateCommandFromFileProcessor
        -   NewPerformCommandProcessor

    What if this processor is disabled?
        -   commands stored in entity's brain are not processed

    Where the processor should be planned?
        -   after NewGenerateCommandFromInputProcessor
        -   before NewPerformCommandProcessor
    '''

    PREREQ = [
        ('new.command_system.new_generate_command_from_input_processor', 'NewGenerateCommandFromInputProcessor')
        ]

    def __init__(self, add_command_fnc):
        ''' Init the processor.

        Parameters:
            :param add_command_fnc: Reference to the function that adds command to the command queue.
            :param add_command_fnc: reference to fnc
        '''
        super().__init__()

        # Reference to function for adding to command queue
        self.add_command_fnc = add_command_fnc

    def initialize(self, register):
        '''Processor registers itself at esper ECS World'''
        register(self)

    def process(self, *args, **kwargs):
        ''' Puts the proper command to the command queue.
        '''
        self.cycle += 1

        for ent, (brain) in self.world.get_component(components.Brain):
            
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
                    #print(f'Setting up first call cmd time: {cmd_fnc}')

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
