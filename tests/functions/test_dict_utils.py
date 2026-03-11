import pytest

from pgrpg.functions.dict_utils import (
    get_coll_value,
    merge_dicts,
    get_dict_value,
    set_dict_value,
    del_dict_value,
    get_dict_keys_having_value,
)


def _sample_nested():
    return {
        "items": {
            "weapons": {"sword": {"weapon": [2, 3]}},
            "coins": {"golden": [10, 22, 33], "copper": [1, 2, 3]},
        }
    }


class TestGetCollValue:
    def test_basic_path(self):
        ex = {
            "entities": [
                {"id": "NPC", "components": [{"type": "A"}, {"type": "B"}]},
                {"id": "PLAYER", "components": [{"type": "C"}]},
            ]
        }
        ids = list(get_coll_value(coll=ex, path="entities/id", sep="/"))
        assert ids == ["NPC", "PLAYER"]

    def test_deeper_path(self):
        ex = {
            "entities": [
                {"id": "E1", "components": [{"params": {"health": 100}}]},
                {"id": "E2", "components": [{"params": {"health": 50}}]},
            ]
        }
        healths = list(get_coll_value(coll=ex, path="entities/components/params/health", sep="/"))
        assert healths == [100, 50]


class TestMergeDicts:
    def test_nested_override(self):
        orig = {"a": {"x": 1, "y": 2}, "b": 10}
        new = {"a": {"x": 99}, "c": 42}
        merged = merge_dicts(orig, new)
        assert merged["a"]["x"] == 99
        assert merged["a"]["y"] == 2
        assert merged["b"] == 10
        assert merged["c"] == 42

    def test_empty_new_preserves_orig(self):
        orig = {"a": 1, "b": 2}
        merged = merge_dicts(orig, {})
        assert merged == {"a": 1, "b": 2}


class TestGetDictValue:
    def test_existing_path(self):
        d = _sample_nested()
        assert get_dict_value(d, "items.weapons.sword.weapon") == [2, 3]

    def test_missing_path_returns_default(self):
        d = _sample_nested()
        assert get_dict_value(d, "items.coins.silver", not_found=[]) == []

    def test_empty_path_returns_whole_dict(self):
        d = {"key": "val"}
        assert get_dict_value(d, "") == {"key": "val"}


class TestSetDictValue:
    def test_set_existing_path(self):
        d = _sample_nested()
        set_dict_value(d, "items.coins.silver", "new_value")
        assert d["items"]["coins"]["silver"] == "new_value"

    def test_set_creates_missing_keys(self):
        d = {"a": {}}
        set_dict_value(d, "a.b.c", 42)
        assert d["a"]["b"]["c"] == 42


class TestDelDictValue:
    def test_del_nested_value(self):
        d = _sample_nested()
        del_dict_value(d, 3)
        assert 3 not in d["items"]["weapons"]["sword"]["weapon"]
        assert 3 not in d["items"]["coins"]["copper"]
        # Other values should remain
        assert 2 in d["items"]["weapons"]["sword"]["weapon"]


class TestGetDictKeysHavingValue:
    def test_find_keys_with_value(self):
        d = _sample_nested()
        results = get_dict_keys_having_value(d, 3)
        assert ["items", "weapons", "sword", "weapon"] in results
        assert ["items", "coins", "copper"] in results

    def test_find_keys_with_separator(self):
        d = _sample_nested()
        results = get_dict_keys_having_value(d, 3, sep=".")
        assert "items.weapons.sword.weapon" in results
        assert "items.coins.copper" in results
