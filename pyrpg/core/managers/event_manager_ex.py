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
        self._event_handlers = {}  # Stores all event handlers from quests and phases
        logger.info(f'EventManager initiated.')

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

        # Get all actions defined for given event type
        for event_handler in self._event_handlers.get(event.event_type, []):

            # Perform the event handler
            actions = event_handler.get('actions', [])

            # Execute the actions - function from ScriptManager
            self._exec_event_actions_fnc(event, actions)


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


