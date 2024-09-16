import logging

from importlib import import_module

from pyrpg.core.events.event import Event
from pyrpg.core.config.modulepaths import MODULEPATHS # for SCRIPT_MODULE_PATH - Path to the modules containing scripts
from pyrpg.functions import translate, json_logic

# Create logger
logger = logging.getLogger(__name__)

class ScriptManager:
    '''Newly, script manager evaluates json logic and actions + holds the reference to translation
    of ECS manager.'''

    ''' Script Manager holds the dictionary of script names and real references to the modules

        register script function ... that registers script module in 
        the dictionary of all scripts that is also kept on level of script manager

        on request for load of the script first check if exists in dictionary
            if yes return the function
            if not try to get it from script str and if suceeded call the register function with script_manager reference
                that will register the script with the script manager
    '''

    def __init__(self, alias_to_entity_dict_fnc) -> None:
        '''Initiate ScriptManager'''
        # Dictionary having script path/name as key and script module refs as value
        self._scripts = {}
        self._alias_to_entity_dict_fnc = alias_to_entity_dict_fnc
        logger.info(f'ScriptManager created.')

    def register_script(self, fnc, alias) -> None:
        '''Register new script with the ScriptManager under some specific name.
        It is called from script module initialize function.
        '''
        self._scripts.update({alias: fnc})
        logger.info(f'Script function name: {alias} registered at ScriptManager.')

    def execute_event_actions(self, event: Event, actions):
        '''Translates expression using the ECSmanager alias_to_entity dictionary
        and executes the script
        '''

        # Translate entity names for entity IDs before processing of the action
        translated_actions = translate(self._alias_to_entity_dict_fnc(), actions)
        
        logger.debug(f'Using following translation dictionary for translation of aliases in action definition {self._alias_to_entity_dict_fnc()}')
        logger.info(f'Executing actions {translated_actions} for event {event}')

        # Run the actions
        json_logic(
            expr=translated_actions, 
            value_fnc=lambda x: x, 
            script_fnc=lambda *args: self.execute_script(args[0], event, **args[1]), 
            data=event.params
        )

    def execute_script(self, script_module_name: str, *script_args, **script_kwargs):
        '''Runs the script function with given arguments.'''

        # Check if script module is already registered
        script_fnc = self._scripts.get(script_module_name, None)

        # Register the script
        if not script_fnc:

            script_module_path_absolute = MODULEPATHS["SCRIPT_MODULE_PATH"] + script_module_name

            # Try to find the script module and get its reference
            try:
                script_module = import_module(script_module_path_absolute)
            except ValueError:
                logger.error(f'Error during loading of script module "{script_module_path_absolute}".')
                raise ValueError(f'Error during loading of script module "{script_module_path_absolute}".')

            # Try to register the script
            try:
                script_module.initialize(self.register_script, script_module_name)
            except ValueError:
                logger.error(f'Error during initiating/registering of script "{script_module_path_absolute}".')
                raise ValueError(f'Error during initiating/registering of script module "{script_module_path_absolute}".')

            # Get the script function
            script_fnc = self._scripts.get(script_module_name)
        
        # Run the script
        return script_fnc(*script_args, **script_kwargs)


    def clear_scripts(self) -> None:
        ''' Clear all the scripts'''
        self._scripts.clear()
        logger.info(f'Scripts were cleared.')

