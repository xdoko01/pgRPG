"""Manage the event queue and event handler dispatch.

Provides an event queue where processors enqueue game events each frame,
and a handler registry that maps event types to JSON-defined action handlers.
Events are processed by popping the queue and dispatching matched handlers
to the script manager for execution.

Module Globals:
    _event_queue: Deque holding pending Event instances awaiting processing.
    _exec_event_actions_fnc: Callable provided by ScriptManager to execute
        handler action trees.
    _event_handlers: Dict mapping event type strings to dicts of handler
        definitions keyed by handler id.
    _EMPTY: Empty dict sentinel used to avoid allocations in lookups.
"""

# Create logger
import logging
logger = logging.getLogger(__name__)

from collections import deque  # O(1) popleft vs O(n) list.pop(0)
from fnmatch import fnmatchcase # UNIX-like wildcards in load/clean functions

from pgrpg.core.events.event import Event

# deque instead of list: list.pop(0) shifts every remaining element — O(n) per pop,
# meaning draining k events costs O(k²). deque.popleft() is O(1) (pointer move only),
# so draining k events costs O(k). This matters every frame since collision, damage,
# and other processors enqueue events continuously.
_event_queue: deque = deque()
_exec_event_actions_fnc: callable = lambda x: None
_event_handlers: dict = {}  # Stores all event handlers from scenes and phases. Event is a dict key and value is list of handlers

_EMPTY: dict = {} # module-level sentinel for optimization

logger.info(f"EventManager started.")

def init(exec_event_actions_fnc: callable) -> None:
    """Initialize the event manager with the action execution callback.

    Args:
        exec_event_actions_fnc: Callable that executes handler action trees
            for a given event (typically ScriptManager.execute_event_actions).
    """
    global _exec_event_actions_fnc
    _exec_event_actions_fnc = exec_event_actions_fnc
    logger.info(f"EventManager initiated.")

def load_handler(handler_def: list) -> None:
    """Register an event handler definition into the handler registry.

    Args:
        handler_def: Two-element list ``[event_type, handler_data]`` where
            *event_type* is a string (e.g. ``"SCENE_START"``) and
            *handler_data* is a dict containing at least ``"id"`` and
            ``"actions"`` keys.

    Example::

        ["SCENE_START", {
            "id": "ev_start_game",
            "actions": ["SCRIPT", "show_msg_window", {"html_text": "Hello"}]
        }]
    """
    event_type, handler_data = handler_def

    # Check if the event type already exists
    global _event_handlers
    if _event_handlers.get(event_type) is None:
        # If not, create new record with handler id as a key and the rest as dict
        _event_handlers = {**_event_handlers, **{event_type: {handler_data['id']: { k:v for (k,v) in handler_data.items() if k != 'id'}}}}
    else:
        _event_handlers[event_type].update({handler_data['id']: { k:v for (k,v) in handler_data.items() if k != 'id'}})

    logger.info(f'Handler id {handler_data["id"]} for event "{event_type}" was added/updated.')
    logger.debug(f"Handler events dict: {_event_handlers}")

def delete_handler(handler_id: str) -> None:
    """Remove a handler by its id from all event types.

    Args:
        handler_id: Unique identifier of the handler to remove.
    """
    #global _event_handlers

    # Browse all event types, find the handler_id key and delete the record
    for event_type in _event_handlers:
        handler = _event_handlers[event_type].get(handler_id, None)
        if handler is not None:
            del _event_handlers[event_type][handler_id]
            logger.info(f'Handler "{handler_id}" for event "{event_type}" successfully removed.')

def delete_handlers_pattern(handler_id_pattern: str) -> None:
    """Remove all handlers whose ids match a UNIX-style wildcard pattern.

    Args:
        handler_id_pattern: Glob pattern matched via ``fnmatchcase``
            (e.g. ``"quest_*"``).
    """

    logger.debug(f'About to delete handlers with ids matching pattern "{handler_id_pattern}".')

    match = lambda k: fnmatchcase(k, handler_id_pattern)

    for event_type in _event_handlers:
        for handler_id in _event_handlers[event_type].copy().keys():
            if match(handler_id):
                delete_handler(handler_id)

def create_event(type: str, params: dict) -> Event:
    """Create a new Event instance.

    Args:
        type: Event type string (e.g. ``"COLLISION"``).
        params: Dict of event parameters passed to handlers.

    Returns:
        A new Event with the given type and params.
    """
    return Event(event_type=type, generator_obj=None, other_obj=None, params=params)

def get_events() -> list:
    """Return the current event queue.

    Returns:
        The deque of pending Event instances.
    """
    return _event_queue

def add_event(event: Event) -> None:
    """Append an event to the event queue.

    Args:
        event: Event instance to enqueue.
    """
    _event_queue.append(event)
    logger.debug(f'Event "{event.event_type}" added.')

def clear_events() -> None:
    """Remove all events from the event queue."""

    _event_queue.clear()  # deque does not support slice deletion (del deque[:])
    logger.info(f"All events cleared.")

def _process_event(event: Event) -> None:
    """Dispatch a single event to all matching handlers.

    Collects actions from every handler registered for the event's type,
    then executes them via ``_exec_event_actions_fnc``. Actions are
    collected before execution to avoid mutating the handler dict
    mid-iteration.

    Args:
        event: The Event instance to process.
    """

    logger.debug(f'Looking for handler for event "{event.event_type}".')

    # Get all event handlers related to the event
    event_handlers = _event_handlers.get(event.event_type, _EMPTY).values()

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
    logger.debug(f"List of actions for execution: {_actions_for_execution}.")
    for action in _actions_for_execution:

        logger.info(f'Executing event type" {event.event_type}" - {event} - action "{actions}"')
        _exec_event_actions_fnc(event, action)


def process_events(process: list=None, ignore: list=None) -> None:
    """Drain the event queue and dispatch each qualifying event.

    Args:
        process: If provided, only event types in this list are dispatched.
            All others are silently discarded.
        ignore: If provided, event types in this list are silently
            discarded. Checked before *process*.
    """

    # Convert filter arguments to sets once, before the loop.
    # The `in` operator on a list/tuple is O(k) — it scans every element until a
    # match is found. A set uses a hash table, so `in` is O(1) regardless of size.
    # Without this, every event in the queue pays the linear scan cost on each check.
    # Converting here (once per process_events call) is O(k) upfront; after that
    # every per-event membership test drops from O(k) to O(1).
    _ignore  = set(ignore)  if ignore  is not None else None
    _process = set(process) if process is not None else None

    while _event_queue:

        # popleft() is O(1): deque stores head/tail pointers so removing from
        # the front is a single pointer update, with no element shifting.
        event = _event_queue.popleft()

        # If event is to be ignored move it to the new queue
        if _ignore is not None and event.event_type in _ignore:
            pass

        # If event is not in process list
        elif _process is not None and event.event_type not in _process:
            pass

        # Process the rest of the events
        else:
            _process_event(event)


