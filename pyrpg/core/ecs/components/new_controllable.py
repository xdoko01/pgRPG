''' Module "pyrpg.core.ecs.components.new_controllable" contains
NewControllable component implemented as a NewControllable class.

Use 'python -m pyrpg.core.ecs.components.new_controllable -v' to run
module tests.
'''

from pyrpg.core.config.keys import K_PROFILE # Dictionary holding all keybord schemas for manipulation of characters
from .component import Component

class NewControllable(Component):
    ''' Entity can be controlled by the keyboard commands.

    Used by:
        - NewInputProcessor

    Examples of JSON definition:
        {"type" : "NewControllable", "params" :  {"key_profile" : "key_controls_1"}}
        {"type" : "NewControllable", "params" :  {
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
        >>> c = NewControllable(**{"key_profile" : "key_controls_1",\
            "control_keys" : {'left' : 276, 'right': 275, 'up' : 273, 'down' : 274, 'attack' : 122},\
            "control_cmds" : {\
                'left' : [('new_move', {'direction' : 'left'})],\
                'right': [('new_move', {'direction' : 'right'})],\
                'up' : [('new_move', {'direction' : 'up'})],\
                'down' : [('new_move', {'direction' : 'down'})],\
                'attack' : [('new_attack', {})]}\
            }\
            })
    '''

    __slots__ = ['control_keys', 'backup_control_cmds', 'control_cmds']

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
        key_profile = kwargs.get("key_profile", "default")

        # Control keys definition - keyboard arrows + 'z' key for attack
        #default_keys = {'left' : 276, 'right': 275, 'up' : 273, 'down' : 274, 'attack' : 122}
        control_keys = kwargs.get("control_keys", {})

        # Control commands definition
        default_cmds = {
            'left' : [('new_move', {'moves' : ['left']})],
            'right': [('new_move', {'moves' : ['right']})],
            'up' : [('new_move', {'moves' : ['up']})],
            'down' : [('new_move', {'moves' : ['down']})],
            'attack' : [('new_attack', {})]
        }

        control_cmds = kwargs.get("control_cmds", default_cmds)

        try:
            assert key_profile in K_PROFILE.keys(), f'Key scheme "{key_profile}" is not defined in the config.'
            assert isinstance(control_keys, dict), f'Control keys must be passed in a form of dictionary.'
            assert isinstance(control_cmds, dict), f'Control cmds must be passed in a form of dictionary.'

            # Does control_cmds dictionary contain at least one valid command key?
            assert bool(set(default_cmds.keys()).intersection(set(control_cmds.keys()))), f'Control commands are not properly defined'

        except AssertionError:
            # Notify component factory that initiation has failed
            raise ValueError

        # Load key scheme if passed as an argument else load default scheme
        self.control_keys = K_PROFILE[key_profile]

        # If additionally specific keys are passed, override the configuration with those keys
        self.control_keys = {**self.control_keys, **control_keys}

        # Merge defaults with defined commands
        self.control_cmds = {**default_cmds, **control_cmds}

    def disable_input(self):
        ''' Backup the input commands and substitute them with none command
        '''
        self.backup_control_cmds = self.control_cmds
        self.control_cmds = {
            'left' : [('none', {})],
            'right': [('none', {})],
            'up' : [('none', {})],
            'down' : [('none', {})],
            'attack' : [('none', {})]
        }

    def restore_input(self):
        ''' Restore the input commands from backup
        '''
        self.control_cmds = self.backup_control_cmds


if __name__ == '__main__':
    import doctest
    doctest.testmod()
