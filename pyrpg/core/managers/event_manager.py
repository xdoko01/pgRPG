import logging

from pyrpg.core.events.event import Event

# Create logger
logger = logging.getLogger(__name__)

class EventManager:
    '''New version that is ready to get rid of Quest as a class object and
    introduces event handlers as a dictionary property of this manager.
    '''

    def __init__(self, exec_event_actions_fnc) -> None:
        self._event_queue = []
        self._exec_event_actions_fnc = exec_event_actions_fnc
        self._event_handlers = {}  # Stores all event handlers from quests and phases. Event is a dict key and value is list of handlers
        logger.info(f'EventManager initiated.')

    def load_handler(self, handler_def: list) -> None:
        '''Reads the definition of the handler on the input and registers it to the _event_handlers dictionary.

            Example of handler_def
                    [ 
                        "QUEST_START",
                        {
                            "id": "ev_start_game",
                            "actions": 	["SCRIPT", "new.show_msg_window", {"html_text" : "Welcome to <b>%quest_id</b>.<br/>Your goal is to place all the cranes on the market spots."}]
                        }
                    ]
        '''
        event_type, handler_data = handler_def

        # Check if the event type already exists
        if self._event_handlers.get(event_type) is None:
            # If not, create new record with handler id as a key and the rest as dict
            self._event_handlers = {**self._event_handlers, **{event_type: {handler_data['id']: { k:v for (k,v) in handler_data.items() if k != 'id'}}}}
        else:
            self._event_handlers[event_type].update({handler_data['id']: { k:v for (k,v) in handler_data.items() if k != 'id'}})

        logger.info(f'Handler id {handler_data["id"]} for event "{event_type}" was added/updated.')
        logger.debug(f'Handler events dict: {self._event_handlers}')


    def delete_handler(self, handler_id: str) -> None:
        '''Deletes data for handler_id from handler storage _event_handlers'''

        # Browse all event types, dind the handler_id key and delete the record
        for event_type in self._event_handlers:
            handler = self._event_handlers[event_type].get(handler_id, None)
            if handler is not None:
                del self._event_handlers[event_type][handler_id]
                logger.info(f'Handler "{handler_id}" for event "{event_type}" successfully removed.')


    def create_event(self, type: str, params: dict) -> Event:
        '''Create an instance of new event from dictionary'''

        return Event(event_type=type, generator_obj=None, other_obj=None, params=params)

    def get_events(self) -> list:
        '''Returns event queue.'''

        return self._event_queue

    def add_event(self, event: Event) -> None:
        '''Adds new event into the event queue.'''

        self._event_queue.append(event)
        logger.debug(f'Event "{event.event_type}" added.')

    def clear_events(self) -> None:
        '''Deletes all events from the event queue.'''

        del self._event_queue[:]
        logger.info(f'All events cleared.')

    def _process_event(self, event: Event) -> None:
        '''Process particular game event by working with JSON logic statements rather than
        separate conditions and actions statements.'''

        logger.debug(f'Looking for handler for event "{event.event_type}".')

        # Get all event handlers related to the event
        event_handlers = self._event_handlers.get(event.event_type, {}).values()

        # Prepare empty list of actions to be filled in the below cycle and for execution later.
        # This is done in order to avoid modification of _event_handlers dictionary when komplex
        # actions modifying handlers dictionary happen.
        _actions_for_execution = []

        # Loop the event handlers and for each one process the action key
        for event_handler in event_handlers:
            '''Event handler action can modify the _event_handlers dictionary. For
            example load_quest action tries to clead and add items into the _event_handlers.
            One solution that will work is to iterate through the deep copy of dict.
            
            Here it is solved by adding internal list of actions that is filled and executed
            later.
            '''

            # Perform the event handler action
            actions = event_handler.get('actions', [])

            logger.info(f'Adding event {event.event_type} with action {actions} for execution')

            # Do not execute within the handlers loop but after it
            #self._exec_event_actions_fnc(event, actions)
            _actions_for_execution.append(actions)
            
        # Execute the actions - function from ScriptManager
        logger.debug(f'List of actions for execution: {_actions_for_execution}')
        for action in _actions_for_execution:

            logger.info(f'Executing event type" {event.event_type}" - {event} - action "{actions}"')
            self._exec_event_actions_fnc(event, action)


    def process_events(self, process: list(Event.EVENT_TYPES)=None, ignore: list(Event.EVENT_TYPES)=None) -> None:
        ''' Process particular game/quest event types that are specified on the input.
        '''

        # This will be filled by the events that are outstanding for processing
        new_event_queue = []

        while self._event_queue:

            # Pop out event from the beginning of the queue
            event = self._event_queue.pop(0)

            # If event is to be ignored move it to the new queue
            if ignore is not None and event.event_type in ignore:
                new_event_queue.append(event)

            # If event is not in process list
            elif process is not None and event.event_type not in process:
                new_event_queue.append(event)

            # Process the rest of the events
            else:
                self._process_event(event)

        # Renew the value of the event queue - it must be done via extend. I cannot reassigned like
        # event_queue = new_event_queue because other processors have stored link directly to original
        # global event_queue
        self._event_queue.extend(new_event_queue)


