''' Module "example_game.core.components.brain" contains
Brain component implemented as a Brain class.

Use 'python -m example_game.core.components.brain -v' to run
module tests.
'''

from pyrpg.core.ecs import Component

class Brain(Component):
    ''' Entity can perform commands stored in its brain. Contains commands
    and management variables. Commands are executed on given entity and are
    in form of simple list.

    Command structure is following (tuple): (IF-Exception-Goto, CMD NAME, CMD PARAMS)

    Overview:
        - Brain processor checks the commant that is on current position and puts
        it into command queue for processing.
        - If command returns success (no exception) the index of the brain moves
        to the next command and again puts it into the queue for processing.
        - If command returns exception then the index is moved so that it is
        pointing to  IF-EXCEPTION_GOTO item in the list.
        - Those exceptions then facilitate execution of one command many times
        until it succeedes (for examle wait command) or looping in the commands
        (loop command)

    Used by:
        - BrainProcessor
        - RenderDebugProcessor

    Examples of JSON definition:
        {"type" : "Brain", "params" : {"commands" : []}}
        {"type" : "Brain", "params" : {"commands" : [
            [None, "move", {"dx" : -120}],
            [0, loop", {"iterations" : 1}]
        ]}

    Tests:
        >>> c = Brain()
        >>> c.commands
        []
        >>> c.enabled
        False
        >>> c = Brain(**{"commands" : [[None, "move", {"dx" : -120}], [0, "loop", {"iterations" : 1}]]})
        >>> c.enabled
        True
        >>> c.next_cmd_idx
        0
    '''

    __slots__ = ['commands', 'enabled', 'next_cmd_idx', 'current_cmd_idx', 'last_cmd_idx',\
                'cmd_first_call_time', 'cmd_first_call', 'loop_counter',
                'var_1', 'var_2', 'var_3', 'var_4', 'var_5']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new Brain component.

            Parameters:
                :param commands: List of commands to execute
                :type commands: list
        '''

        super().__init__()

        # Brain algorithm in form of the list
        self.commands = kwargs.get('commands', [])

        try:
            assert isinstance(self.commands, list), f'Commands must be passed as a list.'
        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError

        # Should the brain process commands (True) or not (False).
        # If there are some commands passed then enable processing
        self.enabled = True if self.commands else False

        # Idx of next command to process
        self.next_cmd_idx = 0 if self.commands else None

        # Idx of command currently in process
        self.current_cmd_idx = None

        # Idx of the last_cmd that was processed
        self.last_cmd_idx = None

        # When the current cmd unit was first invoked
        # Necessary for commands that work with time delays (cmd_wait)
        self.cmd_first_call_time = None

        # If the unit was invoked for the first time (in case repetidly called units using exception)
        self.cmd_first_call = True

        # Init the Loop counter
        # Necessary for loop commands (cmd_loop)
        self.loop_counter = 0

        # Couple of variables that can be used in the command units
        self.var_1, self.var_2, self.var_3, self.var_4, self.var_5 = None, None, None, None, None

    def process_result(self, exception):
        ''' Processes the result of processed command and moves the brain indexes
        so that those are pointing to the next command that needs to be pushed
        into the command queue.

        Overview:
            Function is called by command queue processor. Based on the result of function
            move indexes in the brain so the proper command on next_cmd_idx is executed
            on the next run of Brain processor.

        Parameters:
            :param exception: In case of successfull cmd finish returns 0
            :type exception: int

        Called from:
            engine module -> process_game_commands function
        '''

        # If the command finished succesfully - move to the next command
        if exception == 0:
            self.next_cmd_idx += 1
        else:
            # If there is return value <> 0 ... that means exception then
            # set self.next_cmd_id to the exception record

            # Find out where to skip if there is exception
            goto_on_exception = self.commands[self.current_cmd_idx][0]

            # If there is some skipping defined
            if goto_on_exception != None:
                self.next_cmd_idx = goto_on_exception
            else:
                # If the command unit does not have defined goto skip on exception
                # then continue with the next command.
                self.next_cmd_idx += 1

    def reset(self, commands=[]):
        ''' Empty and fill the brain with the new set of commands.

        Parameters:
            :param commands: List of new commands to be added into empty brain.
            :type commands: list

        Called from:
            scripts module -> modify_brain function
        '''

        # Should the brain process commands (True) or not (False).
        # If there are some commands passed then enable processing
        self.enabled = True if commands else False

        # Brain algorithm
        self.commands = commands

        # Idx of next command to process
        self.next_cmd_idx = 0 if commands else None

        # Idx of command currently in process
        self.current_cmd_idx = None

        # Idx of the last_cmd that was processed
        self.last_cmd_idx = None

        # When the current cmd unit was first invoked
        self.cmd_first_call_time = None
        self.cmd_first_call = True

        # Init the Loop counter
        self.loop_counter = 0

        # Couple of variables that can be used in the command units
        self.var_1, self.var_2, self.var_3, self.var_4, self.var_5 = None, None, None, None, None


if __name__ == '__main__':
    import doctest
    doctest.testmod()
