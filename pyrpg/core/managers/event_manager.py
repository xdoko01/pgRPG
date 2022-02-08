import logging

from pyrpg.core.events.event import Event

# Create logger
logger = logging.getLogger(__name__)

class EventManager:

    def __init__(self, quests_event_handler_fnc) -> None:
        self._event_queue = []
        self._quest_event_handler_fnc = quests_event_handler_fnc
        logger.info(f'EventManager initiated.')

    def get_events(self) -> list:
        '''Returns event queue.'''

        return self._event_queue

    def add_event(self, event: Event) -> None:
        '''Adds new event into the event queue.'''

        self._event_queue.append(event)
        logger.info(f'Event "{event.event_type}"added.')

    def clear_events(self) -> None:
        '''Deletes all events from the event queue.'''

        del self._event_queue[:]
        logger.info(f'All events cleared.')

    def _process_event(self, event: Event) -> None:
        '''Process particular game event by passing it to
        quests event handlers'''

        # Send every event to every quest for handling
        self._quests_event_handler_fnc(event)

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
