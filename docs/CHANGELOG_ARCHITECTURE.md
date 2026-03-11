# Architecture Migration: Class-Based Managers → Module-Level Singletons

This document preserves the original class-based manager implementations that were
replaced by module-level singleton functions. The refactoring eliminated the need for
a DI container — each manager module now holds its own state at module scope, and
the engine wires them together via a `game_functions` dict passed at startup.

The class-based versions below are kept for historical reference only.

---

## `pgrpg/core/engine.py` — Old `Game` class + `run()` stub

```python
def run(key_events, key_pressed, dt, debug: bool=False) -> State:
    # Check for End Game
    for event in key_events:
        if event.type == pygame.QUIT:
            logger.info(f"Exiting the game")
            return State.EXIT_GAME_DIALOG
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                #self.gui_manager.save_screen()
                logger.info(f"Leaving to main menu")
                return State.MAIN_MENU
            elif event.key == KEYS["K_SAVE_GAME"]:
                pass
            elif event.key == KEYS["K_LOAD_GAME"]:
                pass

    # maps and scenes added in order that command can be informed about scene to change the phase
    ecs_manager.process(events=key_events, keys=key_pressed, dt=dt, debug=debug)

    return State.GAME


class Game:

    def __init__(self, gui_manager: GUIManager, sound_manager: SoundManager, timed: bool=False) -> None:

        # System resources managers
        self.gui_manager = gui_manager # for drawing anything on the screen
        self.sound_manager = sound_manager # for playing music and sounds

        # Gameplay managers
        self.map_manager = MapManager()
        self.message_manager = MessageManager()
        self.dialog_manager = DialogManager()
        self.command_manager = CommandManager()
        self.ecs_manager = ECSManager()
        self.script_manager = ScriptManager(alias_to_entity_dict_fnc=self.ecs_manager.get_alias_to_entity_dict)
        self.pathfind_manager = PathfindManager()

        self.event_manager = EventManager(self.script_manager.execute_event_actions)

        self.ecs_manager.initialize(timed=timed, game_functions={
            "window" : self.gui_manager.window,
            "create_entity_fnc" : self.ecs_manager.create_entity,
            "remove_entity_fnc" : self.ecs_manager.delete_entity,
            "maps" : self.map_manager._maps,
            "teleport_event_queue" : self.event_manager.add_event,
            "weapon_event_queue" : self.event_manager.add_event,
            "ammo_pack_event_queue" : self.event_manager.add_event,
            "wearable_event_queue" : self.event_manager.add_event,
            "item_pickup_event_queue" : self.event_manager.add_event,
            "entity_coll_event_queue" : self.event_manager.add_event,
            "game_event_handler" : self.event_manager.process_events,
            "game_messages" : self.message_manager.get_messages,
            "add_message" : self.message_manager.add_message,
            "damage_event_queue" : self.event_manager.add_event,
            "destroy_event_queue" : self.event_manager.add_event,
            "score_event_queue" : self.event_manager.add_event,
            "FNC_GET_MAP": self.map_manager.get_map,
            "FNC_ADD_COMMAND" : self.command_manager.add_command,
            "FNC_CLEAR_COMMANDS" : self.command_manager.clear_command_queue,
            "FNC_GET_COMMANDS" : self.command_manager.get_command_queue,
            "FNC_PROCESS_COMMANDS" : self.command_manager.process_commands,
            "FNC_EXEC_CMD_INIT" : self.command_manager.execute_command_init,
            "FNC_EXEC_CMD" : self.command_manager.execute_command,
            "FNC_CALC_PATHS": self.pathfind_manager.continue_pathfinding,
            "FNC_REQUEST_PATHFIND": self.pathfind_manager.request_path,
            "FNC_GET_PATH": self.pathfind_manager.get_path,
            "FNC_ADD_EVENT" : self.event_manager.add_event,
            "add_event_fnc" : self.event_manager.add_event,
            "clear_events_fnc" : self.event_manager.clear_events,
            "get_events_fnc" : self.event_manager.get_events,
            "FNC_GET_ENTITY_ID" : self.ecs_manager.get_entity_id,
            "REF_ECS_MNG": self.ecs_manager,
            "FNC_PLAY_SOUND" : self.sound_manager.play_sound
        })

        self._scenes = {}

        self.load_scene_def_fncs = [
            ["prereqs", self.load_scene_from_file],
            ["cleanup/processors", self.ecs_manager.delete_processor],
            ["cleanup/maps", self.map_manager.delete_map],
            ["cleanup/templates", self.ecs_manager.delete_template],
            ["cleanup/entities", self.ecs_manager.delete_entity],
            ["cleanup/dialogs", self.dialog_manager.delete_dialog],
            ["cleanup/handlers", self.event_manager.delete_handler],
            ["processors", self.ecs_manager.load_processor],
            ["maps", self.map_manager.load_map],
            ["dialogs", self.dialog_manager.load_dialog],
            ["templates", self.ecs_manager.load_template],
            ["entities", self.ecs_manager.load_register_empty_entity],
            ["entities", self.ecs_manager.load_update_empty_entity],
            ["entities/components/params/handlers", self.event_manager.load_handler],
            ["handlers", self.event_manager.load_handler]
        ]

        logger.info(f"Game initiated")

    def load_scene_from_file(self, filepath: str) -> Scene:
        scene_def = get_dict_from_file(filepath=Path(filepath), dir=SCENE_PATH)
        scene = self.load_scene_from_def(scene_def)
        scene.filepath = filepath
        return scene

    def load_scene_from_def(self, scene_def: dict) -> Scene:
        scene = Scene(alias=scene_def["id"], scene_def=scene_def)
        logger.info(f"Loading objects for scene {scene.alias} has started.")
        for data_path, process_fnc in self.load_scene_def_fncs:
            data_to_process = get_coll_value(coll=scene_def, path=data_path, sep="/")
            logger.info(f'Start of processing of "{data_path}" for scene "{scene.alias}".')
            with ProgressBar2(gui_manager=self.gui_manager, header="Loading", text=data_path) as progress:
                for item in progress(data_to_process):
                    logger.debug(f'About to process following item "{item}" using function "{process_fnc}".')
                    process_fnc(item)
            logger.info(f'End of processing of "{data_path}" for scene "{scene.alias}".')
        logger.info(f'Loading objects for scene "{scene.alias}" has finished.')
        return scene

    def new_game(self, filepath: str, clear_before_load: bool=True, show_progress: bool=True) -> None:
        logger.debug(f'Loading scene "{filepath}".')
        if clear_before_load: self._clear_game()
        scene = self.load_scene_from_file(filepath=filepath)
        self._scenes[scene.alias] = scene
        self.event_manager.add_event(
            Event("SCENE_START", self, None, params={
                "filepath": scene.filepath, "id": scene.id, "alias": scene.alias,
                "title": scene.title, "description": scene.description,
                "objective": scene.objective, "stats": scene.stats
            })
        )
        logger.info(f'Scene "{filepath}" successfully loaded.')

    def _clear_game(self) -> None:
        self.map_manager.clear_maps()
        self.dialog_manager.clear_dialogs()
        self.message_manager.clear_messages()
        self.command_manager.clear_command_queue()
        self.event_manager.clear_events()
        self.ecs_manager.clear_ecs()
        self.script_manager.clear_scripts()
        self.clear_scenes()
        logger.info(f"All game resources cleared.")

    def delete_scene(self, scene_name: str) -> None:
        del self._scenes[scene_name]
        logger.info(f'Scene "{scene_name}" was deleted.')

    def clear_scenes(self) -> None:
        for scene_name in self._scenes.copy().keys():
            self.delete_scene(scene_name)
        logger.info(f"Quests cleared.")

    def exit_game(self) -> None:
        self._clear_game()

    def run(self, key_events, key_pressed, dt, debug: bool=False) -> State:
        for event in key_events:
            if event.type == pygame.QUIT:
                logger.info(f"Exiting the game")
                return State.EXIT_GAME_DIALOG
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    logger.info(f"Leaving to main menu")
                    return State.MAIN_MENU
                elif event.key == KEYS["K_SAVE_GAME"]:
                    pass
                elif event.key == KEYS["K_LOAD_GAME"]:
                    pass
        self.ecs_manager.process(events=key_events, keys=key_pressed, dt=dt, debug=debug)
        return State.GAME
```

---

## `pgrpg/core/managers/ecs_manager.py` — Old `ECSManager` class

The full class-based `ECSManager` mirrored the current module-level functions but used
`self._world`, `self._alias_to_entity`, etc. as instance attributes instead of module globals.
(~520 lines of class code, omitted for brevity — see git history for the full version.)

---

## `pgrpg/core/managers/event_manager.py` — Old `EventManager` class

```python
class EventManager:
    '''New version that is ready to get rid of Scene as a class object and
    introduces event handlers as a dictionary property of this manager.
    '''

    def __init__(self, exec_event_actions_fnc) -> None:
        self._event_queue = []
        self._exec_event_actions_fnc = exec_event_actions_fnc
        self._event_handlers = {}
        logger.info(f'EventManager initiated.')

    def load_handler(self, handler_def: list) -> None:
        event_type, handler_data = handler_def
        if self._event_handlers.get(event_type) is None:
            self._event_handlers = {**self._event_handlers, **{event_type: {handler_data['id']: { k:v for (k,v) in handler_data.items() if k != 'id'}}}}
        else:
            self._event_handlers[event_type].update({handler_data['id']: { k:v for (k,v) in handler_data.items() if k != 'id'}})

    def delete_handler(self, handler_id: str) -> None:
        for event_type in self._event_handlers:
            handler = self._event_handlers[event_type].get(handler_id, None)
            if handler is not None:
                del self._event_handlers[event_type][handler_id]

    def create_event(self, type: str, params: dict) -> Event:
        return Event(event_type=type, generator_obj=None, other_obj=None, params=params)

    def get_events(self) -> list:
        return self._event_queue

    def add_event(self, event: Event) -> None:
        self._event_queue.append(event)

    def clear_events(self) -> None:
        del self._event_queue[:]

    def _process_event(self, event: Event) -> None:
        event_handlers = self._event_handlers.get(event.event_type, {}).values()
        _actions_for_execution = []
        for event_handler in event_handlers:
            actions = event_handler.get('actions', [])
            _actions_for_execution.append(actions)
        for action in _actions_for_execution:
            self._exec_event_actions_fnc(event, action)

    def process_events(self, process=None, ignore=None) -> None:
        new_event_queue = []
        while self._event_queue:
            event = self._event_queue.pop(0)
            if ignore is not None and event.event_type in ignore:
                new_event_queue.append(event)
            elif process is not None and event.event_type not in process:
                new_event_queue.append(event)
            else:
                self._process_event(event)
        self._event_queue.extend(new_event_queue)
```

---

## `pgrpg/core/managers/command_manager.py` — Old `CommandManager` class

The full class-based `CommandManager` mirrored the current module-level functions.
(~180 lines, see git history for the full version.)

---

## `pgrpg/core/managers/script_manager.py` — Old `ScriptManager` class

```python
class ScriptManager:
    '''Newly, script manager evaluates json logic and actions + holds the reference to translation
    of ECS manager.'''

    def __init__(self, alias_to_entity_dict_fnc) -> None:
        self._scripts = {}
        self._alias_to_entity_dict_fnc = alias_to_entity_dict_fnc

    def register_script(self, fnc, alias) -> None:
        self._scripts.update({alias: fnc})

    def execute_event_actions(self, event: Event, actions):
        translated_actions = translate(self._alias_to_entity_dict_fnc(), actions)
        json_logic(
            expr=translated_actions,
            value_fnc=lambda x: x,
            script_fnc=lambda *args: self.execute_script(args[0], event, **args[1]),
            data=event.params
        )

    def execute_script(self, script_module_name: str, *script_args, **script_kwargs):
        script_fnc = self._scripts.get(script_module_name, None)
        if not script_fnc:
            script_module_path_absolute = f"{MODULEPATHS['SCRIPT_MODULE_PATH']}.{script_module_name}"
            try:
                script_module = import_module(script_module_path_absolute)
            except ValueError:
                raise ValueError(f'Error during loading of script module "{script_module_path_absolute}".')
            try:
                script_module.initialize(self.register_script, script_module_name)
            except ValueError:
                raise ValueError(f'Error during initiating/registering of script module "{script_module_path_absolute}".')
            script_fnc = self._scripts.get(script_module_name)
        return script_fnc(*script_args, **script_kwargs)

    def clear_scripts(self) -> None:
        self._scripts.clear()
```

---

## `pgrpg/core/managers/map_manager.py` — Old `MapManager` class

```python
class MapManager:

    def __init__(self) -> None:
        self._maps = {}

    def get_map(self, map_name) -> Map:
        return self._maps.get(map_name, None)

    def load_map(self, map_def: str) -> None:
        if not self._maps.get(map_def, None):
            self._maps.update({map_def : Map(map_def)})

    def delete_map(self, map_name: str) -> None:
        if self._maps.get(map_name, None):
            del self._maps[map_name]

    def clear_maps(self) -> None:
        maps = list(self._maps.keys()).copy()
        for map_name in maps:
            self.delete_map(map_name)
```

---

## `pgrpg/core/managers/dialog_manager.py` — Old `DialogManager` class

```python
class DialogManager():

    def __init__(self) -> None:
        self._dialogs = {}

    def load_dialog(self, dialog_def: dict) -> None:
        # Same logic as module-level version but using self._dialogs
        # and direct path constants (DIALOG_PATH, IMAGE_PATH, FONT_PATH)
        ...

    def delete_dialog(self, dialog_name: str) -> None:
        if self._dialogs.get(dialog_name, None):
            del self._dialogs[dialog_name]

    def clear_dialogs(self) -> None:
        dialogs = list(self._dialogs.keys()).copy()
        for dialog_name in dialogs:
            self.delete_dialog(dialog_name)
```

---

## `pgrpg/core/managers/pathfind_manager.py` — Old `PathfindManager` class

```python
class PathfindManager:
    '''Manages requests for path calculations and returns the resulting path once it is ready.'''

    def __init__(self):
        self._req_queue = []
        self._req_lookup = dict()
        self._next_req_id = 0

    def request_path(self, graph, start, goal, search='BFS'):
        path_req = PathfindRequest(graph=graph, start=start, goal=goal, option=PathfindOption[search])
        req_id = self._next_req_id
        self._next_req_id += 1
        self._req_lookup.update({req_id: path_req})
        self._req_queue.append(path_req)
        return req_id

    def continue_pathfinding(self, max_steps=None):
        if len(self._req_queue) == 0: return
        max_steps_per_calc = max_steps // len(self._req_queue) if max_steps is not None else None
        for path_req in self._req_queue.copy():
            finished, path = path_req.search.proceed(no_of_steps=max_steps_per_calc)
            if finished:
                self._req_queue.remove(path_req)

    def get_path(self, req_id):
        path_req = self._req_lookup.get(req_id, None)
        if path_req is None: return None
        if not path_req.search.finished: return None
        self._req_lookup.pop(req_id)
        if path_req.options.value.checkpoints: path_req.search.filter_checkpoints()
        if path_req.options.value.start: path_req.search.include_start()
        return path_req.search.get_path_result()
```

---

## `pgrpg/core/config/states.py` — Old hardcoded state graph

```python
STATES_GRAPH = {
    State.START_PROGRAM    : [State.MAIN_MENU,  State.GAME],
    State.MAIN_MENU        : [State.LOAD_QUEST_MENU, State.EXIT_GAME_DIALOG, State.CONSOLE],
    State.LOAD_QUEST_MENU  : [State.MAIN_MENU, State.GAME, State.CONSOLE],
    State.GAME             : [State.MAIN_MENU, State.PAUSE_GAME, State.CONSOLE, State.EXIT_GAME_DIALOG],
    State.PAUSE_GAME       : [State.GAME, State.CONSOLE],
    State.CONSOLE          : [State.MAIN_MENU, State.LOAD_QUEST_MENU, State.GAME],
    State.EXIT_GAME_DIALOG : [State.END_PROGRAM, State.GAME, State.MAIN_MENU],
    State.END_PROGRAM      : []
}

NON_GAME_STATES = [State.CONSOLE, State.START_PROGRAM, State.END_PROGRAM]

START_STATE = State.START_PROGRAM
```

---

## `pgrpg/core/commands/__init__.py` — Old frozen `Command` dataclass

```python
@dataclass(frozen=True)
class Command:
    name: str
    params: dict
```

Replaced by `Command = namedtuple('Command', ['name', 'params', 'entity_id'])`.

---

## `pgrpg/functions/str_utils.py` — Old `parse_fnc_str_obsolete`

```python
def parse_fnc_str_obsolete(for_parse: str) -> tuple:
    '''Parses function call defined as a string into
    function name and list of parameters.'''

    start_pos = None
    end_pos = None
    args = ''

    for pos, c in enumerate(for_parse):
        if c == '(':
            start_pos = pos
        elif c == ')':
            end_pos = pos
            args = for_parse[start_pos+1:end_pos]
            break

    vars = []
    for v in args.split(","):
        v = v.strip()
        if len(v) == 0: continue
        v = int(v) if v.isdigit() else v
        vars.append(v)

    return (for_parse[:start_pos], vars)
```

Replaced by `parse_fnc_str()` and `parse_fnc_list()`.
