__all__ = ['GenerateCommandFromBTreeProcessor']

import logging
import pygame	# for pygame.time.get_ticks()

# Parent super-class
from pyrpg.core.ecs.esper import Processor

# Used components
from pyrpg.core.ecs.components.new.btree import BTree

# Logger init
logger = logging.getLogger(__name__)

class GenerateCommandFromBTreeProcessor(Processor):
    ''' Put command that is in the component's BTree Behavior
    node and that is about to be processed into the command queue.

    Involved components:
        -   BTree

    Related processors:
        -   GenerateCommandFromBrainProcessor
        -   GenerateCommandFromInputProcessor
        -   GenerateCommandFromFileProcessor
        -   PerformCommandProcessor

    What if this processor is disabled?
        -   commands stored in entity's btree are not processed

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

        for ent, (btree) in self.world.get_component(BTree):

            # If the root node is in status SUCCESS or FAILURE, do not
            # continue as the behavior has finished.
            if btree.root.is_finished(): 
                return

            # if some node is RUNNING, execute him directly
            if btree.blackboard.running_behavior.is_running():
                cmd = btree.blackboard.running_behavior.process()
                logger.debug(f'({self.cycle}) - Entity {ent} - Command "{cmd}" returned from the btree (running_behavior.process())')

            # else search for some next behavior leaf node to run and execute process function on it
            else:
                cmd = btree.root.process()
                logger.debug(f'({self.cycle}) - Entity {ent} - Command "{cmd}" returned from the btree (root.process()).')

            cmd_fnc, cmd_params = cmd

            # Put the command into the queue for processing - entity and btree can be override by the command
            # itself. It is used for global scripting functionality.
            self.add_command_fnc((cmd_fnc, {**{"entity" : ent, "brain" : btree}, **cmd_params}))
            logger.debug(f'({self.cycle}) - Entity {ent} - Command "{cmd_fnc}" with params {cmd_params} sent to the command queue - from btree.')

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
