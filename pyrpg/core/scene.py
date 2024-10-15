
class Scene:
    def __init__(self, alias: str, scene_def: dict) -> None:
        self.filepath: str = None
        self.id, self.alias = alias, alias
        self.title = scene_def.get("title")
        self.description = scene_def.get("description")
        self.objective = scene_def.get("objective")
        self.stats = {
            "no_of_prereqs": len(scene_def.get("prereqs", [])),
            "no_of_procs": len(scene_def.get("processors", [])),
            "no_of_maps": len(scene_def.get("maps", [])),
            "no_of_dlgs": len(scene_def.get("dialogs", [])),
            "no_of_temps": len(scene_def.get("templates", [])),
            "no_of_ents": len(scene_def.get("entities", [])),
            "no_of_handlers": len(scene_def.get("handlers", [])),
            "no_of_comps": {e.get("id"): len(e.get("components", [])) for e in scene_def.get("entities", [])}
        }
