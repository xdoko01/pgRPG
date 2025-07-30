''' Module "example_game.core.components.controllable" contains
Controllable component implemented as a Controllable class.

Use 'python -m example_game.core.components.controllable -v' to run
module tests.
'''
import logging

# Create logger
logger = logging.getLogger(__name__)

from pyrpg.core.config import KEYS # for K_PROFILE # Dictionary holding all keybord schemas for manipulation of characters
from pyrpg.core.ecs import Component
from pyrpg.core.commands import cmd_factory

class Controllable(Component):
    ''' Entity can be controlled by the keyboard commands.

    Used by:
        - NewInputProcessor

    Examples of JSON definition:
        {"type" : "Controllable", "params" :  {"key_profile" : "key_controls_1"}}
        {"type" : "Controllable", "params" :  {
            "key_profile" : "key_controls_1",
            "control_keys" : {'left' : 276, 'right': 275, 'up' : 273, 'down' : 274, 'attack' : 122},
            "control_cmds" : {
                'left' : [('move', {'direction' : 'left'})],
                'right': [('move', {'direction' : 'right'})],
                'up' : [('move', {'direction' : 'up'})],
                'down' : [('move', {'direction' : 'down'})],
                'attack' : [('attack', {})]}
            }
        }

    Tests:
        >>> c = Controllable(**{"key_profile" : "key_controls_1",\
            "control_keys" : {'left' : 276, 'right': 275, 'up' : 273, 'down' : 274, 'attack' : 122},\
            "control_cmds" : {\
                'left' : [('new_move', {'direction' : 'left'})],\
                'right': [('new_move', {'direction' : 'right'})],\
                'up' : [('new_move', {'direction' : 'up'})],\
                'down' : [('new_move', {'direction' : 'down'})],\
                'attack' : [('new_attack', {})]}\
            }\
            )
    '''

    __slots__ = ['control_keys', 'backup_control_cmds', 'control_cmds', 'key_feedback', 'backup_key_feedback']

    def __init__(self, *args, **kwargs):
        ''' Initiate values for the new Controllable component.

        Parameters:
            :param key_profile: Profile stored in configuration
                that is describing keys and linked commands (optional)
            :type key_profile: str

            :param control_keys: Dictionary containing mapping
                of movement and action keys to keyboard keys (optional)
            :type control_keys: dict

            :param control_cmds: Dictionary containing mapping
                of movement and action keys to commands (optional)
            :type control_cmds: dict

            :raise: ValueError - in case of incorrect keys/commands definition
        '''
        super().__init__()

        # Possibility to disable input for the global processor
        self.backup_control_cmds = None

        # Get keyboard key scheme for players based on configuration
        # Use 'default' if no scheme is passed
        key_profile = kwargs.get("key_profile", "DEFAULT")

        # Control keys definition - keyboard arrows + 'z' key for attack
        control_keys = kwargs.get("control_keys", {})

        # Control commands definition
        default_cmds = {
            'LEFT' : [('move_dir', {'moves' : ['left']})],
            'RIGHT': [('move_dir', {'moves' : ['right']})],
            'UP' : [('move_dir', {'moves' : ['up']})],
            'DOWN' : [('move_dir', {'moves' : ['down']})],
            'ATTACK' : [('attack', {})]
        }

        control_cmds = kwargs.get("control_cmds", default_cmds)

        try:
            assert key_profile in KEYS["K_PROFILE"].keys(), f'Key scheme "{key_profile}" is not defined in the config.'
            assert isinstance(control_keys, dict), f'Control keys must be passed in a form of dictionary.'
            assert isinstance(control_cmds, dict), f'Control cmds must be passed in a form of dictionary.'

            # Does control_cmds dictionary contain at least one valid command key?
            assert bool(set(default_cmds.keys()).intersection(set(control_cmds.keys()))), f'Control commands are not properly defined'

        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError

        # Load key scheme if passed as an argument else load default scheme
        self.control_keys = KEYS["K_PROFILE"][key_profile]

        # If additionally specific keys are passed, override the configuration with those keys
        self.control_keys = {**self.control_keys, **control_keys}

        # Merge defaults with defined commands
        self.control_cmds = {**default_cmds, **control_cmds}

        # Key feedback
        self.backup_key_feedback = None

        default_key_feedback = KEYS["KEY_FEEDBACK"]
        key_feedback = kwargs.get("key_feedback", {})
        self.key_feedback = {**default_key_feedback, **key_feedback}
        # Assert that for every control command exists a key feedback definition
        assert set(self.control_cmds.keys()) == set(self.key_feedback.keys())

        # Transform commands in form of a list/tuple to Command nametuples
        self._prep_commands()

        logger.debug(f'Controls and assigned commands are following: {self.control_cmds=}, {self.key_feedback=}')

    def _prep_commands(self) -> None:
        '''Transform JSON representation of the command to Command class form.
        '''
        for key, commands in self.control_cmds.copy().items():
            for cmd_idx in range(len(commands if commands else [])):
                logger.debug(f'Command in orig form: {self.control_cmds[key][cmd_idx]}')
                self.control_cmds[key][cmd_idx] = cmd_factory(self.control_cmds[key][cmd_idx])
                logger.debug(f'Command after transformation: {self.control_cmds[key][cmd_idx]}')


    def disable_input(self, control_keys: list=None) -> None:
        ''' Backup the input commands and substitute them with none command

            :param control_keys: List of control key names to be disabled. The rest will stay enabled.
                                 If None, all control keys are disabled.
            :type control_keys: list
        '''
        # Backup the configuration prior to change to recover if needed
        self.backup_control_cmds = self.control_cmds.copy()

        # Disable all keys if list of keys not specified as a parameter
        control_keys = list(self.control_cmds.keys()) if control_keys is None else control_keys
        
        # Assign empty command list to the keys that should stop to work
        for key in control_keys: self.control_cmds[key] = []


    def restore_input(self, control_keys: list=None) -> None:
        ''' Restore the input commands from backup

            :param control_keys: List of control key names to be re-enabled. The rest will stay enabled.
                                 If None, all control keys are re-enabled.
            :type control_keys: list

            Tests:
                >>> c = Controllable(**{"key_profile" : "key_controls_1",\
                "control_keys" : {'left' : 276, 'right': 275, 'up' : 273, 'down' : 274, 'attack' : 122},\
                "control_cmds" : {\
                    'left' : [('new_move', {'direction' : 'left'})],\
                    'right': [('new_move', {'direction' : 'right'})],\
                    'up' : [('new_move', {'direction' : 'up'})],\
                    'down' : [('new_move', {'direction' : 'down'})],\
                    'attack' : [('new_attack', {})]}\
                }\
                )
                >>> c.disable_input()
                >>> c.control_cmds['left']
                []
                >>> c.restore_input()
                >>> c.control_cmds['left']
                [('new_move', {'direction' : 'left'})]
        '''
        # If there is nothing to restore, end with error
        if self.backup_control_cmds is None: raise ValueError(f'No backup of control key commands was done. Nothing to restore from.')

        # Re-enable all keys if list of keys not specified as a parameter
        control_keys = list(self.control_cmds.keys()) if control_keys is None else control_keys

        # Assign the original backuped commands to the keys
        for key in control_keys: 
            self.control_cmds[key] = self.backup_control_cmds[key]

        # Set the backup back to None to indicate that it was already restored
        self.backup_control_cmds = None

    def set_control_cmds(self, control_cmds: dict) -> None:
        '''Swith between current control commands and the controll commands specified in the parameter.
        '''
        # Backup the configuration prior to change to recover if needed
        self.backup_control_cmds = self.control_cmds.copy()

        # Assign new commands - iterate the adjust dictionary and update only those that need to be adjusted
        for key, cmds in control_cmds.items():
            self.control_cmds[key] = cmds

        # Transform new commands to the proper command form
        self._prep_commands()

    def restore_control_cmds(self) -> None:
        '''Restore back control commands.
        '''
        # If there is nothing to restore, end with error
        if self.backup_control_cmds is None: raise ValueError(f'No backup of control commands was done. Nothing to restore from.')

        # Restore the control commands from the backup
        self.control_cmds = self.backup_control_cmds

        # Set the backup back to None to indicate that it was already restored
        self.backup_control_cmds = None

    def set_key_feedback(self, key_feedback: dict) -> None:
        '''Swith between current key feedback mode and the key feedback mode specified in the parameter.
        '''
        # Backup the configuration prior to change to recover if needed
        self.backup_key_feedback = self.key_feedback.copy()

        # Assign new commands - iterate the adjust dictionary and update only those that need to be adjusted
        for cmd, feedback_mode in key_feedback.items():
            self.key_feedback[cmd] = feedback_mode

    def restore_key_feedback(self) -> None:
        '''Restore back key feedback mode.
        '''
        # If there is nothing to restore, end with error
        if self.backup_key_feedback is None: raise ValueError(f'No backup of key feedback mode was done. Nothing to restore from.')

        # Restore the key feedback from the backup
        self.key_feedback = self.backup_key_feedback

        # Set the backup back to None to indicate that it was already restored
        self.backup_key_feedback = None


if __name__ == '__main__':
    import doctest
    doctest.testmod()
