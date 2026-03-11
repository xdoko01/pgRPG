import pytest

from pgrpg.functions.get_dict_params import get_dict_params


STORAGE = {
    "t_tile_pos": {
        "id": "t_tile_pos",
        "vars": ["$tileX=0", "$tileY=0", "$map"],
        "components": [
            {
                "type": "position:Position",
                "params": {"tile_x": "$tileX", "tile_y": "$tileY", "map": "$map"},
            }
        ],
    }
}


class TestDefaults:
    def test_defaults_used_when_arg_missing(self):
        result = get_dict_params(
            definition=["t_tile_pos", {"$map": "arena"}],
            storage=STORAGE,
        )
        params = result["components"][0]["params"]
        assert params["tile_x"] == 0
        assert params["tile_y"] == 0
        assert params["map"] == "arena"


class TestKwargOverride:
    def test_kwarg_overrides_positional(self):
        result = get_dict_params(
            definition=["t_tile_pos", [9, 8, "arena"], {"$tileX": 5, "$tileY": 2}],
            storage=STORAGE,
        )
        params = result["components"][0]["params"]
        assert params["tile_x"] == 5
        assert params["tile_y"] == 2


class TestListDefinition:
    def test_list_definition_format(self):
        result = get_dict_params(
            definition=["t_tile_pos", [5, 2, "arena"]],
            storage=STORAGE,
        )
        params = result["components"][0]["params"]
        assert params["tile_x"] == 5
        assert params["tile_y"] == 2
        assert params["map"] == "arena"


class TestStringDefinition:
    def test_string_definition_format(self):
        result = get_dict_params(
            definition="t_tile_pos(5, 5, test_arena_sand)",
            storage=STORAGE,
        )
        params = result["components"][0]["params"]
        assert params["tile_x"] == 5
        assert params["tile_y"] == 5
        assert params["map"] == "test_arena_sand"
