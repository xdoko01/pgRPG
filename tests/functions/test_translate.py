import pytest

from pgrpg.functions.translate import translate


class TestTranslateDict:
    def test_dict_values_translated(self):
        trans = {"a": 1, "b": 2}
        result = translate(trans, {"k1": "a", "k2": "b"})
        assert result == {"k1": 1, "k2": 2}


class TestTranslateList:
    def test_list_items_translated(self):
        trans = {"x": 10, "y": 20}
        result = translate(trans, ["x", "y"])
        assert result == [10, 20]


class TestTranslateTuple:
    def test_tuple_items_translated(self):
        trans = {"x": 10, "y": 20}
        result = translate(trans, ("x", "y"))
        assert result == (10, 20)
        assert isinstance(result, tuple)


class TestTranslateString:
    def test_string_found_replaced(self):
        trans = {"hello": "world"}
        assert translate(trans, "hello") == "world"

    def test_string_not_found_returned_unchanged(self):
        trans = {"hello": "world"}
        assert translate(trans, "unknown") == "unknown"


class TestTranslatePrefix:
    def test_prefix_filtering(self):
        trans = {"name": "Alice"}
        result = translate(trans, "^name", prefix="^")
        assert result == "Alice"

    def test_no_prefix_match_returns_unchanged(self):
        trans = {"name": "Alice"}
        result = translate(trans, "name", prefix="^")
        assert result == "name"

    def test_missing_prefixed_key_raises_key_error(self):
        trans = {"name": "Alice"}
        with pytest.raises(KeyError):
            translate(trans, "^missing", prefix="^")


class TestTranslateNested:
    def test_nested_recursive_translation(self):
        trans = {"a": 1, "b": 2, "c": 3}
        value = {
            "k1": "a",
            "k2": ["b", {"inner": "c"}],
        }
        result = translate(trans, value)
        assert result == {
            "k1": 1,
            "k2": [2, {"inner": 3}],
        }
